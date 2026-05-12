from day05.IntCode import IntCodeComputer

with open("day5_input.txt") as file:
    data = list(map(int, file.read().split(',')))

def run_diagnostic_program(data: list[int], input_value: int) -> list[int]:
    computer = IntCodeComputer()
    computer.load_program(data)
    computer.put_input(input_value)
    computer.run()
    return computer.get_output()

print(f"Part 1: {run_diagnostic_program(data, 1)}")
print(f"Part 2: {run_diagnostic_program(data, 5)}")