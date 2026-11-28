from __future__ import annotations
from day10.Vector2D import Vector2D
from day17.ASCII import Direction
from enum import StrEnum
from dataclasses import dataclass, field
from typing import Final, Iterable, Iterator
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
    def is_entrance(tile: str) -> bool:
        return Tile.ENTRANCE in tile

    @staticmethod
    def is_movable(tile: str) -> bool:
        return tile == Tile.OPEN or Tile.is_door(tile) or Tile.is_key(tile) or Tile.is_entrance(tile)

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
class LocationState:
    tiles: tuple[str, ...]

    @classmethod
    def of(cls, items: str | Iterable[str]) -> LocationState:
        if isinstance(items, str):
            return cls((items,))
        return cls(tuple(items))

    def __iter__(self) -> Iterator[str]:
        return iter(self.tiles)

    def set(self, idx: int, tile: str) -> LocationState:
        if idx < 0 or idx >= len(self.tiles):
            return self
        return LocationState(self.tiles[:idx] + (tile,) + self.tiles[idx+1:])


@dataclass(frozen=True)
class KeyState:
    keys: frozenset[str]

    @classmethod
    def empty(cls) -> KeyState:
        return cls(frozenset())

    @classmethod
    def of(cls, items: str | Iterable[str]) -> KeyState:
        if isinstance(items, str): items = [items]
        keys = frozenset([item if Tile.is_key(item) else Tile.key_to(item) for item in items])
        return cls(keys)

    def __repr__(self) -> str:
        return str(tuple(self.keys))

    @property
    def length(self) -> int:
        return len(self.keys)

    def add_keys(self, items: str | Iterable[str]) -> KeyState:
        if isinstance(items, str):
            items = {items}
        items = {item if Tile.is_key(item) else Tile.key_to(item)
                 for item in items
                 if Tile.is_key(item) or Tile.is_door(item)}
        return KeyState(self.keys | items)

    def contains(self, other: KeyState | str | Iterable[str]) -> bool:
        if not isinstance(other, KeyState):
            other = KeyState.of(other)
        return other.keys <= self.keys

    def difference_from(self, other: KeyState) -> str | None:
        difference = set(self.keys - other.keys)
        return difference.pop() if difference else None


class Vault:
    def __init__(self, gridmap: list[list[str]]) -> None:
        self._map: Final[list[list[str]]] = gridmap
        self._key_positions: dict[str, Vector2D] = dict()
        self._entrance_positions: dict[str, Vector2D] = dict()
        self._adjacency_list: dict[str, dict[str, tuple[int, KeyState]]] = dict()
        self._find_entrance_and_keys()
        self._generate_adjacency_list()

    def _find_entrance_and_keys(self) -> None:
        num_entrances = 0
        for y, row in enumerate(self._map):
            for x, tile in enumerate(row):
                if Tile.is_key(tile):
                    self._key_positions[tile] = Vector2D(x, y)
                elif tile == Tile.ENTRANCE:
                    num_entrances += 1
                    tile += str(num_entrances)
                    self._entrance_positions[tile] = Vector2D(x, y)

    @property
    def _x_bound(self) -> int:
        return len(self._map[0])

    @property
    def _y_bound(self) -> int:
        return len(self._map)

    @property
    def keys(self) -> list[str]:
        return list(self._key_positions.keys())

    @property
    def entrances(self) -> list[str]:
        return list(self._entrance_positions.keys())

    @property
    def goal(self) -> KeyState:
        return KeyState.of(self.keys)

    def _is_in_bounds(self, point: Vector2D) -> bool:
        return 0 <= point.x < self._x_bound and 0 <= point.y < self._y_bound

    def _tile_at(self, point: Vector2D) -> str:
        if not self._is_in_bounds(point):
            return ''
        return self._map[point.y][point.x]

    def _position_of(self, tile: str) -> Vector2D | None:
        if Tile.is_key(tile):
            return self._key_positions.get(tile, None)
        elif Tile.is_entrance(tile):
            return self._entrance_positions.get(tile, None)
        return None

    def _get_movable_positions(self, point: Vector2D) -> list[Vector2D]:
        return [neighbour for direction in Direction
                if Tile.is_movable(self._tile_at(neighbour := point + direction.vector))]

    def _bfs(self, start_tile: str) -> None:
        start_position = self._position_of(start_tile)
        if start_position is None:
            return

        queue: deque[tuple[Vector2D, int, KeyState]] = deque()
        visited: set[Vector2D] = set()
        adjacent_tiles: dict[str, tuple[int, KeyState]] = dict()

        queue.append((start_position, 0, KeyState.empty()))

        while queue:
            position, distance, keys_required = queue.popleft()
            visited.add(position)
            tile = self._tile_at(position)
            if Tile.is_key(tile) and position != start_position:
                adjacent_tiles[tile] = (distance, keys_required)
                continue
            elif Tile.is_door(tile):
                keys_required = keys_required.add_keys(tile)
            for next_position in self._get_movable_positions(position):
                if next_position not in visited:
                    queue.append((next_position, distance + 1, keys_required))

        self._adjacency_list[start_tile] = adjacent_tiles

    def _generate_adjacency_list(self) -> None:
        for key in self.keys:
            self._bfs(key)
        for entrance in self.entrances:
            self._bfs(entrance)

    def _get_accessible_keys(self, locations: LocationState, keys: KeyState) -> list[tuple[LocationState, int]]:
        result = list()
        for idx, tile in enumerate(locations):
            if tile not in self._adjacency_list:
                self._bfs(tile)
            adjacent_tiles = self._adjacency_list.get(tile, None)
            if adjacent_tiles is None:
                continue
            result.extend([(locations.set(idx, neighbour), distance)
                           for neighbour, (distance, keys_required) in adjacent_tiles.items()
                           if keys.contains(keys_required)])
        return result

    @dataclass(order=True)
    class QueueItem:
        distance: int
        locations: LocationState = field(compare=False)
        keys: KeyState = field(compare=False)

        @property
        def items(self) -> tuple[int, LocationState, KeyState]:
            return self.distance, self.locations, self.keys

    def dijkstra(self) -> ShortestPathsResult:
        pqueue: list[Vault.QueueItem] = list()
        distances: dict[tuple[LocationState, KeyState], int] = dict()
        predecessors: dict[tuple[LocationState, KeyState], tuple[LocationState, KeyState]] = dict()

        initial_locations = LocationState.of(self.entrances)
        initial_keys = KeyState.empty()
        final_state = None

        heapq.heappush(pqueue, Vault.QueueItem(0, initial_locations, initial_keys))
        distances[(initial_locations, initial_keys)] = 0
        predecessors[(initial_locations, initial_keys)] = (initial_locations, initial_keys)

        while pqueue:
            distance, locations, keys = heapq.heappop(pqueue).items
            if keys.contains(self.goal):
                final_state = (locations, keys)
                break
            for next_locations, next_distance in self._get_accessible_keys(locations, keys):
                next_keys = keys.add_keys(next_locations)
                next_distance += distances.get((locations, keys), inf)
                if next_distance < distances.get((next_locations, next_keys), inf):
                    distances[(next_locations, next_keys)] = next_distance
                    predecessors[(next_locations, next_keys)] = (locations, keys)
                    heapq.heappush(pqueue, Vault.QueueItem(next_distance, next_locations, next_keys))

        return ShortestPathsResult(distances, predecessors, final_state)

    def get_map(self) -> list[list[str]]:
        return self._map


@dataclass(frozen=True)
class ShortestPathsResult:
    distances: dict[tuple[LocationState, KeyState], int]
    predecessors: dict[tuple[LocationState, KeyState], tuple[LocationState, KeyState]]
    final_state: tuple[LocationState, KeyState]

    @property
    def distance(self) -> int:
        return self.distances[self.final_state]

    @property
    def path(self) -> list[str]:
        path: list[str] = list()
        curr_state, prev_state = self.final_state, self.predecessors[self.final_state]
        while curr_state != prev_state:
            _, curr_keys = curr_state
            _, prev_keys = prev_state
            key = curr_keys.difference_from(prev_keys)
            if key is not None:
                path.append(key)
            curr_state, prev_state = prev_state, self.predecessors[prev_state]
        return path[::-1]