from day10.Vector2D import Vector2D
from Robot import Robot
from day08.day8 import render_image_as_string
from numpy.typing import NDArray
import numpy as np
import matplotlib.pyplot as plt

def paint_hull(data: list[int], hull_paint: dict[Vector2D, int], max_iters: int = 10_000) -> dict:
    robot = Robot()
    robot.load_program(data)
    current_position = robot.get_position()
    for _ in range(max_iters):
        panel_colour = hull_paint.get(current_position, 0)
        robot.scan_panel(panel_colour)
        panel_colour = robot.step()
        hull_paint[current_position] = panel_colour
        current_position = robot.get_position()
        if robot.is_done():
            break
    return hull_paint

def image_dict_to_image_array(image_dict: dict[Vector2D, int], padding: int = 0) -> NDArray[np.int_]:
    def get_coordinate_range() -> tuple[int, int, int, int]:
        coordinates: list[Vector2D] = list(image_dict.keys())
        x_coordinates: list[int] = list(map(lambda coord: coord.x, coordinates))
        y_coordinates: list[int] = list(map(lambda coord: coord.y, coordinates))
        x_min, x_max = min(x_coordinates) - padding, max(x_coordinates) + padding
        y_min, y_max = min(y_coordinates) - padding, max(y_coordinates) + padding
        return x_min, x_max, y_min, y_max

    x_min, x_max, y_min, y_max = get_coordinate_range()
    image = np.zeros((y_max-y_min+1, x_max-x_min+1), dtype=np.int_)
    for coordinate, colour in image_dict.items():
        x, y = coordinate.x - x_min, coordinate.y - y_min
        image[y, x] = colour
    return np.flipud(image).astype(np.int_)

if __name__ == "__main__":
    with open("day11_input.txt") as file:
        data = list(map(int, file.read().split(',')))

    painted_hull_part1 = paint_hull(data, dict())
    painted_hull_part2 = image_dict_to_image_array(paint_hull(data, {Vector2D.zero(): 1}))
    print(f"Part 1: {len(painted_hull_part1.keys())}")
    print(f"Part 2:\n{render_image_as_string(painted_hull_part2)}")

    plt.figure(figsize=painted_hull_part2.shape[::-1])
    plt.imshow(painted_hull_part2, cmap='gray_r')
    plt.axis('off')
    plt.savefig("day11_output.png", bbox_inches='tight')
    plt.close()