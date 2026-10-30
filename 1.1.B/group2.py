

class Encoder:
    def __init__(self, encoding="utf-8"):
        self.encoding = encoding

    def encode(self, s):
        return s.encode(self.encoding)

    def decode(self, b):
        return b.decode(self.encoding)



class Blocker:
    def __init__(self,block_size):
        self.b = block_size
        self.M = 2 ** self.b

    def block(self, byts):
        """bytes object --> list of ints"""
        # padding goes at the back, and the very last int tells how much padding there is
        bits = "".join(f"{byte:08b}" for byte in byts)
        padding_len = (-len(bits)) % self.b
        bits += "0" * padding_len
        # the int(..., 2) means reading off in base 2
        blocks = [int(bits[i:i + self.b], 2) for i in range(0, len(bits), self.b)]
        return blocks + [padding_len]


    def deblock(self, ints):
        """list of ints --> bytes object"""
        # reads last int as ammount of padding
        padding_len = ints[-1]
        bits = "".join(f"{n:0{self.b}b}" for n in ints[:-1])

        if (padding_len != 0):
            bits = bits[:-padding_len]
        #the 8s here are for grouping 8 bits into a byte in order to write as byte object
        return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


class Cipher():
    def __init__(self):
        pass
    def encrypt(self, letter, key):
        pass
    def decrypt(self, letter, key):
        pass

class AdditionCipher(Cipher):
    def __init__(self, mod):
        self.mod = mod

    def encrypt(self, letter, key):
        return (letter+key) % self.mod

    def decrypt(self, letter, key):
        return (letter-key) % self.mod


class CryptoStack:
    """encode, block, cipher OR decipher, deblock, decode"""

    def __init__(self, encoder, block_size, cipher): #change this to make it take in a cipher class and optionally a mod and of no mod then default to 2**block_size.
        self.blocker = Blocker(block_size)
        if self.blocker.M > cipher.mod:
            raise ValueError("Ur special! Cipher mod less than 2^block_size")
        self.encoder = encoder
        
        self.cipher = cipher

    def encrypt(self, s, key):

        blocked = self.blocker.block(self.encoder.encode(s))

        return [self.cipher.encrypt(a,key) for a in blocked]


    def decrypt(self, ints, key):

        decrypted = [self.cipher.decrypt(a,key) for a in ints]

        return self.encoder.decode(self.blocker.deblock(decrypted))





