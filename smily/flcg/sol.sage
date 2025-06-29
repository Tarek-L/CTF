from Crypto.Cipher import AES
from binascii import unhexlify

# Known values from out.txt
outputs = [
    7434459989309917390,
    13764883950722179945,
    6491039561529571699,
    13576977941708037180
]

ciphertext_hex = "5c285fcff21cadb30a6ec92d445e5d75898f83fc31ff395cb43fb8be319d464895cf9aed809c20f92eb6f79f6bd36fc8d3091725b54c889a22850179ec26f89c"
ciphertext = unhexlify(ciphertext_hex)

MOD64 = 2^64 - 59
max_k = 10  # how many lifted candidates to try

# Generate lifted candidates for internal state
lifted_states = []
for y in outputs:
    lifted_states.append([y + k * MOD64 for k in range(max_k)])

# Try all combinations of lifted states
for x0 in lifted_states[0]:
    for x1 in lifted_states[1]:
        for x2 in lifted_states[2]:
            for x3 in lifted_states[3]:
                try:
                    a = (x2 - x1) / (x1 - x0)
                    c = x1 - a * x0
                    # m can be computed using x3 = (a * x2 + c) % m ⇒ m = a*x2 + c - x3
                    m_candidate = (a * x2 + c) - x3
                    if not m_candidate.is_integer():
                        continue
                    m = Integer(m_candidate)
                    if m <= 0 or not is_prime(m):
                        continue


                    # Validate the recurrence
                    def fwd(x): return (a * x + c) % m
                    test = [int(fwd(x0)) % MOD64 == outputs[1],
                            int(fwd(fwd(x0))) % MOD64 == outputs[2],
                            int(fwd(fwd(fwd(x0)))) % MOD64 == outputs[3]]
                    if all(test):
                        print(f"[+] Found LCG params:\na = {int(a)}\nc = {int(c)}\nm = {int(m)}")

                        # Recover key = get_blocks(2) = first two outputs
                        k1 = int(x0) % MOD64
                        k2 = int(fwd(x0)) % MOD64
                        key = k1.to_bytes(8, 'big') + k2.to_bytes(8, 'big')
                        print(f"[+] AES Key = {key.hex()}")

                        # Decrypt
                        cipher = AES.new(key, AES.MODE_ECB)
                        flag = cipher.decrypt(ciphertext)
                        print("[+] Flag:", flag.strip())
                        quit()
                except ZeroDivisionError:
                    continue

print("[-] No valid parameters found.")

