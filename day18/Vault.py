from __future__ import annotations
from day10.Vector2D import Vector2D
from day15.Droid import Path
from day17.ASCII import Direction
from enum import StrEnum
from dataclasses import dataclass, field
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
    keys: frozenset[str]

    @classmethod
    def empty(cls) -> State:
        return cls(frozenset())

    @classmethod
    def of(cls, items: str | Iterable[str]) -> State:
        if isinstance(items, str): items = [items]
        keys = frozenset([item if Tile.is_key(item) else Tile.key_to(item) for item in items])
        return cls(keys)

    def __repr__(self) -> str:
        return str(self.keys)

    @property
    def length(self) -> int:
        return len(self.keys)

    def add_key(self, key: str) -> State:
        if not Tile.is_key(key):
            return self
        return State(self.keys | {key})

    def add_door(self, key: str) -> State:
        return self.add_key(Tile.key_to(key))

    def contains(self, other: State | str | Iterable[str]) -> bool:
        if not isinstance(other, State):
            other = State.of(other)
        return other.keys <= self.keys

    def what_changed_from(self, other: State) -> str:
        item, = self.keys - other.keys
        return item


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

    def bfs(self) -> StateMap:
        queue: deque[tuple[Vector2D, Path, State]] = deque()
        visited: set[Vector2D] = set()
        paths_to_keys: dict[str, Path] = dict()
        requirements_per_key: dict[str, State] = dict()

        queue.append((self._poi_locations[Tile.ENTRANCE], Path.empty(), State.empty()))

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
                if next_position not in visited:
                    queue.append((next_position, next_path_from_start, doors_required))

        return StateMap(paths_to_keys, requirements_per_key)

    def get_map(self) -> list[list[str]]:
        return self._map


class StateMap:
    def __init__(self, paths: dict[str, Path], requirements: dict[str, State]) -> None:
        self._paths_to_keys: Final[dict[str, Path]] = paths
        self._distance_between_keys: dict[frozenset[str], int] = dict()
        self._requirements: Final[dict[str, State]] = requirements

    @property
    def keys(self) -> list[str]:
        return list(self._requirements.keys())

    @property
    def goal(self) -> State:
        return State.of(self.keys)

    def _distance_between(self, key1: str, key2: str) -> int:
        key_pair = frozenset((key1, key2))
        if key_pair not in self._distance_between_keys:
            path_to_key1 = self._paths_to_keys.get(key1, Path.empty())
            path_to_key2 = self._paths_to_keys.get(key2, Path.empty())
            self._distance_between_keys[key_pair] = (path_to_key1.reverse() + path_to_key2).length
        return self._distance_between_keys[key_pair]

    def _meets_requirement(self, state: State, key: str) -> bool:
        requirement = self._requirements.get(key, State.empty())
        return state.contains(requirement)

    def _get_accessible_keys(self, state: State) -> list[str]:
        return [key for key in self.keys if self._meets_requirement(state, key)]

    @dataclass(order=True)
    class QueueItem:
        distance: int
        key: str = field(compare=False)
        state: State = field(compare=False)

        @property
        def items(self) -> tuple[int, str, State]:
            return self.distance, self.key, self.state

    def dijkstra(self) -> tuple[dict[State, int], dict[State, State]]:
        pqueue: list[StateMap.QueueItem] = list()
        distances: dict[State, int] = dict()
        predecessors: dict[State, State] = dict()

        heapq.heappush(pqueue, StateMap.QueueItem(0, Tile.ENTRANCE, State.empty()))
        distances[State.empty()] = 0
        predecessors[State.empty()] = State.empty()

        while pqueue:
            distance, key, state = heapq.heappop(pqueue).items
            if state == self.goal:
                break
            for next_key in self._get_accessible_keys(state):
                next_state = state.add_key(next_key)
                next_distance = distances[state] + self._distance_between(key, next_key)
                if not state.contains(next_key):
                    heapq.heappush(pqueue, StateMap.QueueItem(next_distance, next_key, next_state))
                if next_distance < distances.get(next_state, inf):
                    distances[next_state] = next_distance
                    predecessors[next_state] = state

        return distances, predecessors

    def reconstruct_path(self, predecessors: dict[State, State]) -> list[str]:
        path: list[str] = list()
        curr_state, prev_state = self.goal, predecessors[self.goal]
        while curr_state != prev_state:
            key = curr_state.what_changed_from(prev_state)
            path.append(key)
            curr_state, prev_state = prev_state, predecessors[prev_state]
        return path[::-1]

    def get_requirements(self) -> dict[str, State]:
        return self._requirements