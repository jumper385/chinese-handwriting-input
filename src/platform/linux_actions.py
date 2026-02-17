import os
import re
import shutil
import subprocess
import time

from src.platform.actions import PlatformActions


class LinuxActions(PlatformActions):
    def __init__(self):
        self.this_pid = os.getpid()
        self._last_target_app = None
        self._last_target_window_id = None

    def _run(self, args):
        result = subprocess.run(args, capture_output=True, text=True, check=False)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

    def _has_command(self, command):
        return shutil.which(command) is not None

    def _required_tools_ok(self):
        return self._has_command("xdotool") and self._has_command("xprop")

    def _clipboard_set(self, text):
        if self._has_command("xclip"):
            result = subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0

        if self._has_command("xsel"):
            result = subprocess.run(
                ["xsel", "--clipboard", "--input"],
                input=text,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0

        return False

    def _clipboard_get(self):
        if self._has_command("xclip"):
            ok, out, _err = self._run(["xclip", "-selection", "clipboard", "-o"])
            return out if ok else ""

        if self._has_command("xsel"):
            ok, out, _err = self._run(["xsel", "--clipboard", "--output"])
            return out if ok else ""

        return ""

    def _window_pid(self, window_id):
        ok, out, _err = self._run(["xdotool", "getwindowpid", window_id])
        if not ok or not out:
            return None
        try:
            return int(out)
        except ValueError:
            return None

    def _window_name(self, window_id):
        ok, out, _err = self._run(["xdotool", "getwindowname", window_id])
        if not ok:
            return None
        return out or None

    def _stacked_windows_top_down(self):
        ok, out, _err = self._run(["xprop", "-root", "_NET_CLIENT_LIST_STACKING"])
        if not ok or "#" not in out:
            return []

        hex_ids = re.findall(r"0x[0-9a-fA-F]+", out)
        if not hex_ids:
            return []

        dec_ids = [str(int(item, 16)) for item in hex_ids]
        dec_ids.reverse()
        return dec_ids

    def _find_last_external_window(self):
        for window_id in self._stacked_windows_top_down():
            pid = self._window_pid(window_id)
            if pid is None:
                continue
            if pid == self.this_pid:
                continue
            return window_id
        return None

    @property
    def last_target_app(self):
        return self._last_target_app

    def update_last_target_app(self):
        if not self._required_tools_ok():
            return

        window_id = self._find_last_external_window()
        if not window_id:
            return

        self._last_target_window_id = window_id
        window_name = self._window_name(window_id)
        if window_name:
            self._last_target_app = window_name

    def insert_text_and_return(self, text: str):
        if not self._required_tools_ok():
            return False, "Linux 需要 xdotool 和 xprop，请先安装。"

        if not (self._has_command("xclip") or self._has_command("xsel")):
            return False, "缺少 Linux 剪贴板工具，请安装 xclip 或 xsel。"

        if not self._last_target_window_id:
            return False, "无法确定外部窗口，请先聚焦目标应用一次后重试。"

        ok_source, source_window_id, _err = self._run(["xdotool", "getactivewindow"])
        source_window_id = source_window_id if ok_source and source_window_id else None

        previous_clipboard = self._clipboard_get()
        if not self._clipboard_set(text):
            return False, "设置系统剪贴板失败。"

        ok_activate, _out, _err = self._run(
            ["xdotool", "windowactivate", "--sync", self._last_target_window_id]
        )
        if not ok_activate:
            self._clipboard_set(previous_clipboard)
            return False, "无法激活目标应用进行输入。"

        time.sleep(0.08)
        ok_paste, _out, _err = self._run(["xdotool", "key", "--clearmodifiers", "ctrl+v"])

        time.sleep(0.12)
        self._clipboard_set(previous_clipboard)

        if source_window_id:
            self._run(["xdotool", "windowactivate", "--sync", source_window_id])

        if not ok_paste:
            return False, "粘贴失败，请检查桌面自动化权限后重试。"

        target_name = self._last_target_app or "目标窗口"
        return True, f"已输入：{text} -> {target_name}"

    def _send_key_and_return(self, key_name: str, success_text: str):
        if not self._required_tools_ok():
            return False, "Linux 需要 xdotool 和 xprop，请先安装。"

        if not self._last_target_window_id:
            return False, "无法确定外部窗口，请先聚焦目标应用一次后重试。"

        ok_source, source_window_id, _err = self._run(["xdotool", "getactivewindow"])
        source_window_id = source_window_id if ok_source and source_window_id else None

        ok_activate, _out, _err = self._run(
            ["xdotool", "windowactivate", "--sync", self._last_target_window_id]
        )
        if not ok_activate:
            return False, "无法激活目标应用进行按键操作。"

        time.sleep(0.08)
        ok_key, _out, _err = self._run(["xdotool", "key", "--clearmodifiers", key_name])

        time.sleep(0.08)
        if source_window_id:
            self._run(["xdotool", "windowactivate", "--sync", source_window_id])

        if not ok_key:
            return False, "按键发送失败，请检查桌面自动化权限后重试。"

        target_name = self._last_target_app or "目标窗口"
        return True, f"{success_text} -> {target_name}"

    def backspace_and_return(self):
        return self._send_key_and_return("BackSpace", "已执行退格")

    def newline_and_return(self):
        return self._send_key_and_return("Return", "已换行")