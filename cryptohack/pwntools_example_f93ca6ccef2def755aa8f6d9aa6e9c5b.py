from pwn import *  # pip install pwntools
import base64
import codecs
from Crypto.Util.number import bytes_to_long, long_to_bytes
import json

r = remote("socket.cryptohack.org", 13377, level="debug")


def json_recv():
    line = r.recvline()
    return json.loads(line.decode())


def json_send(hsh):
    request = json.dumps(hsh).encode()
    r.sendline(request)


while True:
    try:
        received = json_recv()
        print("Received type:", received.get("type"))
        print("Received encoded value:", received.get("encoded"))

        encoding = received["type"]
        c = received["encoded"]

        # Handle each encoding type
        if encoding == "base64":
            decoded = base64.b64decode(c).decode()
        elif encoding == "hex":
            decoded = bytes.fromhex(c).decode()
        elif encoding == "rot13":
            decoded = codecs.decode(c, "rot_13")
        elif encoding == "bigint":
            decoded = long_to_bytes(int(c, 16)).decode()
        elif encoding == "utf-8":
            decoded = "".join(chr(b) for b in c)
        else:
            print(f"Unknown encoding type: {encoding}")
            break

        print("Decoded:", decoded)
        json_send({"decoded": decoded})

    except EOFError:
        print("Server closed the connection.")
        break
    except Exception as e:
        print("Error:", e)
        break

r.close()
