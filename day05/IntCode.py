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
            assert len(address) == len(value), "Address and value must have same number of elements"
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
    def parse_opcode(opcode: int) -> tuple[int, list[int]]:
        instruction = opcode % 100
        param_modes: list[int] = list()
        match instruction:
            case 1 | 2 | 5 | 6 | 7 | 8:  # add, multiply, jump-if-true, jump-if-false, less than, equals
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
        memory_pointer, input_pointer = 0, 0
        while memory_pointer < len(self.memory):
            opcode = self.read_memory(memory_pointer)
            instruction, param_modes = self.parse_opcode(opcode)
            match instruction:
                case 1:  # add
                    param1, param2, param3 = self.read_memory(range(memory_pointer+1, memory_pointer+4))
                    mode1, mode2 = param_modes
                    value = self.read_param(param1, mode1) + self.read_param(param2, mode2)
                    self.set_memory(param3, value)
                    memory_pointer += 4
                case 2:  # multiply
                    param1, param2, param3 = self.read_memory(range(memory_pointer+1, memory_pointer+4))
                    mode1, mode2 = param_modes
                    value = self.read_param(param1, mode1) * self.read_param(param2, mode2)
                    self.set_memory(param3, value)
                    memory_pointer += 4
                case 3:  # input
                    param = self.read_memory(memory_pointer+1)
                    value = self.read_input(input_pointer)
                    self.set_memory(param, value)
                    memory_pointer += 2
                    input_pointer += 1
                case 4:  # output
                    param = self.read_memory(memory_pointer+1)
                    mode = param_modes[0]
                    value = self.read_param(param, mode)
                    self.write_output(value)
                    memory_pointer += 2
                case 5:  # jump-if-true
                    param1, param2 = self.read_memory(range(memory_pointer+1, memory_pointer+3))
                    mode1, mode2 = param_modes
                    if self.read_param(param1, mode1) != 0:
                        memory_pointer = self.read_param(param2, mode2)
                    else:
                        memory_pointer += 3
                case 6:  # jump-if-false
                    param1, param2 = self.read_memory(range(memory_pointer+1, memory_pointer+3))
                    mode1, mode2 = param_modes
                    if self.read_param(param1, mode1) == 0:
                        memory_pointer = self.read_param(param2, mode2)
                    else:
                        memory_pointer += 3
                case 7:  # less than
                    param1, param2, param3 = self.read_memory(range(memory_pointer+1, memory_pointer+4))
                    mode1, mode2 = param_modes
                    if self.read_param(param1, mode1) < self.read_param(param2, mode2):
                        self.set_memory(param3, 1)
                    else:
                        self.set_memory(param3, 0)
                    memory_pointer += 4
                case 8:  # equals
                    param1, param2, param3 = self.read_memory(range(memory_pointer+1, memory_pointer+4))
                    mode1, mode2 = param_modes
                    if self.read_param(param1, mode1) == self.read_param(param2, mode2):
                        self.set_memory(param3, 1)
                    else:
                        self.set_memory(param3, 0)
                    memory_pointer += 4
                case 99:  # halt
                    break
                case _:
                    raise ValueError(f"Unknown opcode {instruction}")