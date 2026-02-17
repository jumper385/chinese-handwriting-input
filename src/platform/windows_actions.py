from src.platform.actions import PlatformActions


class WindowsActions(PlatformActions):
    def __init__(self):
        self._last_target_app = None

    @property
    def last_target_app(self):
        return self._last_target_app

    def update_last_target_app(self):
        return None

    def insert_text_and_return(self, text: str):
        return False, "Windows 平台操作暂未实现。"

    def backspace_and_return(self):
        return False, "Windows 平台操作暂未实现。"

    def newline_and_return(self):
        return False, "Windows 平台操作暂未实现。"