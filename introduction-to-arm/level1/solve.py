from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
mov X1, #0x1337
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{colSh4OvQLeSOJX3IC5lZjKd0Kf.dlTM2MDL4AjMyMzW}