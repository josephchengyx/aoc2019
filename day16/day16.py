from itertools import accumulate

def digit_list_to_int(digits: list[int]) -> int:
    return int(''.join(map(str, digits)))

def naive_fft(signal: list[int], num_phases: int) -> int:
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
    return digit_list_to_int(signal[:8])

def fast_fft(signal: list[int], signal_repeats: int, num_phases: int) -> int:
    # N.B.: fast-flawed frequency transmission, not fast-fast fourier transform
    signal_length = len(signal) * signal_repeats
    offset = digit_list_to_int(signal[:7])
    assert offset >= signal_length // 2, "only works if message location is past half the signal length!"

    def get_signal_element(idx: int) -> int:
        if idx < 0: idx += signal_length
        return signal[idx % len(signal)]

    def fft_phase(input_list: list[int]) -> list[int]:
        return [abs(elem) % 10 for elem in accumulate(input_list)]

    # reverse the signal from end to offset so that we can capitalize on cumsum
    signal_segment = [get_signal_element(i) for i in range(signal_length - 1, offset - 1, -1)]
    for _ in range(num_phases):
        signal_segment = fft_phase(signal_segment)
    return digit_list_to_int(signal_segment[-8:][::-1])

if __name__ == "__main__":
    with open("day16_input.txt") as file:
        data = list(map(int, list(file.read().strip())))

    print(f"Part 1: {naive_fft(data, 100)}")
    print(f"Part 2: {fast_fft(data, 10_000, 100)}")