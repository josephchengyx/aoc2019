from __future__ import annotations
from IntCode.v3 import IntCodeComputer
from day10.Vector2D import Vector2D
from dataclasses import dataclass
from enum import Enum
from collections import deque
from math import inf
from functools import reduce
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
    O2_SYSTEM = (2, 'x', True)

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

    @property
    def length(self) -> int:
        return len(self.steps)

    def __add__(self, other: Path) -> Path:
        steps = self.steps + other.steps
        return Path(steps).reduce()

    def add_step(self, step: Direction) -> Path:
        return Path(self.steps + (step,))

    def remove_step(self, num_steps: int = 1) -> Path:
        return Path(self.steps[:-num_steps])

    def reverse(self) -> Path:
        return Path(tuple(step.opposite for step in self.steps[::-1]))

    def destination(self) -> Vector2D:
        return reduce(lambda vec1, vec2: vec1 + vec2, map(lambda step: step.vector, self.steps))

    def reduce(self) -> Path:
        stack: list[Direction] = list()
        for step in self.steps:
            if stack and stack[-1] is step.opposite:
                stack.pop()
            else:
                stack.append(step)
        return Path(tuple(stack))


class Droid:
    origin: Final[Vector2D] = Vector2D.zero()

    def __init__(self) -> None:
        self.position: Vector2D = Droid.origin
        self._computer: IntCodeComputer = IntCodeComputer()
        self._computer.configure_settings(await_further_input=True)
        self._program: list[int] = list()
        self._map: dict[Vector2D, Location] = dict()
        self._paths: dict[Vector2D, Path] = dict()
        self._map_x_min: int = 0  # inclusive
        self._map_y_min: int = 0  # inclusive
        self._map_x_max: int = 1  # exclusive
        self._map_y_max: int = 1  # exclusive

    def load_program(self, program: list[int]) -> None:
        self._program = program
        self._computer.load_program(self._program)

    def restart(self) -> None:
        self._computer.reset()
        self._computer.load_program(self._program)
        self.position = Droid.origin
        self._map = dict()
        self._map_x_min = 0
        self._map_y_min = 0
        self._map_x_max = 1
        self._map_y_max = 1

    def bfs(self, max_depth: Optional[int] = inf) -> None:
        queue: deque[tuple[Vector2D, Path]] = deque()
        queue.append((self.position, Path.empty()))
        path_to_start = Path.empty()
        while queue:
            position, path_from_start = queue.popleft()
            self._traverse(path_to_start + path_from_start)
            if self.position != position:  # encountered a Location.WALL
                path_from_start = path_from_start.remove_step()
            else:
                self._paths[position] = path_from_start
                for direction in Direction:
                    new_position = position + direction.vector
                    new_path_from_start = path_from_start.add_step(direction)
                    if new_position not in self._map and new_path_from_start.length <= max_depth:
                        queue.append((new_position, new_path_from_start))
            path_to_start = path_from_start.reverse()
        self._traverse(path_to_start)

    def get_path_to_position(self, position: Vector2D) -> Path | None:
        return self._paths.get(position, None)

    def get_o2_system_position(self) -> Vector2D | None:
        for position, location in self._map.items():
            if location is Location.O2_SYSTEM:
                return position
        return None

    def get_max_path_length(self) -> int:
        max_length = 0
        for position, path in self._paths.items():
            if path.length > max_length:
                max_length = path.length
        return max_length

    def move_to(self, position: Vector2D) -> None:
        path = self.get_path_to_position(position)
        if path is not None:
            self._traverse(path)
            self._update_paths()

    def view_map(self) -> str:
        x_range, y_range = self._map_size()
        grid_map: list[list[str]] = [['#' for x in range(x_range)] for y in range(y_range)]
        for position, location in self._map.items():
            x, y = tuple(self._to_map_coords(position))
            grid_map[y][x] = location.item
        x0, y0 = tuple(self._to_map_coords(Droid.origin))
        grid_map[y0][x0] = 'o'
        grid_map = grid_map[::-1]
        return '\n'.join(' '.join(row) for row in grid_map)

    def _traverse(self, path: Path, num_steps: Optional[int] = None) -> None:
        path = path.steps
        if num_steps is not None:
            path = path[:num_steps]
        for direction in path:
            self._move(direction)

    def _move(self, direction: Direction) -> None:
        new_position = self.position + direction.vector
        self._computer.put_input(direction.value)
        self._computer.run()
        status = self._computer.read_output().pop()
        self._update_map(new_position, Location(status))
        if Location(status).is_movable:
            self.position = new_position

    def _update_map(self, position: Vector2D, location: Location) -> None:
        if position in self._map:
            return
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

    def _update_paths(self) -> None:
        offset = self.get_path_to_position(self.position)
        if offset is None or offset.length == 0:
            return
        offset = offset.reverse()
        for position, path in list(self._paths.items()):
            self._paths[position] = offset + path

    def _map_size(self) -> tuple[int, int]:
        return self._map_x_max - self._map_x_min, self._map_y_max - self._map_y_min

    def _to_map_coords(self, position: Vector2D) -> Vector2D:
        return position - Vector2D(self._map_x_min, self._map_y_min)