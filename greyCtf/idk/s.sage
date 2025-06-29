# Clean SageMath script to recover RSA private key and decrypt ciphertext using (rho, sigma) proof data

from hashlib import sha256
import re

# RSA public key
N = 15259097618051614944787283201589661884102249046616617256551480013493757323043057001133186203348289474506700039004930848402024292749905563056243342761253435345816868449755336453407731146923196889610809491263200406510991293039335293922238906575279513387821338778400627499247445875657691237123480841964214842823837627909211018434713132509495011638024236950770898539782783100892213299968842119162995568246332594379413334064200048625302908007017119275389226217690052712216992320294529086400612432370014378344799040883185774674160252898485975444900325929903357977580734114234840431642981854150872126659027766615908376730393
e = 65537
c = 6820410793279074698184582789817653270130724082616000242491680434155953264066785246638433152548701097104342512841159863108848825283569511618965315125022079145973783083887057935295021036668795627456282794393398690975486485865242636068814436388602152569008950258223165626016102975011626088643114257324163026095853419397075140539144105058615243349994512495476754237666344974066561982636000283731809741806084909326748565899503330745696805094211629412690046965596957064965140083265525186046896681441692279075201572766504836062294500730288025016825377342799012299214883484810385513662108351683772695197185326845529252411353

# Load sigmas from file
def load_sigmas(filename):
    lines = [line.strip() for line in open(filename) if line.strip()]
    F_hex = lines[0]
    sigmas = []
    for line in lines[1:]:
        if line in ["0", "OK"]:
            break
        try:
            sigmas.append(int(line, 16))
        except:
            break
    return F_hex, sigmas

# Load from dump1.txt and dump2.txt
F1, sigmas1 = load_sigmas("dump1.txt")
F2, sigmas2 = load_sigmas("dump2.txt")
assert F1 == F2, "Different F values in dumps!"
sigmas = sigmas1 + sigmas2

# Deterministic generation of rho values
def gen_rho(N, idx):
    attempt = 0
    while True:
        h = sha256()
        h.update(b'Z')
        h.update(N.to_bytes((N.nbits() + 7) // 8, byteorder='big'))
        h.update(idx.to_bytes(4, 'big'))
        h.update(attempt.to_bytes(4, 'big'))
        candidate = int.from_bytes(h.digest(), 'big') % N
        if 1 < candidate < N and gcd(candidate, N) == 1:
            return candidate
        attempt += 1

# Construct (rho, sigma) pairs
pairs = []
for i in range(min(30, len(sigmas))):
    rho_i = gen_rho(N, i + 1)
    sigma_i = sigmas[i]
    pairs.append((rho_i, sigma_i))

print(f"[*] Loaded {len(pairs)} (rho, sigma) pairs.")

# Attempt to guess d using a simple linear system (inexact, for short d only)
# Try to find d such that sigma = rho^d mod N
found_d = None
for rho, sigma in pairs:
    try:
        d = discrete_log(Mod(sigma, N), Mod(rho, N))
        found_d = d
        print("[+] Found d using discrete_log:", d)
        break
    except:
        continue

if found_d is None:
    print("[-] Could not recover d (try lattice attack next).")
    quit()

# Decrypt ciphertext
m = power_mod(c, found_d, N)
msg = m.to_bytes((m.nbits() + 7) // 8, byteorder="big")

try:
    text = msg.decode()
except:
    text = msg.decode(errors="ignore")

print("[*] Decrypted preview:", text[:100])
flag = re.findall(r'grey\{.*?\}', text)
if flag:
    print("[🎉] FLAG:", flag[0])
else:
    print("[-] Flag not found.")

