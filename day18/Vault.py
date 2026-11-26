from __future__ import annotations
from day10.Vector2D import Vector2D
from day15.Droid import Path
from day17.ASCII import Direction
from enum import StrEnum
from dataclasses import dataclass
from typing import Final, Iterable
from collections import deque
import heapq
from math import inf

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
        return tile == Tile.ENTRANCE or Tile.is_key(tile)

    @staticmethod
    def is_movable(tile: str) -> bool:
        return tile == Tile.OPEN or Tile.is_door(tile) or Tile.is_poi(tile)

    @staticmethod
    def key_to(door: str) -> str:
        if not Tile.is_door(door):
            return ''
        return door.lower()

    @staticmethod
    def door_for(key: str) -> str:
        if not Tile.is_key(key):
            return ''
        return key.upper()


@dataclass(frozen=True)
class State:
    doors: tuple[str, ...]

    @classmethod
    def empty(cls) -> State:
        return cls(tuple())

    def __repr__(self) -> str:
        return str(self.doors)

    @property
    def length(self) -> int:
        return len(self.doors)

    def add_door(self, door: str) -> State:
        if not Tile.is_door(door):
            return self
        return State(self.doors + (door,))

    def add_key(self, key: str) -> State:
        return self.add_door(Tile.door_for(key))

    def meets_requirement(self, other: State) -> bool:
        return set(other.doors) <= set(self.doors)


class GridMap:
    def __init__(self, gridmap: list[list[str]]) -> None:
        self._map: Final[list[list[str]]] = gridmap
        self._poi_locations: dict[str, Vector2D] = dict()
        self._find_poi_locations()

    def _find_poi_locations(self) -> None:
        for y, row in enumerate(self._map):
            for x, tile in enumerate(row):
                if Tile.is_poi(tile):
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
        return [direction for direction in Direction if Tile.is_movable(self._tile_at(point + direction.vector))]

    def bfs(self, max_depth: int = inf) -> StateMap:
        queue: deque[tuple[Vector2D, Path, State]] = deque()
        queue.append((self._poi_locations[Tile.ENTRANCE], Path.empty(), State.empty()))
        visited: set[Vector2D] = set()
        paths_to_keys: dict[str, Path] = dict()
        requirements_per_key: dict[str, State] = dict()

        while queue:
            position, path_from_start, doors_required = queue.popleft()
            tile = self._tile_at(position)
            if Tile.is_door(tile):
                doors_required = doors_required.add_door(tile)
            elif Tile.is_key(tile):
                paths_to_keys[tile] = path_from_start
                requirements_per_key[tile] = doors_required
            visited.add(position)
            for direction in self._get_movable_directions(position):
                next_position = position + direction.vector
                next_path_from_start = path_from_start.add_step(direction)
                if next_position not in visited and next_path_from_start.length <= max_depth:
                    queue.append((next_position, next_path_from_start, doors_required))

        return StateMap(paths_to_keys, requirements_per_key)

    def get_map(self) -> list[list[str]]:
        return self._map


class StateMap:
    def __init__(self, paths: dict[str, Path], requirements: dict[str, State]) -> None:
        self._paths: Final[dict[str, Path]] = paths
        self._requirements: Final[dict[str, State]] = requirements

    @property
    def nodes(self) -> list[str]:
        return list(self._requirements.keys())

    def _distance_between(self, key1: str, key2: str) -> int:
        path_to_key1, path_to_key2 = self._paths.get(key1, Path.empty()), self._paths.get(key2, Path.empty())
        return (path_to_key1.reverse() + path_to_key2).length

    def _meets_requirement(self, state: State, node: str) -> bool:
        requirement = self._requirements.get(node, State.empty())
        return state.meets_requirement(requirement)

    def _get_accessible_nodes(self, state: State) -> list[str]:
        return [node for node in self.nodes if self._meets_requirement(state, node)]

    def dijkstra(self) -> None:
        pqueue: list[tuple[State, int]] = list()
        heapq.heappush(pqueue, (State.empty(), 0))
        pass

    def get_requirements(self) -> dict[str, State]:
        return self._requirements