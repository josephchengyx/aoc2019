def fft(signal: list[int], num_phases: int) -> list[int]:
    pattern: list[int] = [0, 1, 0, -1]
    def get_pattern_value(in_idx: int, out_idx: int) -> int:
        return pattern[(in_idx + 1) // (out_idx + 1) % len(pattern)]

    def fft_phase(input_list: list[int]) -> list[int]:
        output_list: list[int] = list()
        for out_idx in range(len(input_list)):
            out_elem = 0
            for in_idx, in_elem in enumerate(input_list):
                out_elem += in_elem * get_pattern_value(in_idx, out_idx)
            output_list.append(abs(out_elem) % 10)
        return output_list

    for _ in range(num_phases):
        signal = fft_phase(signal)
    return signal

def digit_list_to_int(digits: list[int]) -> int:
    return int(''.join(map(str, digits)))

def part1(data: list[int]) -> int:
    output = fft(data, 100)[:8]
    return digit_list_to_int(output)

def part2(data: list[int]) -> int:
    offset = digit_list_to_int(data[:7])
    pass

if __name__ == "__main__":
    with open("day16_input.txt") as file:
        data = list(map(int, list(file.read().strip())))

    print(f"Part 1: {part1(data)}")