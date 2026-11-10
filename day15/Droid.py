from __future__ import annotations
from IntCode.v3 import IntCodeComputer
from day10.Vector2D import Vector2D
from dataclasses import dataclass
from enum import Enum
from typing import Self, Final

class Direction(Enum):
    NORTH = (1, Vector2D(0, 1))
    SOUTH = (2, Vector2D(0, -1))
    WEST = (3, Vector2D(-1, 0))
    EAST = (4, Vector2D(1, 0))

    def __new__(cls, cmd, vector) -> Self:
        obj = object.__new__(cls)
        obj._value_ = cmd
        obj.vector = vector
        return obj

    @classmethod
    def from_vector(cls, vector: Vector2D) -> Self | None:
        for direction in cls:
            if direction.vector == vector:
                return direction
        return None

    @property
    def opposite(self) -> Self:
        return Direction.from_vector(-self.vector)


class Location(Enum):
    WALL = (0, '#')
    OPEN = (1, '.')
    O2_SYSTEM = (2, '*')

    def __new__(cls, status, char) -> Self:
        obj = object.__new__(cls)
        obj._value_ = status
        obj.char = char
        return obj


@dataclass(frozen=True)
class Path:
    steps: Final[tuple[Direction, ...]]

    @classmethod
    def empty(cls) -> Path:
        return cls(tuple())

    def add_step(self, step: Direction) -> Path:
        return Path(self.steps + (step,))

    def reverse(self) -> tuple[Direction, ...]:
        return tuple(Direction(cmd).opposite for cmd in self.steps)


class Droid:
    origin: Final[Vector2D] = Vector2D.zero()

    def __init__(self) -> None:
        self.position: Vector2D = Droid.origin
        self.map: dict[Vector2D, Location] = dict()
        self._computer: IntCodeComputer = IntCodeComputer()
        self._computer.configure_settings(await_further_input=True)

    def move(self, direction: Direction) -> None:
        new_position = self.position + direction.vector
        self._computer.put_input(direction.value)
        self._computer.run()
        status = self._computer.read_output().pop()
        self.map[new_position] = Location(status)
        if status in {Location.OPEN, Location.O2_SYSTEM}:
            self.position = new_position

    def move_along_path(self, path: Path) -> None:
        for direction in path.steps:
            self.move(direction)