from Vault import GridMap, State

if __name__ == "__main__":
    with open("day18_test.txt") as file:
        data = list(map(lambda row: list(row.strip()), file.readlines()))

    gridmap = GridMap(data)
    statemap = gridmap.bfs()
    distances, predecessors = statemap.dijkstra()
    print(f"Part 1: {distances[statemap.goal]}")