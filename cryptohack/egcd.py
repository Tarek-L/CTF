from math import gcd


def extended_euclid(a, b):
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r != 0:
        quotient = old_r // r

        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t

    # Now old_r is gcd, old_s = u, old_t = v
    return old_r, old_s, old_t


# Input
a = int(input("Enter a: "))
b = int(input("Enter b: "))

g, u, v = extended_euclid(a, b)

print(f"gcd({a}, {b}) = {g}")
print(f"Solution: {u}*{a} + {v}*{b} = {g}")
