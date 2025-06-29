from Crypto.Cipher import AES
from binascii import unhexlify

MOD64 = 2**64 - 59
outputs = [
    7434459989309917390,
    13764883950722179945,
    6491039561529571699,
    13576977941708037180
]
ciphertext = unhexlify("5c285fcff21cadb30a6ec92d445e5d75898f83fc31ff395cb43fb8be319d464895cf9aed809c20f92eb6f79f6bd36fc8d3091725b54c889a22850179ec26f89c")

def find_lcg_params(outputs, max_k=40):
    lifted = [[y + k * MOD64 for k in range(max_k)] for y in outputs]
    for x0 in lifted[0]:
        for x1 in lifted[1]:
            for x2 in lifted[2]:
                for x3 in lifted[3]:
                    try:
                        den = x1 - x0
                        if den == 0:
                            continue
                        a = (x2 - x1) / den
                        if a != int(a): continue
                        a = int(a)
                        c = x1 - a * x0
                        m = a * x2 + c - x3
                        if m <= 0: continue
                        x1_check = (a * x0 + c) % m
                        x2_check = (a * x1_check + c) % m
                        x3_check = (a * x2_check + c) % m
                        if (int(x1_check) % MOD64 == outputs[1] and
                            int(x2_check) % MOD64 == outputs[2] and
                            int(x3_check) % MOD64 == outputs[3]):
                            return a, c, m, x0
                    except:
                        continue
    return None, None, None, None

a, c, m, x0 = find_lcg_params(outputs)

if a:
    print(f"[+] Found LCG params:\na = {a}\nc = {c}\nm = {m}")
    x1 = (a * x0 + c) % m
    key = int(x0) % MOD64
    key2 = int(x1) % MOD64
    key_bytes = key.to_bytes(8, 'big') + key2.to_bytes(8, 'big')
    print(f"[+] AES key = {key_bytes.hex()}")

    cipher = AES.new(key_bytes, AES.MODE_ECB)
    flag = cipher.decrypt(ciphertext)
    print("[+] Flag:", flag.strip())
else:
    print("[-] Failed to recover LCG parameters.")

