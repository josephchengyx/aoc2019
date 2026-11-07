from Arcade import Cabinet, Player

def part1(data: list[int]) -> int:
    cabinet = Cabinet()
    cabinet.load_program(data)
    cabinet.start()
    return cabinet.get_block_count()

def part2(data: list[int]) -> int:
    cabinet = Cabinet()
    cabinet.load_program(data)
    cabinet.start()
    player = Player()
    player.play(cabinet)
    return cabinet.score

if __name__ == "__main__":
    with open("day13_input.txt") as file:
        data = list(map(int, file.read().split(',')))

    cabinet = Cabinet()
    cabinet.load_program(data)
    cabinet.start()
    starting_block_count = cabinet.get_block_count()

    player = Player()
    player.play(cabinet)
    final_score = cabinet.score

    print(f"Part 1: {starting_block_count}")
    print(f"Part 2: {final_score}")