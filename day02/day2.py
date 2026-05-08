from copy import copy

with open("day2_input.txt") as file:
    data = list(map(int, file.read().split(',')))

def run_intcode_program(program: list[int]) -> list[int]:
    program = copy(program)
    ptr = 0
    while ptr < len(program):
        opcode = program[ptr]
        match opcode:
            case 1:
                addr1, addr2, addr3 = program[ptr+1:ptr+4]
                program[addr3] = program[addr1] + program[addr2]
            case 2:
                addr1, addr2, addr3 = program[ptr+1:ptr+4]
                program[addr3] = program[addr1] * program[addr2]
            case 99:
                break
        ptr += 4
    return program

def part1(data: list[int]) -> int:
    data = copy(data)
    data[1], data[2] = 12, 2
    return run_intcode_program(data)[0]

def part2(data: list[int], target: int) -> int:
    original_data = data
    for noun in range(99):
        for verb in range(99):
            data = copy(original_data)
            data[1], data[2] = noun, verb
            result = run_intcode_program(data)[0]
            if result == target:
                return 100 * noun + verb
    return -1  # should not reach here, this is bad

print(f"Part 1: {part1(data)}")
print(f"Part 2: {part2(data, 19690720)}")