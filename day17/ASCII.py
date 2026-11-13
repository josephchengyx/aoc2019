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
        self._camera_view: list[list[str]] = list(list())
        self._robot_instructions: list[list[int]] = list(list())
        self._robot_output: int = 0
        self._mode: ASCII.Mode = ASCII.Mode.CAMERA

    @property
    def _camera_x_bound(self) -> int:
        return len(self._camera_view[0])

    @property
    def _camera_y_bound(self) -> int:
        return len(self._camera_view)

    def load_program(self, program: list[int]) -> None:
        self._program = program
        self._computer.load_program(self._program)

    def update_camera_view(self) -> None:
        if self._mode is ASCII.Mode.ROBOT:
            self._switch_to_camera_mode()
        self._computer.run()
        intcode_output = self._computer.read_output()
        self._camera_view = ASCII._parse_camera_output(intcode_output)

    def get_camera_view(self) -> str:
        return ASCII._format_camera_view(self._camera_view)

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
    def _format_camera_view(camera_view: list[list[str]]) -> str:
        return '\n'.join(map(lambda row: ' '.join(row), camera_view))

    def _is_in_bounds(self, point: Vector2D) -> bool:
        return 0 <= point.x < self._camera_x_bound and 0 <= point.y < self._camera_y_bound

    def _camera_pixel_at(self, point: Vector2D) -> str | None:
        if not self._is_in_bounds(point):
            return None
        return self._camera_view[point.y][point.x]

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

    _LEFT_TURN = nonmember(((0, 1), (-1, 0)))
    _RIGHT_TURN = nonmember(((0, -1), (1, 0)))

    def turn_left(self) -> Direction:
        return Direction(self.value.transform(Direction._LEFT_TURN))

    def turn_right(self) -> Direction:
        return Direction(self.value.transform(Direction._RIGHT_TURN))


class Pathfinder:
    def __init__(self, ascii_program: ASCII) -> None:
        self._ascii: ASCII = ascii_program
        self._instruction_list: list[str] = list()
        self._position: Vector2D = Vector2D.zero()
        self._heading: Direction = Direction.UP

        if not self._ascii._camera_view:
            self._ascii.update_camera_view()
        self._find_robot_position_and_heading()

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