from abc import ABC, abstractmethod
from typing import Optional, Tuple


class PlatformActions(ABC):
    @abstractmethod
    def update_last_target_app(self) -> None:
        pass

    @abstractmethod
    def insert_text_and_return(self, text: str) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def backspace_and_return(self) -> Tuple[bool, str]:
        pass

    @abstractmethod
    def newline_and_return(self) -> Tuple[bool, str]:
        pass

    @property
    @abstractmethod
    def last_target_app(self) -> Optional[str]:
        pass