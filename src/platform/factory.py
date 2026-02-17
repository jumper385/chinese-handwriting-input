import sys

from src.platform.linux_actions import LinuxActions
from src.platform.macos_actions import MacOSActions
from src.platform.windows_actions import WindowsActions


def create_platform_actions():
    if sys.platform == "darwin":
        return MacOSActions()
    if sys.platform.startswith("linux"):
        return LinuxActions()
    if sys.platform in ("win32", "cygwin"):
        return WindowsActions()
    return LinuxActions()