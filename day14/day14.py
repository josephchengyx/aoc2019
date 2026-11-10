from Refinery import Nanofactory, Material

def part1(nanofactory: Nanofactory) -> int:
    return nanofactory.get_ore_cost(Material.FUEL, 1)

def part2(nanofactory: Nanofactory, ore_available: int, max_iters: int = 100) -> int:
    lower_bound = ore_available // nanofactory.get_ore_cost(Material.FUEL, 1)
    upper_bound = 2 * lower_bound
    for _ in range(max_iters):
        if nanofactory.get_ore_cost(Material.FUEL, upper_bound) > ore_available:
            break
        else:
            lower_bound = upper_bound
            upper_bound = 2 * lower_bound
    for _ in range(max_iters):
        if not (lower_bound < upper_bound - 1):
            break
        midpoint = (lower_bound + upper_bound) // 2
        if nanofactory.get_ore_cost(Material.FUEL, midpoint) > ore_available:
            upper_bound = midpoint
        else:
            lower_bound = midpoint
    return lower_bound

if __name__ == "__main__":
    with open("day14_input.txt") as file:
        data = list(map(lambda line: line.rstrip(), file.readlines()))

    nanofactory = Nanofactory(data)
    print(f"Part 1: {part1(nanofactory)}")
    print(f"Part 2: {part2(nanofactory, int(1e12))}")
