from day09.IntCode import IntCodeComputer

with open("day9_input.txt") as file:
    data = list(map(int, file.read().split(',')))

def run_boost_program(data: list[int], input_value: int) -> list[int]:
    computer = IntCodeComputer()
    computer.load_program(data)
    computer.put_input(input_value)
    computer.run()
    return computer.get_output()

print(f"Part 1: {run_boost_program(data, 1)}")
print(f"Part 2: {run_boost_program(data, 2)}")