from __future__ import annotations
from IntCode.v3 import IntCodeComputer
from day10.Vector2D import Vector2D
from enum import Enum, StrEnum, nonmember
from typing import Final

class ASCII:
    class Pixel(StrEnum):
        SCAFFOLD    = '#'
        OPEN_SPACE  = '.'
        ROBOT_UP    = '^'
        ROBOT_DOWN  = 'v'
        ROBOT_LEFT  = '<'
        ROBOT_RIGHT = '>'
        ROBOT_FELL  = 'X'

    class Mode(Enum):
        CAMERA = 0
        ROBOT  = 1

    def __init__(self) -> None:
        self._computer: IntCodeComputer = IntCodeComputer()
        self._program: list[int] = list()
        self._camera_feed: list[list[str]] = list(list())
        self._robot_instructions: list[list[int]] = list(list())
        self._robot_output: int = 0
        self._mode: ASCII.Mode = ASCII.Mode.CAMERA

    @property
    def _camera_x_bound(self) -> int:
        return len(self._camera_feed[0])

    @property
    def _camera_y_bound(self) -> int:
        return len(self._camera_feed)

    def load_program(self, program: list[int]) -> None:
        self._program = program
        self._computer.load_program(self._program)

    def update_camera_feed(self) -> None:
        if self._mode is ASCII.Mode.ROBOT:
            self._switch_to_camera_mode()
        self._computer.run()
        intcode_output = self._computer.read_output()
        self._camera_feed = ASCII._parse_camera_output(intcode_output)

    def get_camera_feed(self) -> str:
        return ASCII._format_camera_feed(self._camera_feed)

    def input_robot_instructions(self, instructions: list[str]) -> None:
        self._robot_instructions = list(map(ASCII._parse_robot_instruction, instructions))

    def run_robot(self) -> None:
        if self._mode is ASCII.Mode.CAMERA:
            self._switch_to_robot_mode()
        for instruction in self._robot_instructions:
            self._computer.put_input(instruction)
            self._computer.run()
        intcode_output = self._computer.read_output()
        self._robot_output = intcode_output.pop()

    def get_robot_output(self) -> int:
        return self._robot_output

    def _switch_to_robot_mode(self):
        if self._mode is ASCII.Mode.ROBOT:
            return
        self._computer.reset()
        self._computer.load_program(self._program)
        self._computer.configure_settings(await_further_input=True)
        self._computer._write_memory(0, 2)
        self._mode = ASCII.Mode.ROBOT

    def _switch_to_camera_mode(self):
        if self._mode is ASCII.Mode.CAMERA:
            return
        self._computer.reset()
        self._computer.load_program(self._program)
        self._computer.configure_settings(await_further_input=False)
        self._computer._write_memory(0, 1)
        self._mode = ASCII.Mode.CAMERA

    @staticmethod
    def _parse_camera_output(output: list[int]) -> list[list[str]]:
        pixel_string = ''.join(map(chr, output)).strip()
        return list(map(lambda row: list(row), pixel_string.split('\n')))

    @staticmethod
    def _parse_robot_instruction(instruction: str) -> list[int]:
        return list(map(ord, list(instruction)))

    @staticmethod
    def _format_camera_feed(camera_feed: list[list[str]]) -> str:
        return '\n'.join(map(lambda row: ' '.join(row), camera_feed))

    def _is_in_bounds(self, point: Vector2D) -> bool:
        return 0 <= point.x < self._camera_x_bound and 0 <= point.y < self._camera_y_bound

    def _camera_pixel_at(self, point: Vector2D) -> str | None:
        if not self._is_in_bounds(point):
            return None
        return self._camera_feed[point.y][point.x]

    def _get_neighbouring_points(self, point: Vector2D) -> list[Vector2D]:
        neighbours = [point + direction.value for direction in Direction]
        return list(filter(self._is_in_bounds, neighbours))

    def _is_intersection_point(self, point: Vector2D) -> bool:
        neighbours = self._get_neighbouring_points(point)
        if len(neighbours) < 4:
            return False
        for nbr_point in neighbours:
            if self._camera_pixel_at(nbr_point) != ASCII.Pixel.SCAFFOLD:
                return False
        return True

    @staticmethod
    def alignment_parameter(point: Vector2D) -> int:
        return point.x * point.y

    def get_alignment_parameters(self) -> list[int]:
        parameters: list[int] = list()
        for y in range(self._camera_y_bound):
            for x in range(self._camera_x_bound):
                point = Vector2D(x, y)
                if self._is_intersection_point(point):
                    parameters.append(ASCII.alignment_parameter(point))
        return parameters


class Direction(Enum):
    UP    = Vector2D(0, -1)
    DOWN  = Vector2D(0, 1)
    LEFT  = Vector2D(-1, 0)
    RIGHT = Vector2D(1, 0)

    _LEFT_TURN  = nonmember(((0, 1), (-1, 0)))
    _RIGHT_TURN = nonmember(((0, -1), (1, 0)))

    @property
    def vector(self) -> Vector2D:
        return self.value

    @property
    def opposite(self) -> Direction:
        return Direction(-self.value)

    def turn_left(self) -> Direction:
        return Direction(self.value.transform(Direction._LEFT_TURN))

    def turn_right(self) -> Direction:
        return Direction(self.value.transform(Direction._RIGHT_TURN))


class Pathfinder:
    def __init__(self, ascii_program: ASCII) -> None:
        self._ascii: ASCII = ascii_program
        self._path: list[str] = list()
        self._instructions: list[str] = list()
        self._position: Vector2D = Vector2D.zero()
        self._heading: Direction = Direction.UP
        self._live_camera_feed: bool = False

        if not self._ascii._camera_feed:
            self._ascii.update_camera_feed()
        self._find_robot_position_and_heading()

    _max_function_length: Final[int] = 10
    _function_names: Final[tuple[str, ...]] = ('A', 'B', 'C')
    _robot_pixel_to_heading: Final[dict[ASCII.Pixel, Direction]] = {
        ASCII.Pixel.ROBOT_UP: Direction.UP,
        ASCII.Pixel.ROBOT_DOWN: Direction.DOWN,
        ASCII.Pixel.ROBOT_LEFT: Direction.LEFT,
        ASCII.Pixel.ROBOT_RIGHT: Direction.RIGHT
    }

    def _find_robot_position_and_heading(self) -> None:
        for y in range(self._ascii._camera_y_bound):
            for x in range(self._ascii._camera_x_bound):
                position = Vector2D(x, y)
                pixel = self._ascii._camera_pixel_at(position)
                heading = Pathfinder._robot_pixel_to_heading.get(ASCII.Pixel(pixel), None)
                if heading is not None:
                    self._position = position
                    self._heading = heading
                    return

    def _in_front(self) -> Vector2D:
        return self._position + self._heading.value

    def _on_left(self) -> Vector2D:
        return self._position + self._heading.turn_left().value

    def _on_right(self) -> Vector2D:
        return self._position + self._heading.turn_right().value

    def _behind(self) -> Vector2D:
        return self._position - self._heading.value

    def find_path(self, max_iters: int = 1_000) -> None:
        if self._path:
            return
        steps = 0
        for _ in range(max_iters):
            if self._ascii._camera_pixel_at(self._in_front()) == ASCII.Pixel.SCAFFOLD:
                steps += 1
                self._position += self._heading.value
                continue
            if steps > 0:
                self._path.append(str(steps))
                steps = 0
            if self._ascii._camera_pixel_at(self._on_left()) == ASCII.Pixel.SCAFFOLD:
                self._path.append('L')
                self._heading = self._heading.turn_left()
            elif self._ascii._camera_pixel_at(self._on_right()) == ASCII.Pixel.SCAFFOLD:
                self._path.append('R')
                self._heading = self._heading.turn_right()
            else:
                break

    def compress_path(self) -> None:
        def next_unassigned_range(assignment: list[int]) -> tuple[int, int]:
            start = 0
            while start < len(assignment) and assignment[start] != 0:
                start += 1
            end = start
            while end < len(assignment) and assignment[end] == 0:
                end += 1
            return start, end

        def mark_all_occurences(function: list[str], assignment: list[int], function_number: int) -> list[int]:
            for start in range(len(assignment) - len(function) + 1):
                end = start + len(function)
                if self._path[start:end] == function and not any(assignment[start:end]):
                    assignment[start:end] = [function_number] * len(function)
            return assignment

        def unmark_all_occurences(assignment: list[int], function_number: int) -> list[int]:
            for idx, element in enumerate(assignment):
                if element == function_number:
                    assignment[idx] = 0
            return assignment

        def extract_main_routine(functions: list[list[str]], assignment: list[int]) -> str:
            main_routine = list()
            current_function = -1
            current_length = 0
            for function_number in assignment:
                function_number -= 1
                if current_function == -1:
                    current_function = function_number
                if function_number != current_function or current_length > len(functions[current_function]):
                    main_routine.append(Pathfinder._function_names[current_function])
                    current_function = function_number
                    current_length = 0
                current_length += 1
            if current_function != -1:
                main_routine.append(Pathfinder._function_names[current_function])
            return Pathfinder.format_instruction(main_routine)

        def backtrack(functions: list[list[str]], assignment: list[int]) -> tuple[list[list[str]], list[int]]:
            if len(functions) == len(Pathfinder._function_names) and all(assignment):
                return functions, assignment
            elif len(functions) < len(Pathfinder._function_names):
                start, end = next_unassigned_range(assignment)
                max_length = min(end - start, Pathfinder._max_function_length)
                for length in range(max_length, 0, -2):
                    next_function = self._path[start:start+length]
                    functions.append(next_function)
                    assignment = mark_all_occurences(next_function, assignment, len(functions))
                    next_functions, next_assignment = backtrack(functions, assignment)
                    if next_functions and next_assignment:
                        return next_functions, next_assignment
                    assignment = unmark_all_occurences(assignment, len(functions))
                    functions.pop()
            return list(), list()

        if self._instructions:
            return
        functions, assignment = backtrack(list(), [0 for cmd in self._path])
        main_routine = extract_main_routine(functions, assignment)
        live_camera_feed = 'y\n' if self._live_camera_feed else 'n\n'
        self._instructions = [main_routine] + list(map(Pathfinder.format_instruction, functions)) + [live_camera_feed]

    def set_live_camera_feed(self, is_live: bool) -> None:
        self._live_camera_feed = is_live

    def get_path(self) -> list[str]:
        return self._path

    def get_instructions(self) -> list[str]:
        return self._instructions

    @staticmethod
    def format_instruction(instruction: list[str]) -> str:
        return ','.join(instruction) + '\n'