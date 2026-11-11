from Droid import Direction, Path, Droid
from day10.Vector2D import Vector2D
from collections import deque

def bfs(droid: Droid, start_position: Vector2D = Droid.origin) -> None:
    queue: deque[tuple[Vector2D, Path]] = deque()
    visited: set[Vector2D] = set()
    queue.append((start_position, Path.empty()))
    while queue:
        position, path = queue.popleft()
        droid.traverse(path)
        for direction in Direction:
            new_position = position + direction.vector
            new_path = path.add_step(direction)
            if new_position not in visited:
                queue.append((new_position, new_path))
        droid.backtrack(path)

if __name__ == "__main__":
    with open("day15_input.txt") as file:
        data = list(map(int, file.read().split(',')))