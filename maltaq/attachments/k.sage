# Spectral-based brute-force recovery of k0
from sage.all import matrix, ZZ, log, floor, sqrt, Integer
import time

# Constants and matrix
FLAG_LEN = 45
K0_BYTES = (FLAG_LEN // 2) + 4  # 26
PREFIX = b"maltactf{"
G = matrix(ZZ, [[1401, 2], [-2048, 1273]])
h1 = Integer("1825310437373651425737133387514704339138752170433274546111276309")

# Estimate k0 via eigenvalue analysis
tr = G[0, 0] + G[1, 1]
det = G.det()
disc = tr^2 - 4*det
lam1 = (tr + sqrt(disc)) / 2

alpha = log(lam1, 2)
A1 = G[0, 0]
C = A1 / lam1
beta = log(C, 2) + 1

n_real = (h1 - beta) / alpha
n_est = floor(n_real)
print("Estimated k0 near:", n_est)

# Search window
window = 50000
batch = 5000
found = False
start = time.time()

print(f"Scanning k0 in [{n_est - window}, {n_est + window}]...")

for i, k in enumerate(range(n_est - window, n_est + window + 1)):
    try:
        b = Integer(k).to_bytes(K0_BYTES, 'big')
    except OverflowError:
        continue

    if b.startswith(PREFIX):
        decoded = b.decode(errors='replace')
        tail = decoded[len(PREFIX):]
        if sum(32 <= ord(c) < 127 for c in tail) >= int(len(tail) * 0.9):
            print("\n✅ Found plausible k0:")
            print("k0 =", k)
            print("bytes =", b)
            print("ascii =", decoded)
            found = True
            break

    if i % batch == 0 and i > 0:
        print(f"Checked {i} candidates... {time.time() - start:.1f}s elapsed")

if not found:
    print("❌ No match found in this window. Try expanding it further.")

print(f"Total time: {time.time() - start:.2f} seconds")

