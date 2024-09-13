.global _start
_start:
        mov x29, #10
        mov x30, #20
        stp x29, x30, [sp, #-16]! 
        mov x29, #0x10
        mov x30, #11
        ldp x29, x30, [sp], #16
        b exit
 exit:
        mov w8, #93
        svc 0
