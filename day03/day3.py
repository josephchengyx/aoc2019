from Line import Coordinate2D, Line2D

def trace_wiring(data: list[str]) -> list[Line2D]:
    wire_segments = list()  # list[Line2D]
    curr_point = Coordinate2D.zero()
    for segment in data:
        curr_line = Line2D.from_point_and_path(curr_point, segment)
        wire_segments.append(curr_line)
        curr_point = curr_line.end
    return wire_segments

def get_intersection_points(wire1: list[Line2D], wire2: list[Line2D]) -> list[tuple[Coordinate2D, int, int]]:
    intersection_points: list[tuple[Coordinate2D, int, int]] = list()
    for i1, segment1 in enumerate(wire1):
        for i2, segment2 in enumerate(wire2):
            intersection = segment1.get_intersection_with(segment2)
            if intersection is not None:
                intersection_points.append((intersection, i1, i2))
    return intersection_points

def cumulative_wiring_length(wire: list[Line2D]) -> list[int]:
    lengths: list[int] = list()
    cumulative_length = 0
    for segment in wire:
        cumulative_length += segment.length()
        lengths.append(cumulative_length)
    return lengths

def part1(intersection_points: list[tuple[Coordinate2D, int, int]]) -> int:
    manhattan_distances: list[int] = list()
    for intersection, _, _ in intersection_points:
        manhattan_distances.append(intersection.manhattan_distance())
    return min(manhattan_distances)

def part2(wire1: list[Line2D], wire2: list[Line2D], intersection_points: list[tuple[Coordinate2D, int, int]]) -> int:
    wire1_lengths = cumulative_wiring_length(wire1)
    wire2_lengths = cumulative_wiring_length(wire2)
    wiring_distances: list[int] = list()
    for intersection, i1, i2 in intersection_points:
        wiring_distances.append(wire1_lengths[i1-1] + wire1[i1].length_up_to_point(intersection) \
                                + wire2_lengths[i2-1] + wire2[i2].length_up_to_point(intersection))
    return min(wiring_distances)

if __name__ == "__main__":
    with open("day3_input.txt") as file:
        data = list(map(lambda line: line.rstrip().split(','), file.readlines()))

    wire1 = trace_wiring(data[0])
    wire2 = trace_wiring(data[1])
    intersection_points = get_intersection_points(wire1, wire2)

    print(f"Part 1: {part1(intersection_points)}")
    print(f"Part 2: {part2(wire1, wire2, intersection_points)}")