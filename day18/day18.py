from Vault import GridMap

if __name__ == "__main__":
    with open("day18_input.txt") as file:
        data = list(map(lambda row: list(row.strip()), file.readlines()))

    gridmap = GridMap(data)
    statemap = gridmap.bfs()

    with open("day18_scratchpad.txt", "w") as file:
        file.write('\n'.join(f"{key}: {requirement}" for key, requirement in
                             sorted(statemap.get_requirements().items(), key = lambda item: item[1].length)))