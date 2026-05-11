from typing import Sequence, Callable, Any
from collections import Counter
import numpy as np

with open("day8_input.txt") as file:
    data = list(map(int, list(file.read().rstrip())))

image_dimensions = (25, 6)  # (width, height)

def process_image_data(data: list[int], image_dimensions: tuple[int, int]) -> np.ndarray:
    return np.array(data).reshape(image_dimensions + (-1,), order='F').transpose((1, 0, 2))

def argmax(sequence: Sequence[Any], key: Callable[[Any], Any] | None = None) -> int:
    if key is None:
        return max(range(len(sequence)), key=lambda idx: sequence[idx])
    else:
        return max(range(len(sequence)), key=lambda idx: key(sequence[idx]))

def argmin(sequence: Sequence[Any], key: Callable[[Any], Any] | None = None) -> int:
    if key is None:
        return min(range(len(sequence)), key=lambda idx: sequence[idx])
    else:
        return min(range(len(sequence)), key=lambda idx: key(sequence[idx]))

def part1(image: np.ndarray) -> int:
    def count_pixel_values(layer: np.ndarray) -> Counter[int]:
        return Counter(layer.flatten())

    digit_counts_per_layer: list[Counter[int]] = list()
    for l in range(image.shape[-1]):
        layer = image[..., l]
        digit_counts_per_layer.append(count_pixel_values(layer))
    least_zeros_layer_idx = argmin(digit_counts_per_layer, key=lambda counts: counts[0])
    ones_digit_count = digit_counts_per_layer[least_zeros_layer_idx][1]
    twos_digit_count = digit_counts_per_layer[least_zeros_layer_idx][2]
    return ones_digit_count * twos_digit_count

image = process_image_data(data, image_dimensions)
print(f"Part 1: {part1(image)}")