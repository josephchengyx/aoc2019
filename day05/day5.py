from IntCode import IntCodeComputer

with open("day5_input.txt") as file:
    data = list(map(int, file.read().split(',')))

def part1(data: list[int]) -> list[int]:
    computer = IntCodeComputer()
    computer.read_program(data)
    computer.put_input(1)
    computer.run()
    return computer.get_output()

print(f"Part 1: {part1(data)}")