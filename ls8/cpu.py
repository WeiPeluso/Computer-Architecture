"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CMP = 0b10100111
JMP = 0b01010100
JNE = 0b01010110
JEQ = 0b01010101
CALL = 0b01010000
RET = 0b00010001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        self.running = False
        self.ram = [0] * 255
        self.registers = [0] * 8
        self.flag = [0] * 8
        self.flag_lt = 5
        self.flag_gt = 6
        self.flag_equal = 7
        self.SP = 7

    def ram_read(self, position):
        return self.ram[position]

    def ram_write(self, position, command):
        self.ram[position] = command

    def load(self, file):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]
        try:
            with open(file) as f:
                for line in f:
                    t = line.split('#')
                    n = t[0].strip()
                    if n == "":
                        continue
                    command = int(n, 2)
                    self.ram[address] = command
                    address += 1
        except FileNotFoundError:
            print(f"File not found: {file}")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        self.running = True
        while self.running:
            op = self.ram_read(self.pc)
            op_len = ((op & 0b11000000) >> 6) + 1
            if op == HLT:
                self.running = False
            elif op == LDI:
                reg_num = self.ram[self.pc + 1]
                value = self.ram[self.pc + 2]
                self.registers[reg_num] = value

            elif op == PRN:
                reg_num = self.ram[self.pc + 1]
                print(self.registers[reg_num])
            elif op == MUL:
                operand_a = self.ram[self.pc + 1]
                operand_b = self.ram[self.pc+2]
                self.registers[operand_a] *= self.registers[operand_b]
            elif op == PUSH:
                self.registers[self.SP] -= 1
                reg_num = self.ram[self.pc + 1]
                value = self.registers[reg_num]
                top_of_stack_addr = self.registers[self.SP]
                self.ram[top_of_stack_addr] = value
            elif op == POP:
                reg_num = self.ram[self.pc + 1]
                top_of_stack_addr = self.registers[SP]
                value = self.ram[top_of_stack_addr]
                self.registers[reg_num] = value
                self.registers[self.SP] += 1
            elif op == CALL:
                reg_num = self.ram[self.pc + 1]
                return_address = self.pc + 2
                self.registers[self.SP] -= 1
                self.ram[self.registers[self.SP]] = return_address
                subroutin_address = self.registers[reg_num]
                self.pc = subroutin_address
            elif op == RET:
                top_of_stack_addr = self.registers[self.SP]
                value = self.ram[top_of_stack_addr]
                self.registers[0] = value
                self.registers[self.SP] += 1
                self.pc = self.registers[0]
            elif op == JMP:
                reg_num = self.ram[self.pc + 1]
                self.pc = self.registers[reg_num]
            elif op == JEQ:
                reg_num = self.ram[self.pc + 1]
                if self.flag[self.flag_equal] == 1:
                    self.pc = self.registers[reg_num]
                else:
                    self.pc += 2
            elif op == JNE:
                reg_num = self.ram[self.pc+1]
                if self.flag[self.flag_equal] == 0:
                    self.pc = self.registers[reg_num]
                else:
                    self.pc += 2
            elif op == CMP:
                operand_a = self.ram[self.pc + 1]
                operand_b = self.ram[self.pc + 2]

                if self.registers[operand_a] == self.registers[operand_b]:
                    self.flag[self.flag_equal] = 1

                elif self.registers[operand_a] < self.registers[operand_b]:
                    self.flag[self.flag_lt] = 1

                elif self.registers[operand_a] > self.registers[operand_b]:
                    self.flag[self.flag_gt] = 1

                else:
                    self.flag[self.flag_lt] = 0
                    self.flag[self.flag_gt] = 0
                    self.flag[self.flag_equal] = 0
            if not (op == JEQ or op == JNE or op == JMP or op == CALL or op == RET):
                self.pc += op_len
