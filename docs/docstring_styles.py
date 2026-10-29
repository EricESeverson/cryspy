"""Docstring styles: one function, several ways to document it."""


# ---------------------------------------------------------------------------
# From the 1.1.B group files, verbatim
# ---------------------------------------------------------------------------

# Group 1, 1.1.B/group1.py
def partition(self, binary: bytes, block_size: int) -> list[int]:
    """
    description

    @param `binary` - from encode
    @param `block_size` - the number of bits in a block

    @return - list of the bytes conv to int with bit size `block_size`
            The first item in the list is the amount of padded 0s in the last block.

            This number will be preserved throughout encryption and decryption
    """


# Group 2, 1.1.B/group2.py
def block(self, byts):
    """bytes object --> list of ints"""


# Group 3, 1.1.B/group3.py
def LZ77_decode(lst):
    """Decompressed lst using LZ77. LZ77_decode(LZ77_encode(b)) is b.
    O(len(b))"""


# ---------------------------------------------------------------------------
# Python's standard styles, all on the same function
# ---------------------------------------------------------------------------

# PEP 257
def block(self, data: bytes) -> list[int]:
    """Cut bytes into blocks of block_size bits.

    The first int is the number of padding bits added at the end.
    """


# Google style
def block(self, data: bytes) -> list[int]:
    """Cut bytes into blocks of block_size bits.

    Args:
        data: the bytes to cut up.

    Returns:
        The number of padding bits, then one int < 2**block_size per block.
    """


# NumPy style
def block(self, data: bytes) -> list[int]:
    """Cut bytes into blocks of block_size bits.

    Parameters
    ----------
    data : bytes
        The bytes to cut up.

    Returns
    -------
    list[int]
        The number of padding bits, then one int < 2**block_size per block.
    """


# reST / Sphinx
def block(self, data: bytes) -> list[int]:
    """Cut bytes into blocks of block_size bits.

    :param data: the bytes to cut up.
    :return: the number of padding bits, then one int < 2**block_size per block.
    """


# ---------------------------------------------------------------------------
# Where a docstring shows up
# ---------------------------------------------------------------------------
# help(block)          prints it
# block.__doc__        is it, as a string
# hovering in VS Code or Colab shows it
