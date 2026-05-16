from IntCode.v2 import IntCodeComputer

def run_diagnostic_program(data: list[int], input_value: int) -> list[int]:
    computer = IntCodeComputer()
    computer.load_program(data)
    computer.put_input(input_value)
    computer.run()
    return computer.get_output()

if __name__ == "__main__":
    with open("day5_input.txt") as file:
        data = list(map(int, file.read().split(',')))

    print(f"Part 1: {run_diagnostic_program(data, 1)}")
    print(f"Part 2: {run_diagnostic_program(data, 5)}")