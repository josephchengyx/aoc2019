from typing import Sequence
from copy import copy

class IntCodeComputer:
    def __init__(self) -> None:
        self.memory: list[int] = list()
        self.input: list[int] = list()
        self.output: list[int] = list()

    def read_program(self, program: list[int]) -> None:
        self.memory = copy(program)

    def set_memory(self, address: int | Sequence[int], value: int | Sequence[int]) -> None:
        if isinstance(address, int):
            self.memory[address] = value
        else:
            assert len(address) == len(value)
            for addr, val in zip(address, value):
                self.memory[addr] = val

    def read_memory(self, address: int | Sequence[int]) -> int | list[int]:
        if isinstance(address, int):
            return self.memory[address]
        else:
            return [self.memory[addr] for addr in address]

    def put_input(self, value: int | Sequence[int]) -> None:
        if isinstance(value, int):
            self.input.append(value)
        else:
            self.input.extend(value)

    def read_input(self, address: int | Sequence[int]) -> int | list[int]:
        if isinstance(address, int):
            return self.input[address]
        else:
            return [self.input[addr] for addr in address]

    def write_output(self, value: int | Sequence[int]) -> None:
        if isinstance(value, int):
            self.output.append(value)
        else:
            self.output.extend(value)

    def get_output(self) -> list[int]:
        return self.output

    @staticmethod
    def parse_opcode(opcode: int) -> tuple[int, list[int] | None]:
        instruction = opcode % 100
        param_modes = None
        match instruction:
            case 1 | 2:  # add, multiply
                param_modes = [(opcode // 100) % 10, (opcode // 1000) % 10]
            case 4:  # output
                param_modes = [opcode // 100]
        return instruction, param_modes

    def read_param(self, param: int, mode: int) -> int:
        if mode == 1:  # immediate mode
            return param
        else:  # mode == 0, position mode
            return self.read_memory(param)

    def run(self) -> None:
        mem_pointer, inp_pointer = 0, 0
        while mem_pointer < len(self.memory):
            opcode = self.read_memory(mem_pointer)
            instruction, param_modes = self.parse_opcode(opcode)
            match instruction:
                case 1:  # add
                    param1, param2, param3 = self.read_memory(range(mem_pointer+1, mem_pointer+4))
                    mode1, mode2 = param_modes
                    value = self.read_param(param1, mode1) + self.read_param(param2, mode2)
                    self.set_memory(param3, value)
                    mem_pointer += 4
                case 2:  # multiply
                    param1, param2, param3 = self.read_memory(range(mem_pointer+1, mem_pointer+4))
                    mode1, mode2 = param_modes
                    value = self.read_param(param1, mode1) * self.read_param(param2, mode2)
                    self.set_memory(param3, value)
                    mem_pointer += 4
                case 3:  # input
                    param = self.read_memory(mem_pointer+1)
                    value = self.read_input(inp_pointer)
                    self.set_memory(param, value)
                    mem_pointer += 2
                    inp_pointer += 1
                case 4:  # output
                    param = self.read_memory(mem_pointer+1)
                    mode = param_modes[0]
                    value = self.read_param(param, mode)
                    self.write_output(value)
                    mem_pointer += 2
                case 99:  # halt
                    break