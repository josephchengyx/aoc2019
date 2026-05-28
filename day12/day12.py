from Vector import Vector3D

if __name__ == "__main__":
    with open("day12_input.txt") as file:
        data = [line.rstrip() for line in file.readlines()]

    moons = [Vector3D.from_string(moon) for moon in data]