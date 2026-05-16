from typing import Callable
import re

def has_repeated_digits(number: int) -> bool:
    repeat_groups = [match.group() for match in re.finditer(r"(\d)\1+", str(number))]
    return len(repeat_groups) > 0

def is_monotonic_nondecreasing(number: int) -> bool:
    number = str(number)
    return all([number[i] >= number[i-1] for i in range(1, len(number))])

def has_double_digits_not_more(number: int) -> bool:
    repeat_groups = [match.group() for match in re.finditer(r"(\d)\1+", str(number))]
    group_lengths = list(map(len, repeat_groups))
    return 2 in group_lengths

def part1_criteria(number: int) -> bool:
    return has_repeated_digits(number) and is_monotonic_nondecreasing(number)

def part2_criteria(number: int) -> bool:
    return has_double_digits_not_more(number) and is_monotonic_nondecreasing(number)

def count_acceptable_numbers(number_range: list[int] | range, criteria: Callable[[int], int]) -> int:
    acceptable_numbers = 0
    for number in number_range:
        if criteria(number):
            acceptable_numbers += 1
    return acceptable_numbers

if __name__ == "__main__":
    number_range = range(123257, 647015 + 1)
    print(f"Part 1: {count_acceptable_numbers(number_range, part1_criteria)}")
    print(f"Part 2: {count_acceptable_numbers(number_range, part2_criteria)}")