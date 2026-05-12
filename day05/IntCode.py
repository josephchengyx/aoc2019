from typing import Sequence, Any
from collections import deque
from copy import copy

class IntCodeComputer:
    _settings: dict[str, type] = {"pause_on_output": bool, "await_further_input": bool}

    def __init__(self) -> None:
        # Internal states
        self._memory: list[int] = list()
        self._pointer: int = 0
        self._done: bool = False
        self._input: deque[int] = deque()
        self._output: deque[int] = deque()
        # User settings
        self._pause_on_output: bool = False
        self._await_further_input: bool = False

    def get_settings(self) -> dict[str, Any]:
        return {setting: getattr(self, f"_{setting}") for setting in self._settings}

    def configure_settings(self, **kwargs: Any) -> None:
        for setting, value in kwargs.items():
            if setting not in self._settings:
                raise KeyError(f"{setting} does not exist in settings")
            expected_type = self._settings.get(setting)
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{setting} must be of type {expected_type.__name__}, got {type(value).__name__} instead"
                )
            setattr(self, f"_{setting}", value)

    def read_program(self, program: list[int]) -> None:
        self._memory = copy(program)
        self._pointer = 0
        self._done = False

    def put_input(self, value: int | Sequence[int]) -> None:
        if isinstance(value, int):
            self._input.append(value)
        else:
            self._input.extend(value)

    def get_output(self) -> list[int]:
        return list(self._output)

    def is_done(self) -> bool:
        return self._done

    def clear_io(self) -> None:
        self._input = deque()
        self._output = deque()

    def _read_memory(self, address: int | Sequence[int]) -> int | list[int]:
        if isinstance(address, int):
            return self._memory[address]
        else:
            return [self._memory[addr] for addr in address]

    def _write_memory(self, address: int | Sequence[int], value: int | Sequence[int]) -> None:
        if isinstance(address, int):
            self._memory[address] = value
        else:
            assert len(address) == len(value), "Address and value must have same number of items"
            for addr, val in zip(address, value):
                self._memory[addr] = val

    def _read_input(self, num_items: int = 1) -> int | list[int] | None:
        assert isinstance(num_items, int) and num_items > 0, "Cannot read non-positive, non-integer number of items"
        if len(self._input) < num_items:
            return None
        if num_items == 1:
            return self._input.popleft()
        else:
            return [self._input.popleft() for _ in range(num_items)]

    def _write_output(self, value: int | Sequence[int]) -> None:
        if isinstance(value, int):
            self._output.append(value)
        else:
            self._output.extend(value)

    @staticmethod
    def _parse_opcode(opcode: int) -> tuple[int, list[int]]:
        instruction = opcode % 100
        param_modes: list[int] = list()
        match instruction:
            case 1 | 2 | 5 | 6 | 7 | 8:  # add, multiply, jump-if-true, jump-if-false, less than, equals
                param_modes = [(opcode // 100) % 10, (opcode // 1000) % 10]
            case 4:  # output
                param_modes = [opcode // 100]
        return instruction, param_modes

    def _read_param(self, param: int, mode: int) -> int:
        if mode == 1:  # immediate mode
            return param
        else:  # mode == 0, position mode
            return self._read_memory(param)

    def run(self) -> None:
        while self._pointer < len(self._memory):
            opcode = self._read_memory(self._pointer)
            instruction, param_modes = self._parse_opcode(opcode)
            match instruction:
                case 1:  # add
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2 = param_modes
                    value = self._read_param(param1, mode1) + self._read_param(param2, mode2)
                    self._write_memory(param3, value)
                    self._pointer += 4
                case 2:  # multiply
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2 = param_modes
                    value = self._read_param(param1, mode1) * self._read_param(param2, mode2)
                    self._write_memory(param3, value)
                    self._pointer += 4
                case 3:  # input
                    param = self._read_memory(self._pointer + 1)
                    value = self._read_input()
                    if value is not None:
                        self._write_memory(param, value)
                        self._pointer += 2
                    elif self._await_further_input:
                        break
                    else:
                        raise RuntimeError("Not enough items in input to read from")
                case 4:  # output
                    param = self._read_memory(self._pointer + 1)
                    mode = param_modes[0]
                    value = self._read_param(param, mode)
                    self._write_output(value)
                    self._pointer += 2
                    if self._pause_on_output:
                        break
                case 5:  # jump-if-true
                    param1, param2 = self._read_memory(range(self._pointer + 1, self._pointer + 3))
                    mode1, mode2 = param_modes
                    if self._read_param(param1, mode1) != 0:
                        self._pointer = self._read_param(param2, mode2)
                    else:
                        self._pointer += 3
                case 6:  # jump-if-false
                    param1, param2 = self._read_memory(range(self._pointer + 1, self._pointer + 3))
                    mode1, mode2 = param_modes
                    if self._read_param(param1, mode1) == 0:
                        self._pointer = self._read_param(param2, mode2)
                    else:
                        self._pointer += 3
                case 7:  # less than
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2 = param_modes
                    if self._read_param(param1, mode1) < self._read_param(param2, mode2):
                        self._write_memory(param3, 1)
                    else:
                        self._write_memory(param3, 0)
                    self._pointer += 4
                case 8:  # equals
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2 = param_modes
                    if self._read_param(param1, mode1) == self._read_param(param2, mode2):
                        self._write_memory(param3, 1)
                    else:
                        self._write_memory(param3, 0)
                    self._pointer += 4
                case 99:  # halt
                    self._done = True
                    break
                case _:
                    raise ValueError(f"Unknown opcode {instruction}")