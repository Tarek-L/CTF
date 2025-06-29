from pwn import *
from random import randint
from math import gcd
from functools import reduce
from itertools import combinations

context.log_level = "info"

HOST, PORT = "smiley.cat", 46177


def recover_n(x, fx_list):
    diffs = [abs(f**2 - x) for f in fx_list if f**2 != x]
    return reduce(gcd, diffs)


def recover_factors_from_fx_with_n(n, fx_list):
    for a, b in combinations(fx_list, 2):
        g = gcd(abs(a - b), n)
        if 1 < g < n:
            p, q = g, n // g
            return min(p, q), max(p, q)
    return None


def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("modular inverse does not exist")
    return x % m


def main():
    io = remote(HOST, PORT)

    # Step 1: Send smart x = r^2 so it's always a square
    r = randint(2, 2**512)
    x = r * r
    log.info(f"Using x = {x}")

    fx_list = []
    NUM_SAMPLES = 12
    for _ in range(NUM_SAMPLES):
        io.sendlineafter(b">>>", str(x).encode())
        line = io.recvline().strip()
        try:
            fx = int(line.strip().split()[-1])
            fx_list.append(fx)
            log.info(f"f({x}) = {fx}")
        except:
            log.warning(f"Failed to parse line: {line}")

    # Step 2: Send non-integer to trigger m print
    io.sendlineafter(b">>>", b"notanumber")
    line = io.recvline().strip()
    try:
        m = int(line.strip().split(b"=")[-1])
        log.success(f"Got m = {m}")
    except:
        log.error(f"Failed to parse m: {line}")
        io.close()
        return

    # Step 3: Recover n
    n = recover_n(x, fx_list)
    log.success(f"Recovered n = {n}")

    # Step 4: Recover p, q
    result = recover_factors_from_fx_with_n(n, fx_list)
    if not result:
        log.error("Failed to factor n")
        io.close()
        return
    p, q = result
    log.success(f"Recovered p = {p}")
    log.success(f"Recovered q = {q}")

    # Step 5: Forge signature s = m^d mod n
    e = 0x10001
    phi = (p - 1) * (q - 1)
    d = modinv(e, phi)
    s = pow(m, d, n)
    log.success(f"Forged signature s = {s}")

    # Step 6: Send forged signature (same connection!)
    io.sendlineafter(b">>>", str(s).encode())

    # Step 7: Receive flag or failure
    try:
        result = io.recvall(timeout=3).decode()
        log.success("Server response:")
        print(result)
    except EOFError:
        log.warning("Connection closed early")


if __name__ == "__main__":
    main()
