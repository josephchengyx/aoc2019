from typing import Sequence
from copy import copy

class IntCodeComputer:
    def __init__(self) -> None:
        self.memory: list[int] = list()

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

    def run(self) -> None:
        pointer = 0
        while pointer < len(self.memory):
            opcode = self.read_memory(pointer)
            match opcode:
                case 1:
                    param1, param2, param3 = self.read_memory(range(pointer+1, pointer+4))
                    value = self.read_memory(param1) + self.read_memory(param2)
                    self.set_memory(param3, value)
                case 2:
                    param1, param2, param3 = self.read_memory(range(pointer+1, pointer+4))
                    value = self.read_memory(param1) * self.read_memory(param2)
                    self.set_memory(param3, value)
                case 99:
                    break
            pointer += 4