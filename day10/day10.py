from Line import Coordinate2D, Line2D

with open("day10_input.txt") as file:
    data = list(map(lambda line: line.rstrip(), file.readlines()))

def read_asteroid_map(data: list[str]) -> set[Coordinate2D]:
    asteroids: set[Coordinate2D] = set()
    x_max, y_max = len(data[0]), len(data)
    for y in range(y_max):
        for x in range(x_max):
            if data[y][x] == '#':
                asteroids.add(Coordinate2D(x, y))
    return asteroids

def part1(asteroid_map: set[Coordinate2D]) -> tuple[Coordinate2D, int]:
    visibility_scores: dict[Coordinate2D, int] = dict()
    for station in asteroid_map:
        visibility_scores[station] = 0
        for asteroid in asteroid_map:
            if station == asteroid:
                continue
            line_of_sight = Line2D(station, asteroid)
            if line_of_sight.get_points().isdisjoint(asteroid_map):
                visibility_scores[station] += 1
    return max(visibility_scores.items(), key=lambda item: item[1])

asteroid_map = read_asteroid_map(data)
station, visibility_score = part1(asteroid_map)
print(f"Part 1: {visibility_score}")