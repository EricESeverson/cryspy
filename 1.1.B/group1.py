from typing import Callable

# tentative: how to store alphabet, strings
# * could do if time - adjust block size for length of alphabet

class Encoder:
  def __init__(self, alphabet):
    "@param `alphabet` - an interable object of the alphabet"
    self.alphabet = alphabet
  

  def encode(self, txt: str) -> bytes:
    """
    @param `txt` - string (for now Python primitive string)
    
    @return python's unicode encoding of a string
    """
    return txt.encode()


  def decode(self, binary: bytes) -> str:
    """
    @param binary - bytes to be decoded
    
    @return unicode decoding of each byte
    """
    return binary.decode()

#------------------------------#

class Cipher:
  def encrypt(self, num, key, **kwargs) -> list[int]:
    "Encrypts a singular number"
    pass

  def decrypt(self, num, key, **kwargs) -> list[int]:
    "Decrypts a singular number"
    pass

  def get_block_size(self, key) -> int | None:
    """Returns the block size if the cipher requires
    a particular block size.
    Default val of 8 otherwise."""
    return 8

class Caesar(Cipher):
  def encrypt(self, num: int, key):
    return (num + key)
  
  def decrypt(self, num: int, key):
    return (num - key)

class Vigenere(Caesar):
  def get_block_size(self, key):
    return 8*len(key)

#------------------------------#

class CryptoStack:

  def __init__(self, encoder: Encoder, cipher: Cipher):
    self.encoder = encoder
    self.cipher = cipher
    self.block_size = None # will be set later
  
  def make_msg(self, msg, key):
    """
    temporary name description

    @param `msg` -
    @param `key` -

    @return -
    """

    self.block_size = self.cipher.get_block_size(key)
    binary = self.encoder.encode(msg)
    partitioned = self.partition(binary, self.block_size)
    enc = self.encrypt(partitioned, key)
    connected = self.connect(enc, self.block_size)
    return self.encoder.decode(connected)

  def receive_msg(self, msg, key):
    """
    temporary name description

    @param `encoder` -
    @param `cipher` -
    @param `msg` -
    @param `key` -

    @return -
    """

    self.block_size = self.cipher.get_block_size(key)
    binary = self.encoder.encode(msg)
    partitioned = self.partition(binary, self.block_size)
    enc = self.decrypt(partitioned, key)
    connected = self.connect(enc, self.block_size)
    return self.encoder.decode(connected)

  def partition(self, binary: bytes, block_size: int) -> list[int]:
    """
    description

    @param `binary` - from encode
    @param `block_size` - the number of bits in a block

    @return - list of the bytes conv to int with bit size `block_size`
            The first item in the list is the amount of padded 0s in the last block.
            
            This number will be preserved throughout encryption and decryption
    """

    bits = "".join([format(bit, f'0{block_size}b') for bit in binary]) 

    r = len(bits) % block_size # remainder
    plus = block_size-r if r != 0 else r
    bits += "0"*plus

    blocks = [bits[i:i+block_size] for i in range(0, len(bits), block_size)]
    return [plus] + [int(block, 2) for block in blocks]

  def connect(self, blocks: list[int], block_size: int) -> bytes:
    """
    description

    @param `blocks` - a list of integers to be turned to bytes
                    The first item in the list is the amount of 
                    
                    padded 0s in the last block
    @param `block_size` - the number of bits in a block

    @return - bytes 
    """

    bit_blocks = [format(block, f'0{block_size}b') for block in blocks[1:]]
    bit_str = "".join(bit_blocks)
    bit_str = bit_str[:-blocks[0]] if blocks[0] > 0 else bit_str

    return bytes( # from chatgpt
      int(bit_str[i:i+8], 2)
      for i in range(0, len(bit_str), 8)
    )  

  def encrypt(self, partitioned: list[int], key, **kwargs) -> list[int]:
    """
    @param `partitioned` - ints to be encrypted
    @param `cipher` - cipher
    @param `key` - arbitrary type. Will be fed into `cipher`
    @param `**kwargs` - `cipher`'s arguments

    @return partitioned ints encrypted with the key.
            The first item in the list is preserved
    """
    return [partitioned[0]]+[self.cipher.encrypt(i, key, **kwargs) for i in partitioned[1:]]

  def decrypt(self, encrypted: list[int], key, **kwargs) -> list[int]:
    """
    @param `encrypted` - list of encrypted ints
    @param `cipiher` - cipher
    @param `key` - arbitrary type. Will be fed into `cipher`
    @param `**kwargs` - `cipher`'s arguments

    @return encrypted ints decrypted with the key
            The first item in the list is preserved
    """

    return [encrypted[0]]+[self.cipher.decrypt(i, key, **kwargs) for i in encrypted[1:]]