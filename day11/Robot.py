from IntCode.v3 import IntCodeComputer
from day10.Vector2D import Vector2D
from typing import Final

class Robot:
    _right_rotation: Final = ((0, 1), (-1, 0))
    _left_rotation: Final = ((0, -1), (1, 0))

    def __init__(self):
        self._position: Vector2D = Vector2D.zero()
        self._heading: Vector2D = Vector2D(0, 1)
        self._computer: IntCodeComputer = IntCodeComputer()
        self._computer.configure_settings(pause_on_output=True)
        self._program: list[int] = list()
        self._done: bool = False

    def load_program(self, program: list[int]) -> None:
        self._program = program
        self._computer.load_program(self._program)

    def restart(self) -> None:
        self._computer.reset()
        self._computer.load_program(self._program)
        self._done = False
        self._position: Vector2D = Vector2D.zero()
        self._heading: Vector2D = Vector2D(0, 1)

    def get_position(self) -> Vector2D:
        return self._position

    def scan_panel(self, colour: int) -> None:
        self._computer.put_input(colour)

    def step(self) -> int | None:
        for _ in range(2):
            self._computer.run()
        self._done = self._computer.is_done()
        if self._done:
            return None
        else:
            colour, turn_direction = self._computer.read_output()
            self._turn(turn_direction)
            self._move()
            return colour

    def is_done(self) -> bool:
        return self._done

    def _turn(self, direction: int) -> None:
        match direction:
            case 0:
                self._heading = self._heading.transform(Robot._left_rotation)
            case 1:
                self._heading = self._heading.transform(Robot._right_rotation)

    def _move(self) -> None:
        self._position += self._heading