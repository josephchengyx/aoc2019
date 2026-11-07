from day13.Arcade import InteractiveCabinet

if __name__ == "__main__":
    with open("day13/day13_input.txt") as file:
        program = list(map(int, file.read().split(',')))

    cabinet = InteractiveCabinet()
    cabinet.load_program(program)
    cabinet.start()
    cabinet.play()