from typing import Sequence, Callable, Any
from numpy.typing import NDArray
from collections import Counter
import numpy as np

with open("day8_input.txt") as file:
    data = list(map(int, list(file.read().rstrip())))

image_dimensions = (25, 6)  # (width, height)

def process_image_data(data: list[int], image_dimensions: tuple[int, int]) -> NDArray[np.int_]:
    # output dimensions: (height, width, layers)
    return np.array(data).reshape(image_dimensions + (-1,), order='F').transpose((1, 0, 2))

def argmin(sequence: Sequence[Any], key: Callable[[Any], Any] | None = None) -> int:
    if key is None: key = lambda x: x
    return min(range(len(sequence)), key=lambda idx: key(sequence[idx]))

def part1(image: NDArray[np.int_]) -> int:
    def count_pixel_values(layer: NDArray[np.int_]) -> Counter[int]:
        return Counter(layer.flatten())

    digit_counts_per_layer: list[Counter[int]] = list()
    for l in range(image.shape[-1]):
        digit_counts_per_layer.append(count_pixel_values(image[..., l]))
    least_zeros_layer_idx = argmin(digit_counts_per_layer, key=lambda counts: counts[0])
    ones_digit_count = digit_counts_per_layer[least_zeros_layer_idx][1]
    twos_digit_count = digit_counts_per_layer[least_zeros_layer_idx][2]
    return ones_digit_count * twos_digit_count

def part2(image: NDArray[np.int_]) -> str:
    def decode_pixel(h: int, w: int) -> int:
        l = 0
        while image[h, w, l] == 2:
            l += 1
        return image[h, w, l].item()

    def render_pixel(value: int) -> str:
        return {0: '.', 1: '#'}.get(value, ' ')

    def image_array_to_string(image: NDArray[np.int_]) -> str:
        if image.dtype != object and image.dtype.kind != 'U': image = image.astype(str)
        return '\n'.join(' '.join(row) for row in image)

    decoded_image = np.empty_like(image[..., 0])
    for h, w in np.ndindex(decoded_image.shape):
        decoded_image[h, w] = decode_pixel(h, w)
    rendered_image = np.vectorize(render_pixel)(decoded_image)
    return image_array_to_string(rendered_image)

image = process_image_data(data, image_dimensions)
print(f"Part 1: {part1(image)}")

rendered_image = part2(image)
print(f"Part 2:\n{rendered_image}")

with open("day8_output.txt", "w") as file:
    file.write(rendered_image)