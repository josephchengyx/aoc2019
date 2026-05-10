from Tree import Tree

with open("day6_input.txt") as file:
    data = list(map(lambda line: line.rstrip(), file.readlines()))

def read_orbit_map(data: list[str]) -> Tree:
    orbit_map = Tree()
    for orbit in data:
        parent, child = orbit.split(')')
        orbit_map.add_edge(parent, child)
    return orbit_map

def part1(orbit_map: Tree) -> int:
    total_orbits = 0
    for node in orbit_map.nodes():
        total_orbits += orbit_map.depth(node)
    return total_orbits

def part2(orbit_map: Tree, start: str, end: str) -> int:
    nearest_common_ancestor = orbit_map.nearest_common_ancestor(start, end)
    path_from_start = orbit_map.path_to_node(start, nearest_common_ancestor)
    path_from_end = orbit_map.path_to_node(end, nearest_common_ancestor)
    return len(path_from_start[1:]) + len(path_from_end[1:])

orbit_map = read_orbit_map(data)
print(f"Part 1: {part1(orbit_map)}")
print(f"Part 2: {part2(orbit_map, "YOU", "SAN")}")