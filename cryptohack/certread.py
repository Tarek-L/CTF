from Crypto.PublicKey import RSA

with open(
    "/home/fkey/ctf/cryptohack/bruce_rsa_6e7ecd53b443a97013397b1a1ea30e14.pub",
    "br",
) as f:
    data = f.read()

k = RSA.import_key(data)

print(int(k.n))
