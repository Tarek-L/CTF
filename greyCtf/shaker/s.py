import socket
from hashlib import md5

HOST = 'challs.nusgreyhats.org'
PORT = 33302
FLAG_LEN = 64
TARGET_MD5 = '4839d730994228d53f64f0dca6488f8d'
NUM_LEAKS = 200

def recvuntil(sock, ending=b'> '):
    data = b''
    while not data.endswith(ending):
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        except socket.timeout:
            break
    return data

def parse_result(output):
    for line in output.decode().splitlines():
        if line.startswith("Result: "):
            return bytes.fromhex(line.split("Result: ")[1])
    return None

def collect_outputs():
    results = []
    with socket.create_connection((HOST, PORT)) as sock:
        sock.settimeout(2)
        for _ in range(NUM_LEAKS):
            recvuntil(sock)           # Wait for menu
            sock.sendall(b'2\n')      # See inside
            output = recvuntil(sock) # Read output and menu again
            result = parse_result(output)
            if result:
                results.append(result)
    return results

def recover_flag(results):
    counts = [{} for _ in range(FLAG_LEN)]
    for r in results:
        for i, b in enumerate(r):
            counts[i][b] = counts[i].get(b, 0) + 1

    most_common = bytes(max(pos.items(), key=lambda x: x[1])[0] for pos in counts)

    for r in results:
        possible = bytes(a ^ b for a, b in zip(r, most_common))
        if md5(possible).hexdigest() == TARGET_MD5:
            return possible
    return None

if __name__ == "__main__":
    print("[*] Connecting and collecting...")
    leaks = collect_outputs()
    print(f"[+] Collected {len(leaks)} samples")

    print("[*] Recovering flag...")
    flag = recover_flag(leaks)

    if flag:
        print("[+] Flag recovered:", flag.decode(errors='replace'))
    else:
        print("[-] Failed to recover flag.")

