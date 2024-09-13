from pwn import *
context.arch = 'aarch64'

asm_bytes = asm(""" 
mov x2, #0x4000
movk x2, #0x4000, lsl 16
movk x2, #0x1337, lsl 32
ldr x0, [x2]
add x2, x2, #0x08
ldr x1, [x2]
add x3, x0, x1
add x2, x2, #0x08
str x3, [x2]
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{YBQJj8VJKVq9l1z8IhwoMrMvg4H.dVjM2MDL4AjMyMzW}