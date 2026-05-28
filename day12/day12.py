from Vector import Vector3D
from itertools import combinations

def simulate_dynamics(
        moon_positions: list[Vector3D],
        moon_velocities: list[Vector3D],
        timesteps: int
) -> tuple[list[Vector3D], list[Vector3D]]:

    num_moons = len(moon_positions)
    for t in range(timesteps):
        # Apply gravity
        for i, j in combinations(range(num_moons), 2):
            delta_velocity = moon_positions[i].compare(moon_positions[j])
            moon_velocities[i] += delta_velocity
            moon_velocities[j] -= delta_velocity
        # Apply velocity
        for i in range(num_moons):
            moon_positions[i] += moon_velocities[i]
    return moon_positions, moon_velocities

def part1(data: list[str]) -> int:
    moon_positions: list[Vector3D] = [Vector3D.from_string(moon) for moon in data]
    moon_velocities: list[Vector3D] = [Vector3D.zero() for moon in data]

    moon_positions, moon_velocities = simulate_dynamics(moon_positions, moon_velocities, 1000)
    moon_energies: list[float] = [position.energy() * velocity.energy() \
                                for position, velocity in zip(moon_positions, moon_velocities)]
    return sum(moon_energies)

if __name__ == "__main__":
    with open("day12_input.txt") as file:
        data = [line.rstrip() for line in file.readlines()]

    print(f"Part 1: {part1(data)}")