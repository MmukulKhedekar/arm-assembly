from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
ldr x0, [sp], #8
ldr x1, [sp], #8
add x0, x0, x1
ldr x1, [sp], #8
add x0, x0, x1
ldr x1, [sp], #8
add x0, x0, x1
ldr x1, [sp], #8
add x0, x0, x1
ldr x1, [sp], #8
add x0, x0, x1
ldr x1, [sp], #8
add x0, x0, x1
ldr x1, [sp], #8
add x0, x0, x1
mov x2, #0x08
udiv x0, x0, x2
str x0, [sp]
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{8_zJmZe1G6WXTjDY6_7HMNE-G3Z.ddjM2MDL4AjMyMzW}