import random
from base64 import b64encode
from functools import reduce
from itertools import product

# Given final hash
target_hash = "aO3qDbHFoittWTN6MoUYw9CZiC9jdfftFGw1ipES89ugOwk2xCUzDpPdpBWtBP3yarjNOPLXjrMODD"

# Custom base64 maps
b64encode_map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0987654321+/"
b64decode_map = {c: i for i, c in enumerate(b64encode_map)}

# Recreate permutation group
class Perm:
    def __init__(self, cycles, n=32):
        self.n = n
        self.p = list(range(1, n + 1))
        for cycle in cycles:
            for i in range(len(cycle)):
                self.p[cycle[i] - 1] = cycle[(i + 1) % len(cycle)]

    def __call__(self, other):
        return Perm.from_perm([self.p[i - 1] for i in other.p])

    def __eq__(self, other):
        return self.p == other.p

    def __hash__(self):
        return hash(tuple(self.p))

    @staticmethod
    def from_perm(p):
        obj = Perm([], len(p))
        obj.p = p[:]
        return obj

    def inverse(self):
        inv = [0] * self.n
        for i, pi in enumerate(self.p):
            inv[pi - 1] = i + 1
        return Perm.from_perm(inv)

# Generators for G
generators = [
    Perm([(1,2,3,4),(5,6,7,8),(9,10,11,12),(13,14,15,16),(17,18,19,20),(21,22,23,24),(25,26,27,28),(29,30,31,32)]),
    Perm([(1,24,3,22),(2,23,4,21),(5,14,7,16),(6,13,8,15),(9,27,11,25),(10,26,12,28),(17,31,19,29),(18,30,20,32)]),
    Perm([(1,5,12,30),(2,6,9,31),(3,7,10,32),(4,8,11,29),(13,25,19,21),(14,26,20,22),(15,27,17,23),(16,28,18,24)]),
    Perm([(1,26),(2,27),(3,28),(4,25),(5,14),(6,15),(7,16),(8,13),(9,23),(10,24),(11,21),(12,22),(17,31),(18,32),(19,29),(20,30)])
]

# Brute-generate group
def generate_group(generators):
    seen = set()
    queue = [Perm.from_perm(list(range(1, 33)))]
    seen.add(queue[0])
    while queue:
        current = queue.pop()
        for g in generators:
            new = g(current)
            if new not in seen:
                seen.add(new)
                queue.append(new)
    return list(seen)

# Set up permutation group
G = generate_group(generators)
num2e = G
e2num = {g: i for i, g in enumerate(G)}

# Seeded random matrix generator
def gen_random_mat(seed: int, size: int):
    random.seed(seed)
    return [[random.randint(0, 1) for _ in range(size)] for _ in range(size)]

# Matrix-vector multiplication over permutation group
def mat_vec_mul(mat, vec):
    return [
        reduce(lambda x, y: x(y), [a.inverse() if b else a for a, b in zip(vec, row)], Perm.from_perm(list(range(1, 33))))
        for row in mat
    ]

# Inverse hash function (reverse the 10 rounds)
def reverse_hash(target_hash):
    sz = len(target_hash)
    vec = [num2e[b64decode_map[c]] for c in target_hash]
    mat = gen_random_mat(0xcaffe * 3 * 0xc0ffee, sz)

    for _ in range(10):
        # Need to solve: mat_vec_mul(mat, x) == vec
        # This is hard algebraically. Instead, brute-force try every base64 string of size sz.
        print("[*] Trying brute-force recovery – this may take time...")

        for candidate in product(range(64), repeat=sz):
            trial_vec = [num2e[i] for i in candidate]
            out = mat_vec_mul(mat, trial_vec)
            if out == vec:
                decoded = ''.join(b64encode_map[i] for i in candidate)
                print("[+] Found base64 input:", decoded)
                return decoded

    return None

# Recover and decode flag
def recover_flag():
    b64_data = reverse_hash(target_hash)
    if not b64_data:
        print("[-] Failed to recover base64 string.")
        return

    # Decode base64 and check format
    import base64
    for pad in ("", "=", "=="):
        try:
            msg = base64.b64decode(b64_data + pad)
            if msg.startswith(b"grey{") and msg.endswith(b"}"):
                print("[+] Flag found:", msg.decode())
                return
        except:
            continue

recover_flag()

