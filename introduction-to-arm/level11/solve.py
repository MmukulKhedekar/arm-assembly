from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
    ldr x2, [x0], #8
    sub x1, x1, #1
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

## pwn.college{wd6AObkE0NjCt5bVNOVuZKBoNpV.dljM2MDL4AjMyMzW}