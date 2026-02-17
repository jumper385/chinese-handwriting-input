import os
import subprocess
import time

from src.platform.actions import PlatformActions


class MacOSActions(PlatformActions):
    def __init__(self):
        self.this_pid = os.getpid()
        self._excluded_app_names = {"Python", "python", "Python3", "python3"}
        self._last_target_app = None

    @property
    def last_target_app(self):
        return self._last_target_app

    def _run_osascript(self, script):
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

    def _frontmost_app(self):
        script = 'tell application "System Events" to get name of first process whose frontmost is true'
        ok, stdout, _stderr = self._run_osascript(script)
        if not ok:
            return None
        return stdout

    def update_last_target_app(self):
        frontmost = self._frontmost_app()
        if frontmost and frontmost not in self._excluded_app_names:
            self._last_target_app = frontmost

    def _get_system_clipboard_text(self):
        result = subprocess.run(
            ["pbpaste"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        return result.stdout

    def _set_system_clipboard_text(self, text):
        result = subprocess.run(
            ["pbcopy"],
            input=text,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0

    def _reactivate_handwriting_window(self):
        script = (
            'tell application "System Events" to set frontmost of '
            f'(first process whose unix id is {self.this_pid}) to true'
        )
        self._run_osascript(script)

    def insert_text_and_return(self, text: str):
        if not self._last_target_app:
            return False, "Could not determine external app. Focus target app once, then retry."

        previous_clipboard = self._get_system_clipboard_text()
        if not self._set_system_clipboard_text(text):
            return False, "Failed to set system clipboard."

        app_name = self._last_target_app.replace('"', '\\"')
        activate_script = f'tell application "{app_name}" to activate'
        ok_activate, _stdout, _stderr = self._run_osascript(activate_script)
        if not ok_activate:
            return False, "Could not activate target app for insertion."

        time.sleep(0.1)
        paste_script = 'tell application "System Events" to keystroke "v" using command down'
        ok_paste, _stdout, _stderr = self._run_osascript(paste_script)

        time.sleep(0.2)
        self._set_system_clipboard_text(previous_clipboard)
        self._reactivate_handwriting_window()

        if not ok_paste:
            return False, "Paste failed. Enable Accessibility for Terminal/Python and retry."

        return True, f"Inserted: {text} -> {self._last_target_app}"