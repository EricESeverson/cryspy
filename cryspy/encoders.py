from abc import ABC, abstractmethod


class Encoder(ABC):
    @abstractmethod
    def encode(self, message: str) -> bytes:
        ...

    @abstractmethod
    def decode(self, data: bytes) -> str:
        ...


class TextEncoder(Encoder):
    def __init__(self, encoding: str = "utf-8") -> None:
        self.encoding = encoding

    def encode(self, message: str) -> bytes:
        return message.encode(self.encoding)

    def decode(self, data: bytes) -> str:
        return data.decode(self.encoding)
