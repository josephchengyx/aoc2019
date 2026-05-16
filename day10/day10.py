from Vector import Vector2D
from typing import Any

def read_asteroid_map(data: list[str]) -> set[Vector2D]:
    asteroids: set[Vector2D] = set()
    x_max, y_max = len(data[0]), len(data)
    for y in range(y_max):
        for x in range(x_max):
            if data[y][x] == '#':
                asteroids.add(Vector2D(x, y))
    return asteroids

def part1(asteroid_map: set[Vector2D]) -> tuple[Vector2D, int]:
    visibility_scores: dict[Vector2D, int] = dict()
    for station in asteroid_map:
        lines_of_sight: set[Vector2D] = set()
        for asteroid in asteroid_map:
            if station == asteroid:
                continue
            line_of_sight = (asteroid - station).normalize()
            lines_of_sight.add(line_of_sight)
        visibility_scores[station] = len(lines_of_sight)
    return max(visibility_scores.items(), key=lambda item: item[1])

def part2(station: Vector2D, asteroid_map: set[Vector2D]) -> int:
    def unravel_colwise(lst: list[list[Any]]) -> list[Any]:
        unravelled: list[Any] = list()
        rows, cols = len(lst), max(map(lambda nested: len(nested), lst))
        for c in range(cols):
            for r in range(rows):
                if c >= len(lst[r]):
                    continue
                unravelled.append(lst[r][c])
        return unravelled

    up_axis = Vector2D(0, -1)
    laser_orientations: dict[Vector2D, list[Vector2D]] = dict()
    for asteroid in asteroid_map:
        if station == asteroid:
            continue
        orientation = (asteroid - station).normalize()
        if orientation not in laser_orientations:
            laser_orientations[orientation] = list()
        laser_orientations[orientation].append(asteroid)
    for orientation, asteroids in laser_orientations.items():
        asteroids.sort(key=lambda asteroid: asteroid.squared_euclidean_distance(station))
    laser_orientations: list[tuple[Vector2D, list[Vector2D]]] \
        = list(laser_orientations.items())
    laser_orientations.sort(key=lambda orientation: orientation[0].rotation_from(up_axis))
    laser_orientations: list[list[Vector2D]] \
        = list(map(lambda orientation: orientation[1], laser_orientations))
    laser_orientations: list[Vector2D] = unravel_colwise(laser_orientations)
    asteroid_200 = laser_orientations[200-1]
    return asteroid_200.x * 100 + asteroid_200.y

if __name__ == "__main__":
    with open("day10_input.txt") as file:
        data = list(map(lambda line: line.rstrip(), file.readlines()))

    asteroid_map = read_asteroid_map(data)
    station, visibility_score = part1(asteroid_map)
    print(f"Part 1: {visibility_score}")
    print(f"Part 2: {part2(station, asteroid_map)}")