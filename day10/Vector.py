from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final, Sequence
from math import gcd, atan2, degrees

@dataclass(unsafe_hash=True)
class Vector2D:
    x: Final[int]
    y: Final[int]

    def __repr__(self) -> str:
        return f"({self.x},{self.y})"

    def __add__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2D) -> Vector2D:
        return Vector2D(self.x - other.x, self.y - other.y)

    def __neg__(self) -> Vector2D:
        return Vector2D(-self.x, -self.y)

    def __mul__(self, scalar: int) -> Vector2D:
        return Vector2D(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: int) -> Vector2D:
        return self.__mul__(scalar)

    def __floordiv__(self, scalar: int) -> Vector2D:
        return Vector2D(self.x // scalar, self.y // scalar)

    def dot(self, other: Vector2D) -> int:
        return self.x * other.x + self.y * other.y

    def det(self, other: Vector2D) -> int:
        return self.x * other.y - self.y * other.x

    def transform(self, matrix: Sequence[Sequence[int]]) -> Vector2D:
        assert len(matrix) == 2 and len(matrix[0]) == 2 and len(matrix[1]) == 2, \
        "Matrix must be of shape (2, 2)"
        return Vector2D(*[self.dot(Vector2D(*row)) for row in matrix])

    def __iter__(self) -> Iterator[int]:
        yield self.x
        yield self.y

    @staticmethod
    def zero() -> Vector2D:
        return Vector2D(0, 0)

    def normalize(self) -> Vector2D:
        norm = gcd(self.x, self.y)
        return self // norm

    def rotation_from(self, other: Vector2D) -> float:
        return degrees(atan2(-self.det(other), self.dot(other))) % 360

    def squared_euclidean_distance(self, other: Vector2D | None = None) -> int:
        if other is None:
            other = Vector2D.zero()
        return (self.x - other.x) ** 2 + (self.y - other.y) ** 2