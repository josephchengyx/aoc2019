from __future__ import annotations
from dataclasses import dataclass
from typing import Final
import re

@dataclass
class Coordinate2D:
    x: Final[int]
    y: Final[int]

    def __repr__(self) -> str:
        return f"({self.x},{self.y})"

    def __add__(self, other: Coordinate2D) -> Coordinate2D:
        return Coordinate2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Coordinate2D) -> Coordinate2D:
        return Coordinate2D(self.x - other.x, self.y - other.y)

    def __neg__(self) -> Coordinate2D:
        return Coordinate2D(-self.x, -self.y)

    @staticmethod
    def zero() -> Coordinate2D:
        return Coordinate2D(0, 0)

    @staticmethod
    def from_path(path: str) -> Coordinate2D | None:
        direction, distance = re.match(r"([UDLR])(\d+)", path).groups()
        distance = int(distance)
        match direction:
            case "U":
                return Coordinate2D(0, distance)
            case "D":
                return Coordinate2D(0, -distance)
            case "L":
                return Coordinate2D(-distance, 0)
            case "R":
                return Coordinate2D(distance, 0)
            case _:
                return None

    def manhattan_distance(self, other: Coordinate2D | None = None) -> int:
        if other is None:
            other = Coordinate2D.zero()
        return abs(self.x - other.x) + abs(self.y - other.y)


@dataclass
class Line2D:
    start: Final[Coordinate2D]
    end: Final[Coordinate2D]

    def __repr__(self) -> str:
        return f"{self.start}-{self.end}"

    @staticmethod
    def from_point_and_path(point: Coordinate2D, path: str) -> Line2D:
        start = point
        end = point + Coordinate2D.from_path(path)
        return Line2D(start, end)

    def is_horizontal(self) -> bool:
        return self.start.y == self.end.y

    def is_vertical(self) -> bool:
        return self.start.x == self.end.x

    def is_orthogonal_to(self, other: Line2D) -> bool:
        return (self.is_horizontal() and other.is_vertical()) \
            or (self.is_vertical() and other.is_horizontal())

    def get_x_bounds(self) -> tuple[int, int]:
        return min(self.start.x, self.end.x), max(self.start.x, self.end.x)

    def get_y_bounds(self) -> tuple[int, int]:
        return min(self.start.y, self.end.y), max(self.start.y, self.end.y)

    def get_intersection_with(self, other: Line2D) -> Coordinate2D | None:
        # note: does not count intersection at bounds
        if self.is_orthogonal_to(other):
            if self.is_horizontal():
                y_min, y_max = other.get_y_bounds()
                x_min, x_max = self.get_x_bounds()
                if y_min < self.start.y < y_max and x_min < other.start.x < x_max:
                    return Coordinate2D(other.start.x, self.start.y)
            elif self.is_vertical():
                x_min, x_max = other.get_x_bounds()
                y_min, y_max = self.get_y_bounds()
                if x_min < self.start.x < x_max and y_min < other.start.y < y_max:
                    return Coordinate2D(self.start.x, other.start.y)
        return None

    def contains_point(self, point: Coordinate2D) -> bool:
        # note: does count boundary points
        if self.is_horizontal() and point.y == self.start.y:
            x_min, x_max = self.get_x_bounds()
            return x_min <= point.x <= x_max and point.y == self.start.y
        elif self.is_vertical() and point.x == self.start.x:
            y_min, y_max = self.get_y_bounds()
            return y_min <= point.y <= y_max and point.x == self.start.x
        return False

    def length(self) -> int:
        return self.end.manhattan_distance(self.start)

    def length_up_to_point(self, point: Coordinate2D) -> int:
        if self.contains_point(point):
            return point.manhattan_distance(self.start)
        return 0