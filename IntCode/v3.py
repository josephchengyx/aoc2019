from typing import Sequence, Any, Final
from collections import deque
from copy import copy

class IntCodeComputer:
    version: Final[int] = 3
    _settings: dict[str, type] = {"pause_on_output": bool, "await_further_input": bool}
    _num_params_per_opcode: dict[int, int] = {1: 3, 2: 3, 3: 1, 4: 1, 5: 2, 6: 2, 7: 3, 8: 3, 9: 1, 99: 0}

    def __init__(self) -> None:
        # Internal states
        self._memory: list[int] = list()
        self._ext_memory: dict[int, int] = dict()
        self._pointer: int = 0
        self._relative_base: int = 0
        self._done: bool = False
        self._input: deque[int] = deque()
        self._output: deque[int] = deque()
        # User settings
        self._pause_on_output: bool = False
        self._await_further_input: bool = False

    def get_settings(self) -> dict[str, Any]:
        return {setting: getattr(self, f"_{setting}") for setting in IntCodeComputer._settings}

    def configure_settings(self, **kwargs: Any) -> None:
        for setting, value in kwargs.items():
            if setting not in IntCodeComputer._settings:
                raise KeyError(f"{setting} does not exist in settings")
            expected_type = IntCodeComputer._settings.get(setting)
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{setting} must be of type {expected_type.__name__}, got {type(value).__name__} instead"
                )
            setattr(self, f"_{setting}", value)

    def load_program(self, program: list[int]) -> None:
        self._memory = copy(program)

    def put_input(self, value: int | Sequence[int]) -> None:
        if isinstance(value, int):
            self._input.append(value)
        else:
            self._input.extend(value)

    def get_output(self) -> list[int]:
        return list(self._output)

    def is_done(self) -> bool:
        return self._done

    def reset(self) -> None:
        self._memory = list()
        self._ext_memory = dict()
        self._pointer = 0
        self._relative_base = 0
        self._done = False
        self._input = deque()
        self._output = deque()

    def _get_from_address(self, address: int) -> int:
        if address < 0: raise IndexError(f"Cannot read from invalid address {address}")
        elif address < len(self._memory):
            return self._memory[address]
        else:
            return self._ext_memory.get(address, 0)

    def _read_memory(self, address: int | Sequence[int]) -> int | list[int]:
        if isinstance(address, int):
            return self._get_from_address(address)
        else:
            return [self._get_from_address(addr) for addr in address]

    def _put_at_address(self, address: int, value: int) -> None:
        if address < 0: raise IndexError(f"Cannot write to invalid address {address}")
        elif address < len(self._memory):
            self._memory[address] = value
        else:
            self._ext_memory[address] = value

    def _write_memory(self, address: int | Sequence[int], value: int | Sequence[int]) -> None:
        if isinstance(address, int):
            self._put_at_address(address, value)
        else:
            assert len(address) == len(value), "Address and value must have same number of items"
            for addr, val in zip(address, value):
                self._put_at_address(addr, val)

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
        num_params = IntCodeComputer._num_params_per_opcode.get(instruction, 0)
        param_modes = [(opcode // (10 ** (i + 2))) % 10 for i in range(num_params)]
        return instruction, param_modes

    def _read_value(self, param: int, mode: int) -> int:
        match mode:
            # position mode
            case 0: return self._read_memory(param)
            # immediate mode
            case 1:  return param
            # relative mode
            case 2: return self._read_memory(param + self._relative_base)
            case _: raise ValueError(f"Unknown parameter mode {mode} for read operation")

    def _read_address(self, param: int, mode: int) -> int:
        match mode:
            # position mode
            case 0: return param
            # immediate mode
            case 1: raise ValueError(f"Invalid parameter mode {mode} for write operation")
            # relative mode
            case 2: return param + self._relative_base
            case _: raise ValueError(f"Unknown parameter mode {mode} for write operation")

    def run(self) -> None:
        while self._pointer < len(self._memory):
            opcode = self._read_memory(self._pointer)
            instruction, param_modes = IntCodeComputer._parse_opcode(opcode)
            match instruction:
                case 1:  # add
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2, mode3 = param_modes
                    value = self._read_value(param1, mode1) + self._read_value(param2, mode2)
                    address = self._read_address(param3, mode3)
                    self._write_memory(address, value)
                    self._pointer += 4
                case 2:  # multiply
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2, mode3 = param_modes
                    value = self._read_value(param1, mode1) * self._read_value(param2, mode2)
                    address = self._read_address(param3, mode3)
                    self._write_memory(address, value)
                    self._pointer += 4
                case 3:  # input
                    param = self._read_memory(self._pointer + 1)
                    mode, = param_modes
                    value = self._read_input()
                    address = self._read_address(param, mode)
                    if value is not None:
                        self._write_memory(address, value)
                        self._pointer += 2
                    elif self._await_further_input:
                        break
                    else:
                        raise RuntimeError("Not enough items in input to read from")
                case 4:  # output
                    param = self._read_memory(self._pointer + 1)
                    mode, = param_modes
                    value = self._read_value(param, mode)
                    self._write_output(value)
                    self._pointer += 2
                    if self._pause_on_output:
                        break
                case 5:  # jump-if-true
                    param1, param2 = self._read_memory(range(self._pointer + 1, self._pointer + 3))
                    mode1, mode2 = param_modes
                    value = self._read_value(param1, mode1)
                    address = self._read_value(param2, mode2)
                    if value != 0:
                        self._pointer = address
                    else:
                        self._pointer += 3
                case 6:  # jump-if-false
                    param1, param2 = self._read_memory(range(self._pointer + 1, self._pointer + 3))
                    mode1, mode2 = param_modes
                    value = self._read_value(param1, mode1)
                    address = self._read_value(param2, mode2)
                    if value == 0:
                        self._pointer = address
                    else:
                        self._pointer += 3
                case 7:  # less than
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2, mode3 = param_modes
                    value1, value2 = self._read_value(param1, mode1), self._read_value(param2, mode2)
                    address = self._read_address(param3, mode3)
                    if value1 < value2:
                        self._write_memory(address, 1)
                    else:
                        self._write_memory(address, 0)
                    self._pointer += 4
                case 8:  # equals
                    param1, param2, param3 = self._read_memory(range(self._pointer + 1, self._pointer + 4))
                    mode1, mode2, mode3 = param_modes
                    value1, value2 = self._read_value(param1, mode1), self._read_value(param2, mode2)
                    address = self._read_address(param3, mode3)
                    if value1 == value2:
                        self._write_memory(address, 1)
                    else:
                        self._write_memory(address, 0)
                    self._pointer += 4
                case 9:  # relative base offset
                    param = self._read_memory(self._pointer + 1)
                    mode, = param_modes
                    value = self._read_value(param, mode)
                    self._relative_base += value
                    self._pointer += 2
                case 99:  # halt
                    self._done = True
                    break
                case _:
                    raise ValueError(f"Unknown opcode {instruction}")