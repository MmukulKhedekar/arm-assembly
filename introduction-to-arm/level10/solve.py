from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
stp x0, x1, [sp, #-16]!
ldp x1, x0, [sp], #16
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{IJ14c-5mjwRTQftmc-ZHl3gDXho.dhjM2MDL4AjMyMzW}