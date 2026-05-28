from Vector3D import Vector3D
from typing import TypeVar, Callable
from itertools import combinations
from math import lcm

T = TypeVar('T')
def simulate_dynamics(
        moon_positions: list[T],
        moon_velocities: list[T],
        gravity_function: Callable[[T, T], T],
        timesteps: int
) -> tuple[list[T], list[T]]:

    num_moons = len(moon_positions)
    for _ in range(timesteps):
        # Apply gravity
        for i, j in combinations(range(num_moons), 2):
            delta_velocity = gravity_function(moon_positions[i], moon_positions[j])
            moon_velocities[i] += delta_velocity
            moon_velocities[j] -= delta_velocity
        # Apply velocity
        for i in range(num_moons):
            moon_positions[i] += moon_velocities[i]
    return moon_positions, moon_velocities

def part1(data: list[str]) -> int:
    moon_positions: list[Vector3D] = [Vector3D.from_string(moon) for moon in data]
    moon_velocities: list[Vector3D] = [Vector3D.zero() for moon in data]

    moon_positions, moon_velocities = simulate_dynamics(
        moon_positions, moon_velocities, lambda x, y: x.sgn_of_difference(y), 1000)
    moon_energies: list[float] = [position.energy() * velocity.energy() \
                                for position, velocity in zip(moon_positions, moon_velocities)]
    return sum(moon_energies)

def part2(data: list[str], max_iters: int = 1_000_000) -> int:
    initial_moon_positions: tuple[Vector3D,...] = tuple(Vector3D.from_string(moon) for moon in data)
    cycle_lengths = [0, 0, 0]

    for i, axis in enumerate("xyz"):
        moon_positions: list[int] = [getattr(moon, axis) for moon in initial_moon_positions]
        moon_velocities: list[int] = [0 for moon in initial_moon_positions]

        for t in range(1, max_iters):
            moon_positions, moon_velocities = simulate_dynamics(
                moon_positions, moon_velocities, lambda x, y: Vector3D.sgn_of_difference_scalar(x, y), 1)
            if all(velocity == 0 for velocity in moon_velocities):
                cycle_lengths[i] = 2 * t
                break

    return lcm(*cycle_lengths)

if __name__ == "__main__":
    with open("day12_input.txt") as file:
        data = [line.rstrip() for line in file.readlines()]

    print(f"Part 1: {part1(data)}")
    print(f"Part 2: {part2(data)}")