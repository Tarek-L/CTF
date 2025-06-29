from pwn import *
from Crypto.Util.number import long_to_bytes

flag = bytes.fromhex(
    "73626960647f6b206821204f21254f7d694f7624662065622127234f726927756d"
)

for i in range(256):
    b = long_to_bytes(i)
    res = xor(flag, b)
    res = res.decode("utf-8", errors="ignore")
    if res[:6] == "crypto":
        print(res)
        break
