from __future__ import annotations
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Final, Sequence
import re

@dataclass(unsafe_hash=True)
class Vector3D:
    x: Final[float]
    y: Final[float]
    z: Final[float]

    def __repr__(self) -> str:
        return f"({self.x},{self.y},{self.z})"

    def __add__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3D) -> Vector3D:
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self) -> Vector3D:
        return Vector3D(-self.x, -self.y, -self.z)

    def __mul__(self, scalar: float) -> Vector3D:
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Vector3D:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vector3D:
        return self.__mul__(1 / scalar)

    def dot(self, other: Vector3D) -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def transform(self, matrix: Sequence[Sequence[float]]) -> Vector3D:
        assert len(matrix) == 3 and all(len(row) == 3 for row in matrix), \
        "Matrix must be of shape (3, 3)"
        return Vector3D(*[self.dot(Vector3D(*row)) for row in matrix])

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z

    @staticmethod
    def zero() -> Vector3D:
        return Vector3D(0, 0, 0)

    @staticmethod
    def from_string(string: str) -> Vector3D:
        def parse(field: str) -> float | int:
            value = float(re.search(rf"{field}=(-?\d+\.?\d*)", string).group(1))
            return int(value) if value.is_integer() else value
        return Vector3D(*[parse(coordinate) for coordinate in 'xyz'])

    def norm(self) -> float:
        return self.dot(self)

    def normalize(self) -> Vector3D:
        return self / self.norm()

    def compare(self, other: Vector3D) -> Vector3D:
        def compare_coordinate(coordinate1: float, coordinate2: float) -> int:
            return int(coordinate1 < coordinate2) - int(coordinate1 > coordinate2)
        return Vector3D(
            compare_coordinate(self.x, other.x),
            compare_coordinate(self.y, other.y),
            compare_coordinate(self.z, other.z)
        )

    def energy(self) -> float:
        return sum(abs(coordinate) for coordinate in self)