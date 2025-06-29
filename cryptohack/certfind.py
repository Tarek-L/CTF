from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from hashlib import sha256
import requests

with open(
    "/home/fkey/ctf/cryptohack/transparency_afff0345c6f99bf80eab5895458d8eab.pem", "rb"
) as f:
    pub_key = serialization.load_pem_public_key(f.read(), backend=default_backend())

pub_der = pub_key.public_bytes(
    encoding=serialization.Encoding.DER,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

fp = sha256(pub_der).hexdigest()
print("SHA-256 Fingerprint:", fp)

url = f"https://crt.sh/?q=sha256:{fp}&output=json"
resp = requests.get(url)
resp.raise_for_status()

entries = resp.json()
if not entries:
    print("❗ No entries found for that fingerprint in crt.sh.")
else:
    for cert in entries:
        print("✅ Certificate found:")
        print("  Serial Number:", cert.get("serial_number"))
        print("  Issuer Name  :", cert.get("issuer_name"))
        print("  Common Name  :", cert.get("common_name"))
        print("  Alt Names    :", cert.get("name_value"))
