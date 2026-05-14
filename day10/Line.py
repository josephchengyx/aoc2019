from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final
from math import gcd

@dataclass(unsafe_hash=True)
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

    def __mul__(self, scalar: int) -> Coordinate2D:
        return Coordinate2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: int) -> Coordinate2D:
        return self.__mul__(scalar)

    def __floordiv__(self, scalar: int) -> Coordinate2D:
        return Coordinate2D(self.x // scalar, self.y // scalar)

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y

    @staticmethod
    def zero() -> Coordinate2D:
        return Coordinate2D(0, 0)

    def as_tuple(self) -> tuple[int, int]:
        return self.x, self.y


@dataclass
class Line2D:
    start: Final[Coordinate2D]
    end: Final[Coordinate2D]

    def __repr__(self) -> str:
        return f"{self.start}-{self.end}"

    def unit_vector(self) -> Coordinate2D:
        direction = self.end - self.start
        norm = gcd(direction.x, direction.y)
        return direction // norm

    def get_points(self) -> set[Coordinate2D]:
        # not including boundary points
        points: set[Coordinate2D] = set()
        direction = self.unit_vector()
        current_point = self.start + direction
        while current_point != self.end:
            points.add(current_point)
            current_point += direction
        return points

    def contains_point(self, point: Coordinate2D) -> bool:
        points = self.get_points()
        return point in points