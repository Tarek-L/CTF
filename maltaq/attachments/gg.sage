# SageMath script to recover k1 via Jordan-block analysis (corrected suffix extraction)
from sage.all import GF, Integer

# ---- Parameters ----
p = 2**255 - 19
h2 = Integer(6525529513224929513242286153522039835677193513612437958976590021494532059727)
h3 = Integer(42423271339336624024407863370989392004524790041279794366407913985192411875865)
FLAG_LEN = 45
# k1 occupies the second half of the flag: total minus (first half+4)
k1_bytes = FLAG_LEN - ((FLAG_LEN // 2) + 4)  # 19 bytes

# ---- Build field and compute eigenvalue (Jordan block) ----
Fp = GF(p)
tr = Fp(1401 + 1273)
lam = tr * Fp(2).inverse()  # eigenvalue λ = tr/2 in Fp

# ---- Direct recovery of n mod p ----n = (Fp(h3) * lam)/(2*(Fp(h2) - 32*h3))
A = Fp(h2) - Fp(32)*Fp(h3)       # = λ^n
n_mod_p = (Fp(h3)*lam) * Fp(2).inverse() * A.inverse()
print(f"Raw n mod p = {n_mod_p}")

# ---- Reduce to the true k1 < 256^k1_bytes ----
# k1 fits in k1_bytes bytes, so we take it mod 256^k1_bytes
modulus = 1 << (8 * k1_bytes)
k1_int = int(n_mod_p) % modulus
print(f"Recovered k1 (truncated) = {k1_int}")

# ---- Extract and print flag suffix ----
suffix = k1_int.to_bytes(k1_bytes, "big")
try:
    print("Flag suffix:", suffix.decode('ascii'))
except:
    print("Raw suffix bytes:", suffix)

