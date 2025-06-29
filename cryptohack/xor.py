flag = [ord(b) for b in "label"]
flag = [b ^ 13 for b in flag]
flag = "".join([chr(b) for b in flag])

print(f"crypto{{{flag}}}")
