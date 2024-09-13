from pwn import *
context.arch = 'aarch64'

asm_bytes = asm(""" 
udiv x2, x0, x1
msub x0, x1, x2, x0
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{EDKCkvWbzA81tr1w7Klqse5NSBU.dNjM2MDL4AjMyMzW}