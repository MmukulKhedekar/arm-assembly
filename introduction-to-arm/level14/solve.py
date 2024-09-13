from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
calc_avg:
    sub sp, sp, #16
    mov x4, x1
loop:
    ldr x3, [x0], #8     
    add x2, x2, x3
    sub w1, w1, #1 
    cbnz w1, loop
    udiv x2, x2, x4
    mov x0, x2 
    add sp, sp, #16
    ret 
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{YCOM8fDCflGFtnmKELyH4bVD-bO.dNzM3MDL4AjMyMzW}