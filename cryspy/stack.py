import base64

from .ciphers import Cipher
from .encoders import Encoder


def bits_to_blocks(bits: str, block_size: int) -> list[int]:
    padding_len = (-len(bits)) % block_size
    bits += "0" * padding_len
    # the int(..., 2) means reading off in base 2
    blocks = [int(bits[k:k + block_size], 2)
              for k in range(0, len(bits), block_size)]
    return [padding_len] + blocks


def blocks_to_bits(ints: list[int], block_size: int) -> str:
    padding_len = ints[0]
    bits = "".join(f"{num:0{block_size}b}" for num in ints[1:])
    return bits[:len(bits) - padding_len]


class Blocker:
    def __init__(self, block_size: int) -> None:
        self.block_size = block_size

    def block(self, data: bytes) -> list[int]:
        """Cut bytes into blocks of block_size bits.

        Args:
            data: the bytes to cut up.

        Returns:
            The number of padding bits, then one int < 2**block_size per block.
        """
        bits = "".join(f"{byte:08b}" for byte in data)
        return bits_to_blocks(bits, self.block_size)

    def deblock(self, ints: list[int]) -> bytes:
        """Join blocks of block_size bits back into bytes.

        Args:
            ints: the number of padding bits, then the blocks, as from block.

        Returns:
            The original bytes.
        """
        bits = blocks_to_bits(ints, self.block_size)
        # the 8s here are for grouping 8 bits into a byte
        return bytes(int(bits[k:k + 8], 2) for k in range(0, len(bits), 8))


def to_text(data: bytes, text_format: str) -> str:
    if text_format == "hex":
        return data.hex()
    if text_format == "base64":
        return base64.b64encode(data).decode("ascii")
    raise ValueError("text_format must be 'hex' or 'base64'")


def from_text(text: str, text_format: str) -> bytes:
    if text_format == "hex":
        return bytes.fromhex(text)
    if text_format == "base64":
        return base64.b64decode(text)
    raise ValueError("text_format must be 'hex' or 'base64'")


class CryptoStack:
    """Encode, block, cipher OR decipher, deblock, decode.

    Args:
        encoder: turns a message into bytes and back.
        block_size: the number of bits in a block.
        cipher: encrypts one block at a time; its mod must be at least
            2**block_size.
        text_format: "hex" or "base64", the text that send returns.
    """

    def __init__(self, encoder: Encoder, block_size: int, cipher: Cipher,
                 text_format: str = "hex") -> None:
        self.encoder = encoder
        self.blocker = Blocker(block_size)
        if 2 ** block_size > cipher.mod:
            raise ValueError("Ur special! Cipher mod less than 2^block_size")
        self.cipher = cipher
        self.text_format = text_format
        # every ciphertext int is less than mod, so it fits in this many bytes
        self.bytes_per_block = ((cipher.mod - 1).bit_length() + 7) // 8

    def encrypt(self, message: str, key) -> list[int]:
        blocks = self.blocker.block(self.encoder.encode(message))
        return [self.cipher.encrypt(num, key) for num in blocks]

    def decrypt(self, ints: list[int], key) -> str:
        decrypted = [self.cipher.decrypt(num, key) for num in ints]
        return self.encoder.decode(self.blocker.deblock(decrypted))

    def send(self, message: str, key) -> str:
        ints = self.encrypt(message, key)
        data = b"".join(num.to_bytes(self.bytes_per_block, "big") for num in ints)
        return to_text(data, self.text_format)

    def receive(self, text: str, key) -> str:
        data = from_text(text, self.text_format)
        n = self.bytes_per_block
        ints = [int.from_bytes(data[k:k + n], "big") for k in range(0, len(data), n)]
        return self.decrypt(ints, key)
