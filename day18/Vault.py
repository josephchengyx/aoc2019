from __future__ import annotations
from day10.Vector2D import Vector2D
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
    def is_movable(tile: str) -> bool:
        return tile in {Tile.OPEN, Tile.ENTRANCE} or Tile.is_door(tile) or Tile.is_key(tile)

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
        return str(tuple(self.keys))

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

    def what_changed_from(self, other: State) -> str | None:
        difference = set(self.keys - other.keys)
        return difference.pop() if difference else None


class Vault:
    def __init__(self, gridmap: list[list[str]]) -> None:
        self._map: Final[list[list[str]]] = gridmap
        self._key_locations: dict[str, Vector2D] = dict()
        self._entrance_location: Vector2D = Vector2D.zero()
        self._adjacency_list: dict[str, dict[str, tuple[int, State]]] = dict()
        self._find_entrance_and_keys()
        # self._generate_adjacency_list()

    def _find_entrance_and_keys(self) -> None:
        for y, row in enumerate(self._map):
            for x, tile in enumerate(row):
                if Tile.is_key(tile):
                    self._key_locations[tile] = Vector2D(x, y)
                elif tile == Tile.ENTRANCE:
                    self._entrance_location = Vector2D(x, y)

    @property
    def _x_bound(self) -> int:
        return len(self._map[0])

    @property
    def _y_bound(self) -> int:
        return len(self._map)

    @property
    def keys(self) -> list[str]:
        return list(self._key_locations.keys())

    @property
    def goal(self) -> State:
        return State.of(self.keys)

    def _is_in_bounds(self, point: Vector2D) -> bool:
        return 0 <= point.x < self._x_bound and 0 <= point.y < self._y_bound

    def _tile_at(self, point: Vector2D) -> str:
        if not self._is_in_bounds(point):
            return ''
        return self._map[point.y][point.x]

    def _location_of(self, item: str) -> Vector2D | None:
        if item == Tile.ENTRANCE:
            return self._entrance_location
        else:
            return self._key_locations.get(item, None)

    def _get_movable_locations(self, point: Vector2D) -> list[Vector2D]:
        return [neighbour for direction in Direction
                if Tile.is_movable(self._tile_at(neighbour := point + direction.vector))]

    def _bfs(self, start: str) -> None:
        start_position = self._location_of(start)
        if start_position is None:
            return

        queue: deque[tuple[Vector2D, int, State]] = deque()
        visited: set[Vector2D] = set()
        adjacent_keys: dict[str, tuple[int, State]] = dict()

        queue.append((start_position, 0, State.empty()))

        while queue:
            position, distance, keys_required = queue.popleft()
            visited.add(position)
            tile = self._tile_at(position)
            if Tile.is_key(tile) and tile != start:
                adjacent_keys[tile] = (distance, keys_required)
                continue
            elif Tile.is_door(tile):
                keys_required = keys_required.add_door(tile)
            for next_position in self._get_movable_locations(position):
                if next_position not in visited:
                    queue.append((next_position, distance + 1, keys_required))

        self._adjacency_list[start] = adjacent_keys

    def _generate_adjacency_list(self) -> None:
        for tile in [Tile.ENTRANCE] + self.keys:
            self._bfs(tile)

    def _get_accessible_keys(self, key: str, state: State) -> list[tuple[str, int]]:
        if key not in self._adjacency_list:
            self._bfs(key)
        adjacent_keys = self._adjacency_list.get(key, None)
        if adjacent_keys is None:
            return list()
        return [(key, distance) for key, (distance, keys_required) in adjacent_keys.items()
                if state.contains(keys_required)]

    @dataclass(order=True)
    class QueueItem:
        distance: int
        key: str = field(compare=False)
        state: State = field(compare=False)

        @property
        def items(self) -> tuple[int, str, State]:
            return self.distance, self.key, self.state

    def dijkstra(self) -> ShortestPathsResult:
        pqueue: list[Vault.QueueItem] = list()
        distances: dict[tuple[str, State], int] = dict()
        predecessors: dict[tuple[str, State], tuple[str, State]] = dict()

        heapq.heappush(pqueue, Vault.QueueItem(0, Tile.ENTRANCE, State.empty()))
        distances[(Tile.ENTRANCE, State.empty())] = 0
        predecessors[(Tile.ENTRANCE, State.empty())] = (Tile.ENTRANCE, State.empty())
        final_key_state = None

        while pqueue:
            distance, key, state = heapq.heappop(pqueue).items
            if state.contains(self.goal):
                final_key_state = (key, state)
                break
            for next_key, next_distance in self._get_accessible_keys(key, state):
                next_state = state.add_key(next_key)
                next_distance += distances.get((key, state), inf)
                if next_distance < distances.get((next_key, next_state), inf):
                    distances[(next_key, next_state)] = next_distance
                    predecessors[(next_key, next_state)] = (key, state)
                    heapq.heappush(pqueue, Vault.QueueItem(next_distance, next_key, next_state))

        return ShortestPathsResult(distances, predecessors, final_key_state)

    def get_map(self) -> list[list[str]]:
        return self._map


@dataclass(frozen=True)
class ShortestPathsResult:
    distances: dict[tuple[str, State], int]
    predecessors: dict[tuple[str, State], tuple[str, State]]
    final_key_state: tuple[str, State]

    @property
    def distance(self) -> int:
        return self.distances[self.final_key_state]

    @property
    def path(self) -> list[str]:
        path: list[str] = list()
        curr_key_state, prev_key_state = self.final_key_state, self.predecessors[self.final_key_state]
        while curr_key_state != prev_key_state:
            _, curr_state = curr_key_state
            _, prev_state = prev_key_state
            key = curr_state.what_changed_from(prev_state)
            if key is not None:
                path.append(key)
            curr_key_state, prev_key_state = prev_key_state, self.predecessors[prev_key_state]
        return path[::-1]