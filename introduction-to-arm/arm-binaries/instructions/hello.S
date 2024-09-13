.data

msg:
        .ascii "Hello, AArch64!\n"
len = . - msg

.text

.globl _start
_start:
        // Prepare write(int fd, const void *buf, size_t count)
        mov x0, #1
        ldr x1, =msg
        ldr x2, =len
        mov w8, #64 
        svc #0 
        
        // Prepare exit(int status)
        mov x0, #0
        mov w8, #93
        svc #0
