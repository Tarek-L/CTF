from PIL import Image
from pwn import xor


flag = Image.open(
    "/home/fkey/ctf/cryptohack/flag_7ae18c704272532658c10b5faad06d74.png"
).convert("RGB")
lemur = Image.open(
    "/home/fkey/ctf/cryptohack/lemur_ed66878c338e662d3473f0d98eedbd0d.png"
).convert("RGB")

width, height = flag.size

flag = flag.tobytes()
lemur = lemur.tobytes()

res = xor(flag, lemur)


res = Image.frombytes("RGB", (width, height), res)

res.show()
