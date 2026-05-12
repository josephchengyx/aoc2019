from day02.IntCode import IntCodeComputer

with open("day2_input.txt") as file:
    data = list(map(int, file.read().split(',')))

def part1(data: list[int]) -> int:
    computer = IntCodeComputer()
    computer.load_program(data)
    computer.set_memory([1, 2], [12, 2])
    computer.run()
    return computer.read_memory(0)

def part2(data: list[int], target: int) -> int:
    computer = IntCodeComputer()
    for noun in range(99):
        for verb in range(99):
            computer.load_program(data)
            computer.set_memory([1, 2], [noun, verb])
            computer.run()
            result = computer.read_memory(0)
            if result == target:
                return 100 * noun + verb
    return -1  # should not reach here, this is bad

print(f"Part 1: {part1(data)}")
print(f"Part 2: {part2(data, 19690720)}")