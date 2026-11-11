from __future__ import annotations
from IntCode.v3 import IntCodeComputer
from day10.Vector2D import Vector2D
from dataclasses import dataclass
from enum import Enum
from typing import Self, Optional, Final

class Direction(Enum):
    NORTH = (1, Vector2D(0, 1))
    SOUTH = (2, Vector2D(0, -1))
    WEST = (3, Vector2D(-1, 0))
    EAST = (4, Vector2D(1, 0))

    def __new__(cls, cmd: int, vector: Vector2D) -> Self:
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
    WALL = (0, '#', False)
    OPEN = (1, '.', True)
    O2_SYSTEM = (2, '*', True)

    def __new__(cls, status: int, item: str, is_movable: bool) -> Self:
        obj = object.__new__(cls)
        obj._value_ = status
        obj.item = item
        obj.is_movable = is_movable
        return obj


@dataclass(frozen=True)
class Path:
    steps: Final[tuple[Direction, ...]]

    @classmethod
    def empty(cls) -> Path:
        return cls(tuple())

    def depth(self) -> int:
        return len(self.steps)

    def add_step(self, step: Direction) -> Path:
        return Path(self.steps + (step,))

    def reverse(self) -> tuple[Direction, ...]:
        return tuple(step.opposite for step in self.steps[::-1])


class Droid:
    origin: Final[Vector2D] = Vector2D.zero()

    def __init__(self) -> None:
        self.position: Vector2D = Droid.origin
        self._map: dict[Vector2D, Location] = dict()
        self._computer: IntCodeComputer = IntCodeComputer()
        self._computer.configure_settings(await_further_input=True)
        self._map_x_min: int = 0  # inclusive
        self._map_x_max: int = 1  # exclusive
        self._map_y_min: int = 0  # inclusive
        self._map_y_max: int = 1  # exclusive

    def move(self, direction: Direction) -> None:
        new_position = self.position + direction.vector
        self._computer.put_input(direction.value)
        self._computer.run()
        status = self._computer.read_output().pop()
        self._update_map(new_position, Location(status))
        if Location(status).is_movable:
            self.position = new_position

    def backtrack(self, path: Path, num_steps: Optional[int] = None) -> None:
        reverse_path = path.reverse()
        if isinstance(num_steps, int):
            reverse_path = reverse_path[:num_steps]
        for direction in reverse_path:
            self.move(direction)

    def view_map(self) -> str:
        x_range, y_range = self._map_size()
        grid_map: list[list[str]] = [[' ' for x in range(x_range)] for y in range(y_range)]
        for position, location in self._map.items():
            x, y = tuple(self._to_map_coords(position))
            grid_map[y][x] = location.item
        x0, y0 = tuple(self._to_map_coords(Droid.origin))
        grid_map[y0][x0] = 'o'
        grid_map = grid_map[::-1]
        return '\n'.join(''.join(row) for row in grid_map)

    def _update_map(self, position: Vector2D, location: Location) -> None:
        self._map[position] = location
        x, y = tuple(position)
        if x < self._map_x_min:
            self._map_x_min = x
        elif x >= self._map_x_max:
            self._map_x_max = x + 1
        if y < self._map_y_min:
            self._map_y_min = y
        elif y >= self._map_y_max:
            self._map_y_max = y + 1

    def _map_size(self) -> tuple[int, int]:
        return self._map_x_max - self._map_x_min, self._map_y_max - self._map_y_min

    def _to_map_coords(self, position: Vector2D) -> Vector2D:
        return position - Vector2D(self._map_x_min, self._map_y_min)