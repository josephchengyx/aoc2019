from Vault import Vault
from copy import deepcopy

def update_map_data(data: list[list[str]], old_segment: list[list[str]], new_segment: list[list[str]])\
        -> list[list[str]]:
    assert len(old_segment) == len(new_segment) and len(old_segment[0]) == len(new_segment[0]) \
           and len(old_segment) <= len(data) and len(old_segment[0]) <= len(data[0])
    segment_y_size, segment_x_size = len(old_segment), len(old_segment[0])
    data = deepcopy(data)
    for y in range(len(data) - segment_y_size + 1):
        for x in range(len(data[0]) - segment_x_size + 1):
            segment = [row[x:x+segment_x_size] for row in data[y:y+segment_y_size]]
            if segment == old_segment:
                for dy, new_row in enumerate(new_segment):
                    data[y+dy][x:x+segment_x_size] = new_row
                break
    return data

if __name__ == "__main__":
    with open("day18_input.txt") as file:
        data = list(map(lambda row: list(row.strip()), file.readlines()))

    vault = Vault(data)
    part1_shortest_paths = vault.dijkstra()
    print(f"Part 1: {part1_shortest_paths.distance}")

    old_segment = [
        ['.', '.', '.'],
        ['.', '@', '.'],
        ['.', '.', '.']
    ]
    new_segment = [
        ['@', '#', '@'],
        ['#', '#', '#'],
        ['@', '#', '@']
    ]

    updated_data = update_map_data(data, old_segment, new_segment)
    updated_vault = Vault(updated_data)
    part2_shortest_paths = updated_vault.dijkstra()
    print(f"Part 2: {part2_shortest_paths.distance}")