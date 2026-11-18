from abc import ABC, abstractmethod


class Encoder(ABC):
    """TODO"""
    @abstractmethod
    def encode(self, message: str) -> bytes:
        """TODO"""
        ...

    @abstractmethod
    def decode(self, data: bytes) -> str:
        """TODO"""
        ...


class TextEncoder(Encoder):
    """TODO"""
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def encode(self, message: str) -> bytes:
        """TODO"""
        return message.encode(self.encoding)

    def decode(self, data: bytes) -> str:
        """TODO"""
        return data.decode(self.encoding)
