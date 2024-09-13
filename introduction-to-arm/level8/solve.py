from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
mov x0, #0x4000
movk x0, #0x40, lsl 16
ldp x1, x2, [x0]
stp x1, x2, [x0, #0x10]
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{UI3gosMIBAvsHo-Y4cUtUV3Iy7Q.dZjM2MDL4AjMyMzW}