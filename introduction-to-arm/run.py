#!/opt/pwn.college/python

import os
import pathlib
import random
import struct
import sys
import pwnlib
import pwnlib.asm

from typing import List, Optional

from capstone import *
from unicorn.arm64_const import *
from unicorn import *

pwnlib.context.context.update(arch = 'aarch64')

config = (pathlib.Path(__file__).parent / ".config").read_text()
level = int(config)

os.setuid(os.geteuid())

LEVELS = [
    # Registers
    "EmbryoARMSetRegister",
    "EmbryoARMSetLargeRegister",
    "EmbryoARMLineEquation",
    "EmbryoARMLineEquationSingleInstr",
    "EmbryoARMModulo",
    # Bits in Registers
    "EmbryoARMBitShift",

    # Memory Access
    "EmbryoARMMemoryAccess",
    "EmbryoARMMemoryAccessPairs",

    # Stack
    "EmbryoARMPopPush",
    "EmbryoARMRegSwap",

    # Control Flow
    "EmbryoARMMemoryAccessArray",
    "EmbryoARMMemoryAccessArraySixInstr",
    "EmbryoARMJumps",

    # Functions
    "EmbryoARMAvg",
    "EmbryoARMFib",
    ]

class EmbryoARMBase:
    """
    EmbryoARM:
    A set of levels to teach people the basics of ARM assembly:
    - registers_use
    - stack
    - functions
    - control statements
    Level Layout:
    === Reg ===
    1. mov immediate
    2. movk immediate
    3. Reg complex use
    4. Multiple action instructions
    5. Modulo
    === Bits in Registers ===
    6. Shifting bits
    === Mem Access ===
    7. Read & Write from static memory location
    8. Loading pairs of registers
    === Stack ===
    10. Pop from stack, compute sum
    11. Stack operations as a swap
   === Control Statements ===
    12. Accessing values in an arrray
    13. Accessing values in an arrray (barrel loader)
    14. Unconditional jumps (jump trampoline, relative and absolute)

    === Functions ===
    15. fibonacci
    """

    BASE_STACK = 0x7FFFFF000000
    RSP_INIT = BASE_STACK + 0x200000
    BASE_ADDR = 0x400000
    CODE_OFFSET = 0
    FLAG_PATH = "/flag"

    DATA_OFFSET = 0x4000
    DATA_ADDR = BASE_ADDR + DATA_OFFSET

    LIB_OFFSET = 0x3000
    LIB_ADDR = BASE_ADDR + LIB_OFFSET

    def create_emu(self):
        mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)

        mu.mem_map(self.BASE_ADDR, 2 * 1024 * 1024)
        mu.mem_write(self.BASE_ADDR + self.CODE_OFFSET, self.asm)
        mu.mem_map(self.BASE_STACK, 2 * 1024 * 1024)
        mu.reg_write(UC_ARM64_REG_SP, self.RSP_INIT)

        for reg in range(UC_ARM64_REG_X0, UC_ARM64_REG_X28 + 1):
            mu.reg_write(reg, 0x0)
        mu.reg_write(UC_ARM64_REG_X29, 0x0)
        mu.reg_write(UC_ARM64_REG_X30, 0x0)

        self.emu = mu

    def __init__(self, asm):
        self.asm: Optional[bytes] = asm
        self.emu_err = None

    def print_level_text(self):
        raise NotImplementedError

    def trace(self):
        raise NotImplementedError

    def run(self):
        #self.print_welcome()
        self.print_level_text()

        self.get_asm_from_user()

        self.create_emu()

        print("Executing your code...")
        self.print_disasm()

        won = self.trace()
        if won:
            self.print_flag()
        else:
            print("\nSorry, no flag :(.")

        return won

    def blacklist_hook(self, uc, address, size, user_data):
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        i = next(md.disasm(uc.mem_read(address, size), address))

        if i.mnemonic in self.filter_list:
            self.emu_err = "fail: this instruction is not allowed: %s" % i.mnemonic
            uc.emu_stop()

    def whitelist_hook(self, uc, address, size, user_data):
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        i = next(md.disasm(uc.mem_read(address, size), address))

        if i.mnemonic not in self.filter_list:
            self.emu_err = "fail: this instruction is not allowed: %s" % i.mnemonic
            uc.emu_stop()

    def add_emu_inst_filter(self, insts: List, whitelist: bool):
        self.filter_list = insts
        if whitelist:
            self.emu.hook_add(UC_HOOK_CODE, self.whitelist_hook)
        else:
            self.emu.hook_add(UC_HOOK_CODE, self.blacklist_hook)

 

    def print_flag(self):
        with open(self.FLAG_PATH, "r") as fp:
            flag = fp.read()
            print(flag)

    def print_disasm(self):
        print("---------------- CODE ----------------")
        md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
        for i in md.disasm(self.asm, self.BASE_ADDR + self.CODE_OFFSET):
            print("0x%x:\t%-6s\t%s" % (i.address, i.mnemonic, i.op_str))
        print("--------------------------------------")

    def get_asm_from_user(self):
        if not self.asm:
            print("Please give me your assembly in bytes (up to 0x1000 bytes): ")
            self.asm = sys.stdin.buffer.read(0x1000)

    def debug_output(self):
        print(f"PC {hex(self.emu.reg_read(UC_ARM64_REG_PC))}")
        print(f"SP {hex(self.emu.reg_read(UC_ARM64_REG_SP))}")
        print(f"LR {hex(self.emu.reg_read(UC_ARM64_REG_LR))}")
        print(f"X0 {hex(self.emu.reg_read(UC_ARM64_REG_X0))}")
        print(f"X1 {hex(self.emu.reg_read(UC_ARM64_REG_X1))}")
        print(f"X2 {hex(self.emu.reg_read(UC_ARM64_REG_X2))}")
        print(f"X3 {hex(self.emu.reg_read(UC_ARM64_REG_X3))}")
        print(f"X4 {hex(self.emu.reg_read(UC_ARM64_REG_X4))}")
        print(f"X5 {hex(self.emu.reg_read(UC_ARM64_REG_X5))}")
        print(f"X6 {hex(self.emu.reg_read(UC_ARM64_REG_X6))}")
        print(f"X7 {hex(self.emu.reg_read(UC_ARM64_REG_X7))}")
        print(f"X8 {hex(self.emu.reg_read(UC_ARM64_REG_X8))}")

class EmbryoARMSetRegister(EmbryoARMBase):
    """
    Set register
    """
    def __init__(self, asm=None, should_debug=False):
        super().__init__(asm)
        self.reg = "X1"
        self.value = 0x1337

    def print_level_text(self):
        print("Similar to amd64, the mov instruction can be used.  However, literal values must be prefixed with the # symbol!")

        print(
            "Please set the following:\n"
        )
        print(f"{self.reg} = {hex(self.value)}\n")

    def trace(self):
        try:
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()
            return False

        x1 = self.emu.reg_read(UC_ARM64_REG_X1)
        return x1 == self.value

class EmbryoARMSetLargeRegister(EmbryoARMBase):
    """
    Set register
    """
    def __init__(self, asm=None):
        super().__init__(asm)
        self.reg = "X1"
        self.value = 0xdeadbeef

    def print_level_text(self):
        print(
            "aarch64 registers are 64 bits in size, but the mov instruction only works with 16 bit immediate values.\n"
            "In order to move larger literal values, the mov and movk instructions are needed.\n\n"

            "movk loads a value into the destination register with a specific bitshift, retaining all other bytes\n\n"
            "Example:\n"
            "\tmov x0, #0x3700\n"
            "\tmovk x0, #0x13, lsl 16\n\n"
            "Results in X0 containing the value 0x133700\n"
            )

        print(
            "Please set the following:\n"
        )
        print(f"\t{self.reg} = {hex(self.value)}\n")

    def trace(self):
        try:
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()
            return False

        x0_val = self.emu.reg_read(UC_ARM64_REG_X1)
        return x0_val == self.value

class EmbryoARMLineEquation(EmbryoARMBase):
    """
    Reg complex use: calculate y = mx + b
    """

    def __init__(self, asm=None, should_debug=False):
        super().__init__(asm)
        self.val_x0 = random.randint(1, 10000)
        self.val_x1 = random.randint(1, 10000)
        self.val_x2 = random.randint(1, 10000)

    def print_level_text(self):
        print(
                "Arithmetic instructions take three arguments\n"
                "Example:\n"
                "\t add x0, x1, x2\n\n"
                "This example is equivalent to x0 = x1 + x2\n"
        )

        print(
            "Please compute the following:\n\n"
            "f(x) = mx + b, where:\n"
            "\tm = X0\n"
            "\tx = X1\n"
            "\tb = X2\n\n"
            "Place the value into X0 given the above.\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"\tX0 = {hex(self.val_x0)}\n"
            f"\tX1 = {hex(self.val_x1)}\n"
            f"\tX2 = {hex(self.val_x2)}\n\n"
        )

    def trace(self):
        try:
            self.emu.reg_write(UC_ARM64_REG_X0, self.val_x0)
            self.emu.reg_write(UC_ARM64_REG_X1, self.val_x1)
            self.emu.reg_write(UC_ARM64_REG_X2, self.val_x2)
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        target = (self.val_x0 * self.val_x1) + self.val_x2
        print(target)
        print( self.emu.reg_read(UC_ARM64_REG_X0))
        return target == self.emu.reg_read(UC_ARM64_REG_X0)

class EmbryoARMLineEquationSingleInstr(EmbryoARMBase):
    """
    Reg complex use: calculate y = mx + b single instruction
    """

    def __init__(self, asm=None, should_debug=False):
        super().__init__(asm)
        self.val_x0 = random.randint(1, 10000)
        self.val_x1 = random.randint(1, 10000)
        self.val_x2 = random.randint(1, 10000)

    def print_level_text(self):
        print(
            "aarch64 instructions can have multiple arguments and perform multiple actions.."
            "Please compute the following:\n"
            "f(x) = mx + b, where:\n"
            "\tm = X0\n"
            "\tx = X1\n"
            "\tb = X2\n"
            "Place the value into X0 given the above.\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"X0 = {hex(self.val_x0)}\n"
            f"X1 = {hex(self.val_x1)}\n"
            f"X2 = {hex(self.val_x2)}\n\n"
        )
        print(
                "Constraints:\n"
                "\t- You may submit only one instruction.\n"
        )

    def trace(self):
        if  len(self.asm) != 4:
            print(f"Only submit one aarch64 instruction!  {len(self.asm)} bytes received, but expecting 4!")
            return False
        try:
            self.emu.reg_write(UC_ARM64_REG_X0, self.val_x0)
            self.emu.reg_write(UC_ARM64_REG_X1, self.val_x1)
            self.emu.reg_write(UC_ARM64_REG_X2, self.val_x2)
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        target = (self.val_x0 * self.val_x1) + self.val_x2
        print(target)
        print( self.emu.reg_read(UC_ARM64_REG_X0))
        return target == self.emu.reg_read(UC_ARM64_REG_X0)

class EmbryoARMModulo(EmbryoARMBase):
    """
    Modulo
    """

    def __init__(self, asm=None, should_debug=False):
        super().__init__(asm=asm)
        self.val_x0 = random.randint(1000000, 1000000000)
        self.val_x1 = 2 ** random.randint(1, 10) - 1

    def print_level_text(self):
        print(
            "Modulo in aarch64 cannot be done in a single instruction!\n"
        )

        print(
            "Please compute the following:\n" 
            "\tX0 % X1\n\n" 
            "Place the value in X0.\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"\tX0 = {hex(self.val_x0)}\n"
            f"\tX1 = {hex(self.val_x1)}\n"
        )

        print("Constraints:\n"
              "\t- You may submit 2 instructions.\n"
        )

    def trace(self):
        if  len(self.asm) > 8:
            print(f"Maximum of 2 instruction aarch64 instructions!  {len(self.asm)} bytes received, but expecting maximum of 8!")
            return False
        try:
            self.emu.reg_write(UC_ARM64_REG_X0, self.val_x0)
            self.emu.reg_write(UC_ARM64_REG_X1, self.val_x1)
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        target = self.val_x0 % self.val_x1
        return target == self.emu.reg_read(UC_ARM64_REG_X0)

class EmbryoARMBitShift(EmbryoARMBase):
    """
    Shift
    """

    def __init__(self, asm=None):
        super().__init__(asm)
        self.val_x0 = random.randint(0x55AA55AA55AA55AA, 0x99BB99BB99BB99BB)

    def print_level_text(self):
        print(
            "Shifting in assembly is another interesting concept! aarch64 allows you to 'shift'\n"
            "bits around in a register. Take for instance, X1. For the sake of this example\n"
            "say X1 only can store 8 bits (it normally stores 64). The value in X1 is:\n"
            "X1 = 10001010\n"
            "We if we shift the value once to the left:\n"
            "lsl X1, X1, 1\n"
            "The new value is:\n"
            "X1 = 00010100\n"
            "As you can see, everything shifted to the left and the highest bit fell off and\n"
            "a new 0 was added to the right side. You can use this to do special things to \n"
            "the bits you care about. It also has the nice side affect of doing quick multiplication,\n"
            "division, and possibly modulo.\n\n"
            "Here are the important instructions: \n"
            "\tlsl reg1, reg1, reg2       <=>     Shift reg1 left by the amount in reg2\n"
            "\tlsr reg1, reg1, reg2       <=>     Shift reg1 right by the amount in reg2\n\n"
            "Note: all 'regX' can be replaced by a constant or memory location\n"
        )

        print(
            "Using only the following instructions:\n"
            "\tlsl, lsr\n\n"
            "Please perform the following:\n"
            "\tSet X0 to the 4th least significant byte of X0\n\n"

            "i.e.\n"
            "\tX1 = | B7 | B6 | B5 | B4 | B3 | B2 | B1 | B0 |\n"
            "\tSet X0 to the value of B3\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"\tX0 = {hex(self.val_x0)}\n"
        )

    def trace(self):
        self.add_emu_inst_filter(["lsl", "lsr"], True)
        try:
            self.emu.reg_write(UC_ARM64_REG_X0, self.val_x0)
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        if self.emu_err:
            print(self.emu_err)
            return False

        target = (self.val_x0 >> 24) & 0xFF
        print(hex(target))

        print(hex(self.emu.reg_read(UC_ARM64_REG_X0)))
        return target == self.emu.reg_read(UC_ARM64_REG_X0)

class EmbryoARMMemoryAccess(EmbryoARMBase):
    """
    Read and Write to memory
    """

    def __init__(self, asm=None):
        super().__init__(asm)
        self.val0 = random.randint(1000000, 2000000)
        self.val1 = random.randint(1000000, 2000000)

        # make this larger so it cannot be a single move
        self.BASE_ADDR = 0x1337_40_00_00_00
        self.DATA_ADDR = self.BASE_ADDR + self.DATA_OFFSET

    def print_level_text(self):
        print(
            "Memory addresses cannot be directly accessed in aarch64.  Only registers can be operated on.\n"
            "Values must be loaded from memory to a register with ldr and written back to memory via str\n"
            "For example, to increment a value located at memory address 0x1337, the following instructions\n"
            "would be needed:\n\n"
            "\tmov x1, #0x1337\n"
            "\tldr x0, [x1]\n"
            "\tadd x0, x0, #1\n"
            "\tstr x0, [x1]\n\n"
            "Locations memory addresses can also be offset from.  Example:\n"
            "\tmov x1, #0x4000\n"
            "\tldr x0, [x1, #8]\n\n"
            "Would load 8 bytes stored at 0x4008 into x0\n"
        )

        print(
            "Please perform the following:\n"
            f"\t1. Place the value stored at {hex(self.DATA_ADDR)} into X0\n"
            f"\t2. Place the value stored at {hex(self.DATA_ADDR + 8)} into X1\n"
            f"\t3. Add these values and store the result at address {hex(self.DATA_ADDR + 0x10)}\n"

            "Make sure:\n"
            f"\t- The value in X0 is the original value stored at {hex(self.DATA_ADDR)}\n"
            f"\t- The value in X1 is the original value stored at {hex(self.DATA_ADDR + 8)}\n"
            f"\t- [{hex(self.DATA_ADDR + 0x10)}] now has the addition's result.\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"\t[{hex(self.DATA_ADDR)}] = {hex(self.val0)}\n"
            f"\t[{hex(self.DATA_ADDR + 8)}] = {hex(self.val1)}\n\n"
        )

    def trace(self):
        is_correct = False
        try:
            self.emu.mem_write(self.DATA_ADDR, struct.pack("<Q", self.val0))
            self.emu.mem_write(self.DATA_ADDR + 8, struct.pack("<Q", self.val1))
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()
            return is_correct

        try:
            target = struct.unpack("<Q", self.emu.mem_read(self.DATA_ADDR + 0x10, 8))[0]
            is_correct = target == self.val0 + self.val1

            is_correct &= self.val0 == self.emu.reg_read(UC_ARM64_REG_X0)
            is_correct &= self.val1 == self.emu.reg_read(UC_ARM64_REG_X1)
        except Exception as e:
            print("Fail!")
            return False

        return is_correct

class EmbryoARMMemoryAccessPairs(EmbryoARMBase):
    """
    Read and Write to memory
    """

    def __init__(self, asm=None):
        super().__init__(asm)
        self.val0 = random.randint(1000000, 2000000)
        self.val1 = random.randint(1000000, 2000000)

    def print_level_text(self):
        print(
            "Consecutive memory addresses can be loaded and stored in a single instruction as a pair!\n"
        )

        print(
            "Please perform the following:\n"
            f"\t1. Place the value stored at {hex(self.DATA_ADDR)} to the memory location {hex(self.DATA_ADDR + 0x10)}\n"
            f"\t2. Place the value stored at {hex(self.DATA_ADDR + 8)} to the memory location {hex(self.DATA_ADDR + 0x18)}\n"

            "Constraints:\n"
            "\t- You can only use mov, movk, stp, and ldp\n"
            "\t- You are allowed four instructions\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"\t[{hex(self.DATA_ADDR)}] = {hex(self.val0)}\n"
            f"\t[{hex(self.DATA_ADDR + 8)}] = {hex(self.val1)}\n\n"
        )

    def trace(self):
        self.add_emu_inst_filter(["ldp", "stp", "mov", "movk"], True)

        if len(self.asm) > 16:
            print(f"Maximum 4 aarch64 instructions allowed!  {len(self.asm)} bytes received, but expecting <=16!")
            return False


        is_correct = False
        try:
            self.emu.mem_write(self.DATA_ADDR, struct.pack("<Q", self.val0))
            self.emu.mem_write(self.DATA_ADDR + 8, struct.pack("<Q", self.val1))
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()
            return is_correct

        try:
            res0 = struct.unpack("<Q", self.emu.mem_read(self.DATA_ADDR + 0x10, 8))[0]
            res1 = struct.unpack("<Q", self.emu.mem_read(self.DATA_ADDR + 0x18, 8))[0]
            is_correct = res0 == self.val0
            is_correct &= res1 == self.val1

        except Exception as e:
            print("Fail!")
            return False

        return is_correct


class EmbryoARMMemoryAccessArray(EmbryoARMBase):
    """
    Read and Write to memory
    """

    def __init__(self, asm=None, should_debug=False):
        super().__init__(asm)
        self.arr_addr = self.DATA_ADDR + (random.randint(10, 100) * 8)
        self.arr_len = random.randint(50, 100)
        self.data = [
            random.randint(2 ** 32 - 1000000, 2 ** 32 - 1) for _ in range(self.arr_len)
        ]
        self.key = random.randint(0xAA55AA55, 0xBB99BB99)

    def print_level_text(self):
        print(
            "Loops can be created using conditional branch instructions.\n"
            "The branch instruction in aarch64 is b.\n"
            "To conditionally branch a dot suffix (ex: .gt) is appended resulting in b.gt.\n"
            "This would be equivalent to jg in amd64.\n\n"
        )
        print(
            "Please compute the sum of n consecutive quad words, where:\n"
            "\tX0 = memory address of the 1st quad word\n"
            "\tX1 = n (amount to loop for)\n\n"

            "set x0 to the sum computed\n\n"

            "We will now set the following in preparation for your code:\n"
            f"\t- [{hex(self.arr_addr)}:{hex(self.arr_addr + (self.arr_len * 8))}] = {{n qwords]}}\n"
            f"\t- X0 = {hex(self.arr_addr)}\n"
            f"\t- X1 = {self.arr_len}\n"
        )
    def trace(self):
        try:
            self.emu.reg_write(UC_ARM64_REG_X0, self.arr_addr)
            self.emu.reg_write(UC_ARM64_REG_X1, self.arr_len)

            self.emu.mem_write(self.arr_addr - 0x4, struct.pack("<I", self.key))
            self.emu.mem_write(
                self.arr_addr, struct.pack(f"<{'q'*self.arr_len}", *self.data)
            )
            self.emu.mem_write(
                self.arr_addr + (self.arr_len * 8), struct.pack("<I", self.key)
            )

            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            print(f"PC: {hex(self.emu.reg_read(UC_ARM64_REG_PC))}")

        target = sum(self.data)
        correct = target == self.emu.reg_read(UC_ARM64_REG_X0)

        if not correct:
            print(
            f"""
            [!] ------------------------- [!]
            Failed test check:
            Input:
            X0 = {hex(self.arr_addr)}
            X1 = {self.arr_len}
            [{hex(self.arr_addr)}: = {[hex(i) for i in self.data]}

            Correct output:
            X0 = {hex(target)}

            Your output
            X0 = {hex(self.emu.reg_read(UC_ARM64_REG_X0))}
            [!] ------------------------- [!]
            """
            )
        return correct


class EmbryoARMMemoryAccessArraySixInstr(EmbryoARMBase):
    """
    Read and Write to memory Six Instr
    """

    def __init__(self, asm=None, should_debug=False):
        super().__init__(asm)
        self.arr_addr = self.DATA_ADDR + (random.randint(10, 100) * 8)
        self.arr_len = random.randint(50, 100)
        self.data = [
            random.randint(2 ** 32 - 1000000, 2 ** 32 - 1) for _ in range(self.arr_len)
        ]
        self.key = random.randint(0xAA55AA55, 0xBB99BB99)

    def print_level_text(self):


        print(
            "Loops can be created using conditional branch instructions.\n"
            "The branch instruction in aarch64 is b.\n"
            "To conditionally branch a dot suffix (ex: .gt) is appended resulting in b.gt.\n"
            "This would be equivalent to jg in amd64.\n\n"
        )
        print(
            "Please compute the sum of n consecutive quad words, where:\n"
            "\tX0 = memory address of the 1st quad word\n"
            "\tX1 = n (amount to loop for)\n\n"

            "set x0 to the sum computed\n\n"

            "We will now set the following in preparation for your code:\n"
            f"\t- [{hex(self.arr_addr)}:{hex(self.arr_addr + (self.arr_len * 8))}] = {{n qwords}}\n"
            f"\t- X0 = {hex(self.arr_addr)}\n"
            f"\t- X1 = {self.arr_len}\n"
        )

        print(
            "Constraints:\n"
            "\t- You are allowed six instructions\n"
        )

        print(
            "Hints:\n"
            "\t- Take advantage of pre/post indexing when possible.\n"
            "\t- Use values where they are.\n"
            "\t- Don't forget to place the result in x0.\n"
        )
    def trace(self):
        if len(self.asm) > 24:
            print(f"Maximum 6 aarch64 instructions allowed!  {len(self.asm)} bytes received, but expecting <=24!")
            return False

        try:
            self.emu.reg_write(UC_ARM64_REG_X0, self.arr_addr)
            self.emu.reg_write(UC_ARM64_REG_X1, self.arr_len)

            self.emu.mem_write(self.arr_addr - 0x4, struct.pack("<I", self.key))
            self.emu.mem_write(
                self.arr_addr, struct.pack(f"<{'q'*self.arr_len}", *self.data)
            )
            self.emu.mem_write(
                self.arr_addr + (self.arr_len * 8), struct.pack("<I", self.key)
            )

            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            print(f"PC: {hex(self.emu.reg_read(UC_ARM64_REG_PC))}")

        target = sum(self.data)
        correct = target == self.emu.reg_read(UC_ARM64_REG_X0)

        if not correct:
            print(
            f"""
            [!] ------------------------- [!]
            Failed test check:
            Input:
            X0 = {hex(self.arr_addr)}
            X1 = {self.arr_len}
            [{hex(self.arr_addr)}: = {[hex(i) for i in self.data]}

            Correct output:
            X0 = {hex(target)}

            Your output
            X0 = {hex(self.emu.reg_read(UC_ARM64_REG_X0))}
            [!] ------------------------- [!]
            """
            )
        return correct


class EmbryoARMPopPush(EmbryoARMBase):
    """
    Pop, Modify, Push
    """

    def __init__(self, asm=None, should_debug=False):
        super().__init__(asm)
        self.val_stk = [random.randint(1000000, 1000000000) for _ in range(8)]

    def print_level_text(self):
        print(
            "aarch64 does not have the push/pop instructions to work with the stack.\n"
            "Instead, you must use ldr and str to retrieve values from the stack.\n"
            "Fortunately, both ldr and str have the ability to increment the address passed in pre/post access.\n"
            "This feature can be used to perform the same action!\n\n"

            "popping the stack would be of the form:\n"
            "\tldr x1, [sp], #16\n\n"
            "This loads the value located at the stack pointer into register x1 and then adds 16 to the stack.\n\n"

            "Pushing to the stack would be of the form\n"
            "\tstr x1, [sp, #-16]!\n\n"
            "This places subtracts 16 from the stack pointer and then stores the value in x1 at sp.\n"

            "Note: In aarch64, the stack pointer must be 16 byte aligned!  Accessing the stack pointer when it is\n"
            "not properly aligned will result in a fault!\n\n"

            "Note: There is different syntax for accessing memory at an offset, pre-indexing, and post-indexing.\n"
            "All of these forms are used extensively in aarch64.\n"
        )

        print("Please pop 8 QWORDS from the stack, compute their average, and push the result back onto the stack.\n")

    def trace(self):
        try:
            print(self.val_stk)
            self.emu.mem_write(
                self.BASE_STACK + 0x200000 - 0x48, struct.pack("<QQQQQQQQ", *self.val_stk)
            )
            self.emu.reg_write(UC_ARM64_REG_SP, self.BASE_STACK + 0x200000 - 0x48)
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        if self.emu_err:
            print(self.emu_err)
            return False

        target = bytearray(struct.pack("<Q", (sum(self.val_stk) // 8)))
        sp = self.emu.reg_read(UC_ARM64_REG_SP)
        return target == self.emu.mem_read(sp, 8)

class EmbryoARMRegSwap(EmbryoARMBase):
    """
    Swap registers_use
    """

    def __init__(self, asm=None):
        super().__init__(asm)
        self.val_x0 = random.randint(1000000, 1000000000)
        self.val_x1 = random.randint(1000000, 1000000000)

    def print_level_text(self):
        print(
            "Swap values in X0 and X1.\n"
            "Example:\n"
            "\tIf starting with: X0 = 2 and X1 = 5\n"
            "\tThen end with:    X0 = 5 and X1 = 2\n\n"
        )

        print(
            "Constraints:\n"
            "- You may only use two instructions!\n\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"X0 = {hex(self.val_x0)}\n"
            f"X1 = {hex(self.val_x1)}\n\n"
        )
        print(
                "\n"
                "HINT: You have already used the necessary instructions in previous levels!"
        )

    def trace(self):
        if len(self.asm) > 8:
            print(f"Only submit two aarch64 instruction!  {len(self.asm)} bytes received, but expecting 8!")
            return False

        try:
            self.emu.reg_write(UC_ARM64_REG_X0, self.val_x0)
            self.emu.reg_write(UC_ARM64_REG_X1, self.val_x1)
            self.emu.emu_start(self.BASE_ADDR, self.BASE_ADDR + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        if self.emu_err:
            print(self.emu_err)
            return False

        correct = self.val_x0 == self.emu.reg_read(UC_ARM64_REG_X1)
        correct &= self.val_x1 == self.emu.reg_read(UC_ARM64_REG_X0)
        return correct


class EmbryoARMJumps(EmbryoARMBase):
    """
    Jump to provided code:
    1. relative jump
    2. absoulte jump
    """

    def __init__(self, asm=None):
        super().__init__(asm)
        self.CODE_OFFSET = random.randint(0x10, 0x100)
        self.code_load_addr = self.BASE_ADDR + self.CODE_OFFSET
        self.rel_off = 0x40
        self.val = random.randint(0x10, 0x100)

        self.traversed_bbs = []

        self.exit_key = random.randint(0, 0xFFFF)

        self.lib = pwnlib.asm.asm(
            f"""
            mov x0, #{self.exit_key}
            mov x8, #0x3c
            svc #1337
            """
        )

    def stop_hook(self, uc, address, size, user_data):
        x8 = uc.reg_read(UC_ARM64_REG_X8)
        if x8 == 0x3C:
            uc.emu_stop()

    def print_level_text(self):
        print(
            "In this level we will ask you to do both a relative jump and an absolute jump. You will do a relative\n"
            "jump first, then an absolute one. You will need to fill space in your code with something to make this\n"
            "relative jump possible.\n"
        )

        print(
            f"Using the above knowledge, perform the following:\n"
            f"\t1. Make the first instruction in your code a jmp\n"
            f"\t2. Make that jmp a relative jump to {hex(self.rel_off)} bytes from its current position\n"
            f"\t3. At {hex(self.rel_off)} write the following code:\n"
            f"\t4. Place the top value on the stack into register X1\n"
            f"\t5. jmp to the absolute address {hex(self.LIB_ADDR)}\n"
        )

        print(
            "We will now set the following in preparation for your code:\n"
            f"\t- Loading your given gode at: {hex(self.code_load_addr)}\n"
            f"\t- (stack) [{hex(self.RSP_INIT - 0x8)}] = {hex(self.val)}\n\n"
        )

    def hook_block(self, uc, address, size, user_data):
        self.traversed_bbs.append(address)

    def trace(self):
        self.emu.hook_add(
            UC_HOOK_CODE, self.stop_hook, begin=self.LIB_ADDR + len(self.lib)
        )

        self.emu.hook_add(UC_HOOK_BLOCK, self.hook_block, begin=self.code_load_addr)
        try:
            self.emu.reg_write(UC_ARM64_REG_SP, self.RSP_INIT - 0x10)
            self.emu.mem_write(self.RSP_INIT - 0x10, struct.pack("<Q", self.val))
            self.emu.mem_write(self.LIB_ADDR, self.lib)
            self.emu.emu_start(self.code_load_addr, self.code_load_addr + len(self.asm))
        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()
            return False

        correct_bb_order = [
            self.code_load_addr,
            self.code_load_addr + self.rel_off,
            self.LIB_ADDR,
        ]

        target = self.exit_key

        return (
            target == self.emu.reg_read(UC_ARM64_REG_X0)
            and correct_bb_order == self.traversed_bbs
            and self.val == self.emu.reg_read(UC_ARM64_REG_X1)
        )

class EmbryoARMAvg(EmbryoARMBase):
    def __init__(self, asm=None):
        super().__init__(asm)
        self.avg_count = random.randint(1, 100)
        self.val_stk = [random.randint(1000000, 1000000000) for _ in range(self.avg_count)]
        self.code_load_addr = self.BASE_ADDR + self.CODE_OFFSET

    def print_level_text(self):
        print(
            "Function calls in aarch64 are done with the branch and link instruction bl.\n"
            "The functions return value is stored in register x0.\n\n"

            "The bl instruction:\n"
            "\t- does a PC relative jump the specified location\n"
            "\t- and stores the return address in the link register lr (aka x30)\n\n"
            
            "It is the caller's responsibility to store the existing lr value frame pointer\n"
            "and any needed values in x0 - x15.\n\n"

            "Registers x16 - x18 will be discussed later.\n"
            "Registers x19 - x28 are callee saved.\n"
            "The saved return address is stored in a special link register lr (aka x30).\n"
            "The saved frame pointer is stored in a special frame register fr (aka x29).\n\n"

            "Given the role of x29 and x30, it is common to see a function prologue similar to:\n"
            "\tstp x29, x30, [sp, #-48]!\n"
            "\tmov x29, sp\n\n"

            "Here, the stack pointer is decremented to create a function frame and lr and fr are\n"
            "stored on the stack.  The last instruction shown sets the frame pointer.  Note that\n"
            "the stack pointer and frame pointer are equal in this case.  local variables are stored\n"
            "ABOVE the frame pointer.  The stack pointer may decrement further when passing arguments\n"
            "via the stack or for dynamic stack allocations (alloca).\n\n"

            "Similarly, a function epilogue consists of:\n"
            "\tldp x29, x30, [sp], #48\n"
            "\tret\n\n"

            "which restores lr, fr and the stack before returning.\n"

            "Write a function that calculates an average.\n"
            "Your assembly should be a FUNCTION that will be called, and is expected to return.\n"

            "Your function should be of the form calc_avg(ptr, count)\n"
            "where:\n"
            "- ptr is the start of the array\n"
            "- count is the number of 64 bit numbers in the array\n"
        )

    def unit_test_user_code(self):

        self.harness = pwnlib.asm.asm(f"""
                            mov x0, #{hex(self.BASE_STACK & 0xFFFF)}
                            movk x0, #{hex((self.BASE_STACK & 0xFFFF0000) >> 16)}, lsl 16
                            movk x0, #{hex((self.BASE_STACK & 0xFFFF00000000) >> 32)}, lsl 32
                            movk x0, #{hex((self.BASE_STACK & 0xFFFF000000000000) >> 48)}, lsl 48
                            mov x1, #{hex(self.avg_count)}
                            mov x3, #{hex(self.code_load_addr & 0xFFFF)}
                            movk x3, #{hex((self.code_load_addr & 0xFFFF0000) >> 16)}, lsl 16
                            blr x3
                            """)

        self.create_emu()

        try:
            self.emu.mem_write(
                self.BASE_STACK, struct.pack(f"<{'Q' * self.avg_count}", *self.val_stk)
            )

            self.emu.mem_write(self.LIB_ADDR, self.harness)
            self.emu.emu_start(self.LIB_ADDR, self.LIB_ADDR + len(self.harness))

        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        stack_fixed = self.emu.reg_read(UC_ARM64_REG_SP) == self.RSP_INIT

        def avg(arr):
            return int(sum(i for i in arr)/len(arr))


        val_x0 = self.emu.reg_read(UC_ARM64_REG_X0)
        correct = val_x0 == avg(self.val_stk) and stack_fixed

        if not correct:
            print(f"""nope, expected value {hex(avg(self.val_stk))} but got {hex(val_x0)}\n""")
            # mem = self.emu.mem_read(self.BASE_STACK, 64)
            # yep = [mem[i:i+8] for i in range(0, 64, 8)]
            # for i in yep: print(pwnlib.util.packing.u64(i))
            self.debug_output()
            print(f"values: {[hex(val) for val in self.val_stk]}")

        return correct

    def trace(self):
        for _ in range(100):
            if not self.unit_test_user_code():
                return False
        return True

class EmbryoARMFib(EmbryoARMBase):
    def __init__(self, asm=None):
        super().__init__(asm)
        self.code_load_addr = self.BASE_ADDR + self.CODE_OFFSET

    def print_level_text(self):
        print(
            "Function calls in aarch64 are done with the branch and link instruction bl.\n"
            "The functions return value is stored in register x0.\n\n"

            "The bl instruction:\n"
            "\t- does a PC relative jump the specified location\n"
            "\t- and stores the return address in the link register lr (aka x30)\n\n"
            
            "It is the caller's responsibility to store the existing lr value frame pointer\n"
            "and any needed values in x0 - x15.\n\n"

            "Registers x16 - x18 will be discussed later.\n"
            "Registers x19 - x28 are callee saved.\n"
            "The saved return address is stored in a special link register lr (aka x30).\n"
            "The saved frame pointer is stored in a special frame register fr (aka x29).\n\n"

            "Given the role of x29 and x30, it is common to see a function prologue similar to:\n"
            "\tstp x29, x30, [sp, #-48]!\n"
            "\tmov x29, sp\n\n"

            "Here, the stack pointer is decremented to create a function frame and lr and fr are\n"
            "stored on the stack.  The last instruction shown sets the frame pointer.  Note that\n"
            "the stack pointer and frame pointer are equal in this case.  local variables are stored\n"
            "ABOVE the frame pointer.  The stack pointer may decrement further when passing arguments\n"
            "via the stack or for dynamic stack allocations (alloca).\n\n"

            "Similarly, a function epilogue consists of:\n"
            "\tldp x29, x30, [sp], #48\n"
            "\tret\n\n"

            "which restores lr, fr and the stack before returning.\n"

            "Write a recursive fibonacci function.\n"
            "Your assembly should be a FUNCTION that will be called, and is expected to return.\n"

            "Your function should be of the form fib(pos)\n"
            "where:\n"
            "- pos is position in the fibonacci sequence\n"
        )

    def unit_test_user_code(self, fib_arg):

        # movk is not needed, but for completeness
        self.harness = pwnlib.asm.asm(f"""
                            mov x3, #{hex(self.code_load_addr & 0xFFFF)}
                            movk x3, #{hex((self.code_load_addr >> 16) & 0xFFFF)}, lsl 16
                            movk x3, #{hex((self.code_load_addr >> 32) & 0xFFFF)}, lsl 32
                            movk x3, #{hex((self.code_load_addr >> 48) & 0xFFFF)}, lsl 48
                            blr x3
                            """)

        self.create_emu()

        try:
            self.emu.reg_write(UC_ARM64_REG_X0, fib_arg)

            self.emu.mem_write(self.LIB_ADDR, self.harness)
            self.emu.emu_start(self.LIB_ADDR, self.LIB_ADDR + len(self.harness))

        except UcError as e:
            print("ERROR: %s" % e)
            self.debug_output()

        stack_fixed = self.emu.reg_read(UC_ARM64_REG_SP) == self.RSP_INIT

        def fib(n):
            if n <= 1:
                return n
            else:
                return fib(n - 1) + fib(n - 2)


        val_x0 = self.emu.reg_read(UC_ARM64_REG_X0)
        correct = val_x0 == fib(fib_arg) and stack_fixed

        if not correct:
            print(f"""nope, expected value {hex(fib(fib_arg))} but got {hex(val_x0)}\n""")
            self.debug_output()

        return correct

    def trace(self):
        for _ in range(100):
            fib_arg = random.randint(1, 30)
            if not self.unit_test_user_code(fib_arg):
                return False
        return True

if __name__ == "__main__":
    sel_level = LEVELS[level - 1]
    level = globals()[sel_level]()
    try:
        level.run()
    except KeyboardInterrupt:
        sys.exit(1)
