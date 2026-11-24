from ASCII import ASCII, Pathfinder

if __name__ == "__main__":
    with open("day17_input.txt") as file:
        data = list(map(int, file.read().split(',')))

    ascii_program = ASCII()
    ascii_program.load_program(data)
    ascii_program.update_camera_feed()
    camera_output = ascii_program.get_camera_feed()
    print(f"Part 1: {sum(ascii_program.get_alignment_parameters())}")

    with open("day17_camera_view.txt", "w") as file:
        file.write(camera_output)

    pathfinder = Pathfinder(ascii_program)
    pathfinder.find_path()
    pathfinder.compress_path()
    instructions = pathfinder.get_instructions()
    instructions.append('n\n')  # don't want live camera feed

    with open("day17_robot_instructions.txt", "w") as file:
        file.write(''.join(instructions))

    ascii_program.input_robot_instructions(instructions)
    ascii_program.run_robot()
    print(f"Part 2: {ascii_program.get_robot_output()}")