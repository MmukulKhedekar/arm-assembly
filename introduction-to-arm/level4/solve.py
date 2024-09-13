from pwn import *
context.arch = 'aarch64'

asm_bytes = asm(""" 
madd x0, x0, x1, x2
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{crBdkmdfeXRObrzCklUhdahv6Vc.dJjM2MDL4AjMyMzW}