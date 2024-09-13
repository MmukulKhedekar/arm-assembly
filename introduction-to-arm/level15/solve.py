from pwn import *
context.arch = 'aarch64'

asm_bytes = asm("""
fibonacci:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    sub sp, sp, #16
    str w0, [sp, #12]
    
    cmp w0, #0 
    beq finale
    cmp w0, #1 
    beq finale 

    sub w0, w0, #1 
    bl fibonacci
    str x0, [sp] 
    
    ldr w0, [sp, #12]
    sub w0, w0, #2 
    bl fibonacci
    ldr x1, [sp] 
    add x0, x0, x1 
    
finale:
    add sp, sp, #16
    ldp x29, x30, [sp], #16
    ret
""")

with process('/challenge/run') as p:
    p.send(asm_bytes)
    p.stdin.close()
    p.interactive()

## pwn.college{AohAAHHpn9U7jvWenz5k0iOD3DS.dJzM2MDL4AjMyMzW}
