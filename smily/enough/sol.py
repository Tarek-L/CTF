import hashlib
from Crypto.Cipher import AES
from multiprocessing import Pool, cpu_count
import itertools
import os

# Read given and cipher from flag.txt
with open("flag.txt") as f:
    data = f.read()
namespace = {}
exec(data, {}, namespace)
given = namespace["given"]
ciphertext = bytes.fromhex(namespace["cipher"])

# Constants
LOWER_BITS = 12
UPPER_BITS = 32 - LOWER_BITS
MAX_LOW = 2**LOWER_BITS
KEY_LENGTH = 100  # characters
TOTAL_VALUES = 608  # 624 - 16


# Build a lookup for each given upper to all possible original digits
def possible_digits(g_upper):
    base = g_upper << LOWER_BITS
    return [(base | low) % MAX_LOW for low in range(MAX_LOW)]


# Brute force with early pruning
def try_combinations(indices):
    """
    Try brute-force on a given set of combinations (starting from specific indices).
    indices: list of possible values for first few digits (to allow splitting work).
    """
    # Build all digit options for each index in `given`
    digit_options = [possible_digits(g) for g in given]

    # Override the beginning with the provided indices (work split)
    for i, val in enumerate(indices):
        digit_options[i] = [val]

    # Only consider combinations that are 100 digits long when joined
    for combo in itertools.product(*digit_options):
        key_str = "".join(str(d) for d in combo)
        if len(key_str) < KEY_LENGTH:
            continue
        key_str = key_str[:KEY_LENGTH]
        key = hashlib.sha256(key_str.encode()).digest()
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted = cipher.decrypt(ciphertext)
        if decrypted.startswith(b".;,;.{"):
            print("[+] Found!")
            print("Key string:", key_str)
            print("Decrypted:", decrypted)
            os._exit(0)
    return


# Work dispatcher
def main():
    prefix_digits = (
        2  # Try all combinations for the first 2 digits (4096 * 4096 total tasks)
    )
    options = [possible_digits(g) for g in given[:prefix_digits]]
    jobs = list(itertools.product(*options))

    print(f"[+] Total jobs: {len(jobs)}")
    with Pool(cpu_count()) as pool:
        pool.map(try_combinations, jobs)


if __name__ == "__main__":
    main()
