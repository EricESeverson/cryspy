# 1.3.A Group 2
import cryspy as cp

def exp(a, b, m):
    '''
    returns a ** b mod m
    '''
    a_raised_to_power_of_two = a % m
    res = 1
    for i in range(0, b.bit_length()):
        if (b >> i & 1 == 1):
            res = res * a_raised_to_power_of_two % m
        # calculate a ** (2 ** i)
        a_raised_to_power_of_two = a_raised_to_power_of_two ** 2 % m
    return res
