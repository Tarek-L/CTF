from Crypto.Util.number import inverse, long_to_bytes
from math import gcd
import hashlib

# Given parameters
N = 15259097618051614944787283201589661884102249046616617256551480013493757323043057001133186203348289474506700039004930848402024292749905563056243342761253435345816868449755336453407731146923196889610809491263200406510991293039335293922238906575279513387821338778400627499247445875657691237123480841964214842823837627909211018434713132509495011638024236950770898539782783100892213299968842119162995568246332594379413334064200048625302908007017119275389226217690052712216992320294529086400612432370014378344799040883185774674160252898485975444900325929903357977580734114234840431642981854150872126659027766615908376730393
e = 65537
c = 6820410793279074698184582789817653270130724082616000242491680434155953264066785246638433152548701097104342512841159863108848825283569511618965315125022079145973783083887057935295021036668795627456282794393398690975486485865242636068814436388602152569008950258223165626016102975011626088643114257324163026095853419397075140539144105058615243349994512495476754237666344974066561982636000283731809741806084909326748565899503330745696805094211629412690046965596957064965140083265525186046896681441692279075201572766504836062294500730288025016825377342799012299214883484810385513662108351683772695197185326845529252411353

# Load dumps
def load_dump(file_path):
    with open(file_path, "r") as f:
        lines = f.read().splitlines()
    F_hex = lines[0]
    F_bytes = bytes.fromhex(F_hex)
    sigmas = [int(x, 16) for x in lines[1:] if x.strip() != "0" and len(x.strip()) > 2]
    return F_bytes, sigmas

F1, sigmas1 = load_dump("dump1.txt")
F2, sigmas2 = load_dump("dump2.txt")

# Sanity check: the first line in both dumps should be the same F
assert F1 == F2
F_bytes = F1

mus = sigmas1 + sigmas2  # Combine all mus from both dumps

print(f"Loaded {len(mus)} total mus from both dumps.")

# Step 1: Try to find a nontrivial GCD using the mus
print("[*] Trying to factor N using GCD(mu^2 - theta, N)...")

def gen_theta_J(N, idx, F_bytes):
    attempt = 0
    while True:
        h = hashlib.sha256()
        h.update(b'J')
        h.update(N.to_bytes((N.bit_length() + 7) // 8, 'big'))
        h.update(idx.to_bytes(4, 'big'))
        h.update(F_bytes)
        h.update(attempt.to_bytes(4, 'big'))
        candidate = int.from_bytes(h.digest(), 'big') % N
        if 1 < candidate < N and gcd(candidate, N) == 1:
            a = jacobi(candidate, N)
            if a == 1:
                return candidate
        attempt += 1

def jacobi(a, n):
    a %= n
    result = 1
    while a != 0:
        while a % 2 == 0:
            a //= 2
            if n % 8 in [3, 5]:
                result = -result
        a, n = n, a
        if a % 4 == 3 and n % 4 == 3:
            result = -result
        a %= n
    return result if n == 1 else 0

# Use only non-zero mus
m1 = 35
threshold = (3 * len(mus)) // 8
nonzero_mus = [m for m in mus if m != 0]

print(f"[*] Total non-zero mus: {len(nonzero_mus)}")
assert len(nonzero_mus) >= threshold

for j, mu in enumerate(nonzero_mus):
    idx = m1 + j + 1
    theta = gen_theta_J(N, idx, F_bytes)
    residue = pow(mu, 2, N)
    if residue != theta:
        d = gcd(residue - theta, N)
        if 1 < d < N:
            p = d
            q = N // d
            print(f"[+] Successfully factored N:")
            print(f"p = {p}")
            print(f"q = {q}")
            break
else:
    print("[-] Failed to factor N using mus.")
    exit(1)

# Step 2: Decrypt
phi = (p - 1) * (q - 1)
d = inverse(e, phi)
m = pow(c, d, N)
plaintext = long_to_bytes(m)
print(f"[+] Decrypted message: {plaintext}")

