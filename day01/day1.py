with open("day1_input.txt") as file:
    data = list(map(int, file.readlines()))

def fuel_requirement(mass: int) -> int:
    return max(mass // 3 - 2, 0)

def part1(data: list[int]) -> int:
    return sum(map(fuel_requirement, data))

def part2(data: list[int]) -> int:
    total = 0
    for mass in data:
        added_fuel = fuel_requirement(mass)
        total += added_fuel
        while added_fuel > 0:
            added_fuel = fuel_requirement(added_fuel)
            total += added_fuel
    return total

print(f"Part 1: {part1(data)}")
print(f"Part 2: {part2(data)}")