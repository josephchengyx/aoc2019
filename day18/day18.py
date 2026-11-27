from Vault import Vault

if __name__ == "__main__":
    with open("day18_input.txt") as file:
        data = list(map(lambda row: list(row.strip()), file.readlines()))

    vault = Vault(data)
    shortest_paths = vault.dijkstra()

    print(f"Part 1: {shortest_paths.distance}")