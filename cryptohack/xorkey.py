from pwn import xor


flag = bytes.fromhex(
    "0e0b213f26041e480b26217f27342e175d0e070a3c5b103e2526217f27342e175d0e077e263451150104"
)
plain = b"crypto{"
key = xor(flag[: len(plain)], plain) + xor(flag[-1], b"}")
print(key)

res = xor(flag, key)

print(flag)
print(res.decode())
