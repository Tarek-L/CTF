# SageMath script to recover k0 from noisy bit length leak
from sage.all import matrix, ZZ, log, floor, sqrt, Integer

# Step 1: Define known values
G = matrix(ZZ, [[1401, 2], [-2048, 1273]])
h1 = Integer("1825310437373651425737133387514704339138752170433274546111276309")

# Step 2: Estimate the size of k0
FLAG_LEN = 45  # Length of full flag
K0_BYTES = (FLAG_LEN // 2) + 4  # = 26
PREFIX = b"maltactf{"  # Known prefix to match

# Step 3: Spectral analysis of G to find growth rate
tr = G[0,0] + G[1,1]
det = G.det()
disc = tr^2 - 4*det
lam1 = (tr + sqrt(disc)) / 2

alpha = log(lam1, 2)
A1 = G[0,0]  # G^1[0][0]
C = A1 / lam1
beta = log(C, 2) + 1

# Step 4: Invert to get estimate for k0
n_real = (h1 - beta) / alpha
n_est = floor(n_real)

# Step 5: Brute force a small window around the estimate
window = 100  # Search window
print("Estimated k0 near:", n_est)

for k in range(n_est - window, n_est + window + 1):
    try:
        b = Integer(k).to_bytes(K0_BYTES, 'big')
    except OverflowError:
        continue
    if b.startswith(PREFIX):
        print("Found potential k0:")
        print("k0 =", k)
        print("bytes =", b)
        print("ascii =", b.decode(errors='replace'))
        break
else:
    print("No match found in the search window.")

