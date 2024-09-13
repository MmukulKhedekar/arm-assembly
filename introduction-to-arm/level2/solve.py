from pwn import *
context.arch = 'aarch64'

asm_bytes = asm(""" 
mov x1, #0xbeef
movk x1, #0xdead, lsl 16    
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{gJ-WjzpgVXu91uK0UGBzjxdQFy-.dBjM2MDL4AjMyMzW}