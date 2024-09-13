from pwn import *
context.arch = 'aarch64'

asm_bytes = asm(""" 
lsl x0, x0, #32
lsr x0, x0, #56
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{YTMLREKlMnfLp3BxaG7nKLtDBD-.dRjM2MDL4AjMyMzW}