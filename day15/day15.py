from Droid import Droid

if __name__ == "__main__":
    with open("day15_input.txt") as file:
        data = list(map(int, file.read().split(',')))

    droid = Droid()
    droid.load_program(data)
    droid.bfs()

    o2_system_position = droid.get_o2_system_position()
    path_to_o2_system = droid.get_path_to(o2_system_position)
    print(f"Part 1: {path_to_o2_system.length}")

    droid.move_to(o2_system_position)
    print(f"Part 2: {droid.get_max_path_length()}")

    with open("day15_output.txt", "w") as file:
        file.write(droid.view_map())