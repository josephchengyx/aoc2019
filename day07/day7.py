from day05.IntCode import IntCodeComputer
from itertools import permutations
from typing import Iterable, Callable

with open("day7_input.txt") as file:
    data = list(map(int, file.read().split(',')))

def find_max_thruster_signal(
        phase_settings: Iterable[tuple[int, ...]],
        amplify_signal: Callable[[tuple[int, ...]], int]) -> int:
    best_setting = None
    max_thruster_signal = 0
    for setting in phase_settings:
        thruster_signal = amplify_signal(setting)
        if thruster_signal > max_thruster_signal:
            best_setting = setting
            max_thruster_signal = thruster_signal
    return max_thruster_signal

def part1(data: list[int]) -> int:
    def amplify_signal(setting: tuple[int, ...]) -> int:
        signal = 0
        for amp_setting in setting:
            amplifier.read_program(data)
            amplifier.put_input([amp_setting, signal])
            amplifier.run()
            signal = amplifier.get_output().pop()
        return signal

    amplifier = IntCodeComputer()
    phase_settings = permutations(list(range(5)))
    return find_max_thruster_signal(phase_settings, amplify_signal)

def part2(data: list[int]) -> int:
    def amplify_signal(setting: tuple[int, ...], max_passes: int = 100) -> int:
        signal = 0
        amp_done = [False for _ in range(5)]
        for amplifier, amp_setting in zip(amplifiers, setting):
            amplifier.configure_settings("await_further_input", True)
            amplifier.read_program(data)
            amplifier.put_input(amp_setting)
        for passes in range(max_passes):
            for i, amplifier in enumerate(amplifiers):
                amplifier.put_input(signal)
                amplifier.run()
                signal = amplifier.get_output().pop()
                amp_done[i] = amplifier.is_done()
            if all(amp_done):
                break
        for amplifier in amplifiers:
            amplifier.reset()
        return signal

    amplifiers = [IntCodeComputer() for _ in range(5)]
    phase_settings = permutations(list(range(5, 9 + 1)))
    return find_max_thruster_signal(phase_settings, amplify_signal)

print(f"Part 1: {part1(data)}")
print(f"Part 2: {part2(data)}")