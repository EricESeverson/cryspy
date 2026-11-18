import base64
import secrets

from .ciphers import Cipher
from .encoders import Encoder


def bits_to_blocks(bits: str, block_size: int) -> list[int]:
    """Cut a bit string into blocks of block_size bits. No padding.

    Args:
        bits: a string of 0s and 1s whose length is a multiple of block_size.
        block_size: the number of bits in a block.

    Returns:
        One int < 2**block_size per block.
    """
    if len(bits) % block_size:
        raise ValueError("len(bits) is not a multiple of block_size")
    # the int(..., 2) means reading off in base 2
    return [int(bits[k:k + block_size], 2)
            for k in range(0, len(bits), block_size)]


def blocks_to_bits(ints: list[int], block_size: int) -> str:
    """Join blocks of block_size bits back into a bit string. No padding.

    Args:
        ints: one int < 2**block_size per block.
        block_size: the number of bits in a block.

    Returns:
        The bit string, block_size bits per block.
    """
    return "".join(f"{num:0{block_size}b}" for num in ints)


def bytes_to_bits(data: bytes) -> str:
    """Write bytes as a bit string, 8 bits per byte."""
    return "".join(f"{byte:08b}" for byte in data)


def bits_to_bytes(bits: str) -> bytes:
    """Read a bit string, 8 bits per byte, back into bytes."""
    # the 8s here are for grouping 8 bits into a byte
    return bytes(int(bits[k:k + 8], 2) for k in range(0, len(bits), 8))


def random_bit_string(n: int) -> str:
    """n random bits, as a string of 0s and 1s."""
    return f"{secrets.randbits(n):0{n}b}" if n else ""


class Blocker:
    """Cuts data into blocks for a cipher, and does all the padding.

    Each block is random_bits random bits (the high bits), then
    block_size - random_bits message bits. Random bits are never
    revealed: they are thrown away on deblock, so the same message bits
    encrypt differently each time (the known plaintext patch).
    The last block's message bits are filled out with random padding bits;
    their count goes first in the block list.

    Args:
        block_size: the number of bits in a block.
        random_bits: the number of random bits at the top of each block.
    """
    def __init__(self, block_size: int, random_bits: int = 0) -> None:
        if not 0 <= random_bits < block_size:
            raise ValueError("need 0 <= random_bits < block_size")
        self.block_size = block_size
        self.random_bits = random_bits
        # the message bits in each block
        self.message_bits = block_size - random_bits

    def block_bits(self, bits: str) -> list[int]:
        """Cut a bit string into blocks, adding random bits and padding.

        Args:
            bits: a string of 0s and 1s.

        Returns:
            The number of padding bits, then one int < 2**block_size per block.
        """
        padding_len = (-len(bits)) % self.message_bits
        # random padding bits, not zeros: zeros would be known plaintext
        bits += random_bit_string(padding_len)
        blocks = bits_to_blocks(bits, self.message_bits)
        # random bits go on top: encode adds them
        blocks = [(secrets.randbits(self.random_bits) << self.message_bits) | num
                  for num in blocks]
        return [padding_len] + blocks

    def deblock_bits(self, ints: list[int]) -> str:
        """Undo block_bits: drop the random bits and the padding.

        Args:
            ints: the number of padding bits, then the blocks.

        Returns:
            The original bit string.
        """
        padding_len, *blocks = ints
        # decode throws the random bits away
        mask = (1 << self.message_bits) - 1
        bits = blocks_to_bits([num & mask for num in blocks], self.message_bits)
        return bits[:len(bits) - padding_len]

    def block(self, data: bytes) -> list[int]:
        """Cut bytes into blocks of block_size bits.

        Args:
            data: the bytes to cut up.

        Returns:
            The number of padding bits, then one int < 2**block_size per block.
        """
        return self.block_bits(bytes_to_bits(data))

    def deblock(self, ints: list[int]) -> bytes:
        """Join blocks of block_size bits back into bytes.

        Args:
            ints: the number of padding bits, then the blocks, as from block.

        Returns:
            The original bytes.
        """
        return bits_to_bytes(self.deblock_bits(ints))


def to_text(data: bytes, text_format: str) -> str:
    """TODO"""
    if text_format == "hex":
        return data.hex()
    if text_format == "base64":
        return base64.b64encode(data).decode("ascii")
    raise ValueError("text_format must be 'hex' or 'base64'")


def from_text(text: str, text_format: str) -> bytes:
    """TODO"""
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
        cipher: encrypts one block at a time; it must have at least
            2**block_size messages.
        text_format: "hex" or "base64", the text that send returns.
        random_bits: the number of random bits at the top of each block
            (see Blocker).
    """

    def __init__(self, encoder: Encoder, block_size: int, cipher: Cipher,
                 text_format: str = "hex", random_bits: int = 0) -> None:
        self.encoder = encoder
        self.blocker = Blocker(block_size, random_bits)
        # len() fails on a range this big, but `in` is instant
        if 2 ** block_size - 1 not in cipher.messages:
            raise ValueError("cipher has fewer than 2^block_size messages")
        self.cipher = cipher
        self.text_format = text_format
        # every ciphertext int is less than mod, so it fits in this many bytes
        self.bytes_per_block = ((cipher.mod - 1).bit_length() + 7) // 8

    def encrypt(self, message: str, key) -> list[int]:
        """TODO"""
        padding_len, *blocks = self.blocker.block(self.encoder.encode(message))
        # the padding count goes out unencrypted: it is one of only
        # block_size values, so encrypting it gives away a plaintext block
        return [padding_len] + [self.cipher.encrypt(num, key) for num in blocks]

    def decrypt(self, ints: list[int], key) -> str:
        """TODO"""
        padding_len, *blocks = ints
        decrypted = [self.cipher.decrypt(num, key) for num in blocks]
        return self.encoder.decode(self.blocker.deblock([padding_len] + decrypted))

    def send(self, message: str, key) -> str:
        """TODO"""
        ints = self.encrypt(message, key)
        data = b"".join(num.to_bytes(self.bytes_per_block, "big") for num in ints)
        return to_text(data, self.text_format)

    def receive(self, text: str, key) -> str:
        """TODO"""
        data = from_text(text, self.text_format)
        n = self.bytes_per_block
        ints = [int.from_bytes(data[k:k + n], "big") for k in range(0, len(data), n)]
        return self.decrypt(ints, key)
