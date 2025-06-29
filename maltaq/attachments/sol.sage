# Lean & fast SageMath script for full flag recovery (k0 + k1)
from sage.all import *

# --- Constants ---
h1 = 1825310437373651425737133387514704339138752170433274546111276309
h3 = 42423271339336624024407863370989392004524790041279794366407913985192411875865
p = 2**255 - 19
FLAG_LEN = 45
k0_bytes = FLAG_LEN//2 + 4
k1_bytes = FLAG_LEN - k0_bytes
PREFIX = b"maltactf{"

# --- k0 Recovery ---
a, b, c, d = 1401, 2, -2048, 1273
G = matrix(ZZ, [[a, b], [c, d]])
tr, det = a + d, a*d - b*c
lam = (tr + sqrt(tr^2 - 4*det)) / 2
alpha = log(lam, 2)
beta = log(a / lam, 2) + 1
n_est = floor((h1 - beta) / alpha)

for offset in range(-500, 501):
    k0 = n_est + offset
    try:
        if (G^k0)[0,0].nbits() == h1:
            part = Integer(k0).to_bytes(k0_bytes, 'big')
            if part.startswith(PREFIX):
                first = part.decode('ascii')
                break
    except:
        continue
else:
    raise ValueError("k0 not found")

# --- k1 Recovery ---
Fp = GF(p)
tr1 = Fp(tr)
det1 = Fp(det)
inv_b = Fp(b).inverse()
target = Fp(h3) * inv_b

# Recurrence: u_n = tr1*u_{n-1} - det1*u_{n-2}
B = 1 << 16
u = [Fp(0), Fp(1)]
baby = {u[0]: 0, u[1]: 1}
for j in range(2, B):
    nxt = tr1*u[1] - det1*u[0]
    baby[nxt] = j
    u = [u[1], nxt]

C = companion_matrix([det1, -tr1])
CB = C^B
vec = vector(Fp, [1, 0])
for i in range(B+1):
    if vec[0] in baby:
        k1 = i*B + baby[vec[0]]
        break
    vec = CB * vec
else:
    raise ValueError("k1 not found")

suffix = Integer(k1).to_bytes(k1_bytes, 'big').decode('ascii', 'replace')
print("\nFull flag:", first + suffix)

