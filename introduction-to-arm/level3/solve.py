from pwn import *
context.arch = 'aarch64'

asm_bytes = asm(""" 
mul x0, x0, x1
add x0, x0, x2
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{whiOrwsbNflT5MrxqFomnM3avV3.dFjM2MDL4AjMyMzW}