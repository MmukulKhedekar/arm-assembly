from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
loop:
    ldr x3, [x0], #8 
    add x2, x2, x3
    sub x1, x1, #1 
    cbnz x1, loop
    mov x0, x2
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{Epkka9zUuVp-8XI7X9ZhXNiLdtY.dBzM2MDL4AjMyMzW}