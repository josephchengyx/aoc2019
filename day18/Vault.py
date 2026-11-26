from __future__ import annotations
from day10.Vector2D import Vector2D
from day15.Droid import Path
from day17.ASCII import Direction
from enum import StrEnum
from typing import Final
from collections import deque
from math import inf

class Vault:
    class Tile(StrEnum):
        WALL = '#'
        OPEN = '.'
        ENTRANCE = '@'

        @staticmethod
        def is_door(tile: str) -> bool:
            return tile.isupper()

        @staticmethod
        def is_key(tile: str) -> bool:
            return tile.islower()

        @staticmethod
        def is_poi(tile: str) -> bool:
            return tile == Vault.Tile.ENTRANCE or Vault.Tile.is_key(tile)

        @staticmethod
        def is_movable(tile: str) -> bool:
            return tile == Vault.Tile.OPEN or Vault.Tile.is_door(tile) or Vault.Tile.is_poi(tile)

    def __init__(self, gridmap: list[list[str]]) -> None:
        self._map: Final[list[list[str]]] = gridmap
        self._poi_locations: dict[str, Vector2D] = dict()
        self._find_poi_locations()

    def _find_poi_locations(self) -> None:
        for y, row in enumerate(self._map):
            for x, tile in enumerate(row):
                if Vault.Tile.is_poi(tile):
                    self._poi_locations[tile] = Vector2D(x, y)

    @property
    def _x_bound(self) -> int:
        return len(self._map[0])

    @property
    def _y_bound(self) -> int:
        return len(self._map)

    def _is_in_bounds(self, point: Vector2D) -> bool:
        return 0 <= point.x < self._x_bound and 0 <= point.y < self._y_bound

    def _tile_at(self, point: Vector2D) -> str:
        if not self._is_in_bounds(point):
            return ''
        return self._map[point.y][point.x]

    def _get_movable_directions(self, point: Vector2D) -> list[Direction]:
        return [direction for direction in Direction
                if Vault.Tile.is_movable(self._tile_at(point + direction.vector))]

    def bfs(self, start: Vector2D = None, max_depth: int = inf) -> dict[str, tuple[Path, tuple[str, ...]]]:
        if start is None:
            start = self._poi_locations[Vault.Tile.ENTRANCE]

        queue: deque[tuple[Vector2D, Path, tuple[str, ...]]] = deque()
        queue.append((start, Path.empty(), tuple()))
        visited: set[Vector2D] = set()
        keys_paths_and_requirements = dict()

        while queue:
            position, path_from_start, doors_required = queue.popleft()
            tile = self._tile_at(position)
            if Vault.Tile.is_door(tile):
                doors_required += (tile,)
            elif Vault.Tile.is_key(tile):
                keys_paths_and_requirements[tile] = (path_from_start, doors_required)
            visited.add(position)
            for direction in self._get_movable_directions(position):
                next_position = position + direction.vector
                next_path_from_start = path_from_start.add_step(direction)
                if next_position not in visited and next_path_from_start.length <= max_depth:
                    queue.append((next_position, next_path_from_start, doors_required))

        return keys_paths_and_requirements