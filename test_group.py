class Shift:
    def __init__(self, mod):
        self.mod = mod

    def encrypt(self, x, key):
        return (x + key) % self.mod

    def decrypt(self, x, key):
        return (x - key) % self.mod
