from random import randint
from math import gcd
from functools import reduce


def recover_n(x, fx_list):
    """
    Given a fixed x and multiple outputs f(x), recover modulus n.
    Each f(x) is a randomized square root of x modulo n.
    """
    diffs = [f**2 - x for f in fx_list]
    return reduce(gcd, diffs)


x = randint(2, 2**1024)

print(x)
l = []
for i in range(10):
    t = int(input("enter t = "))
    l.append(t)
n = recover_n(x, l)
print(n)
