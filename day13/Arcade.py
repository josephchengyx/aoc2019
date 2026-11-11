from __future__ import annotations
from IntCode.v3 import IntCodeComputer
from enum import Enum
from typing import Self, Final, Callable, Optional
import curses, time

class Cabinet:
    class Tile(Enum):
        EMPTY = (0, ' ')
        WALL = (1, 'X')
        BLOCK = (2, '*')
        PADDLE = (3, '_')
        BALL = (4, 'o')

        def __new__(cls, _id: int, _char: str) -> Self:
            obj = object.__new__(cls)
            obj._value_ = _id
            obj.char = _char
            return obj

    _KEYMAP: Final[dict[str, int]] = {'a': -1, 's': 0, 'd': 1}

    def __init__(self) -> None:
        self._computer: IntCodeComputer = IntCodeComputer()
        self._computer.configure_settings(await_further_input=True)
        self._program: list[int] = list()
        self._screen: dict[tuple[int, int], Cabinet.Tile] = dict()
        self._screen_size_x: int = 0
        self._screen_size_y: int = 0

        self.score: int = 0
        self.paddle_pos: tuple[int, int] = (0, 0)
        self.ball_pos: tuple[int, int] = (0, 0)

    def load_program(self, program: list[int]) -> None:
        self._program = program
        self._computer.load_program(self._program)

    def _set_to_play_mode(self):
        self._computer._write_memory(0, 2)

    def start(self) -> None:
        self._computer.run()
        self._update_screen()
        self._update_screen_size()
        self._computer.reset()
        self._computer.load_program(self._program)

    def play(self, input_source: Optional[Callable[[Cabinet], int]] = None) -> None:
        if input_source is None:
            input_source = Cabinet._get_joystick_input
        self._set_to_play_mode()
        self._computer.run()
        self._update_screen()
        while not self._computer.is_done():
            joystick_input = input_source(self)
            self._computer.put_input(joystick_input)
            self._computer.run()
            self._update_screen()

    def _get_joystick_input(self) -> int:
        self._render_frame()
        input_key = ''
        while input_key not in Cabinet._KEYMAP:
            input_key = input("Enter joystick input ('a' for left, 's' for stay, 'd' for right): ").lower()
        joystick_input = Cabinet._KEYMAP[input_key]
        return joystick_input

    def _render_frame(self) -> None:
        print(f"\nCurrent score: {self.score}")
        print(self.draw_screen())

    def _update_screen(self) -> None:
        output = self._computer.read_output()
        for i in range(0, len(output), 3):
            x, y, value = output[i:i+3]
            if (x, y) == (-1, 0):
                self.score = value
            else:
                tile = Cabinet.Tile(value)
                self._screen[(x, y)] = tile
                match tile:
                    case Cabinet.Tile.PADDLE:
                        self.paddle_pos = (x, y)
                    case Cabinet.Tile.BALL:
                        self.ball_pos = (x, y)

    def _update_screen_size(self) -> None:
        if not self._screen:
            return
        screen_coords_x, screen_coords_y = zip(*self._screen.keys())
        self._screen_size_x = max(screen_coords_x) + 1
        self._screen_size_y = max(screen_coords_y) + 1

    def _get_screen(self) -> list[list[str]]:
        screen: list[list[str]] = [[' ' for x in range(self._screen_size_x)] for y in range(self._screen_size_y)]
        for (x, y), tile in self._screen.items():
            screen[y][x] = tile.char
        return screen

    def get_block_count(self) -> int:
        return len(list(filter(lambda tile: tile == Cabinet.Tile.BLOCK, self._screen.values())))

    def draw_screen(self) -> str:
        screen = self._get_screen()
        return '\n'.join(' '.join(row) for row in screen)


class InteractiveCabinet(Cabinet):
    _KEYMAP: Final[dict[int, int]] = {curses.KEY_LEFT: -1, curses.KEY_RIGHT: 1}

    def __init__(self) -> None:
        super().__init__()
        self.framerate_hz: float = 1.5
        self._frame_time_secs = 1 / self.framerate_hz

    def set_framerate_hz(self, framerate_hz: float) -> None:
        self.framerate_hz = framerate_hz
        self._frame_time_secs = 1 / self.framerate_hz

    def play(self, input_source: Optional[Callable[[Cabinet], int]] = None) -> None:
        curses.wrapper(self._run)

    def _run(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        self._set_to_play_mode()
        self._computer.run()
        self._update_screen()
        self._render_frame(stdscr)
        self._show_game_start(stdscr)
        next_tick = time.monotonic() + self._frame_time_secs
        while not self._computer.is_done():
            joystick_input = self._get_joystick_input(stdscr, next_tick)
            self._computer.put_input(joystick_input)
            self._computer.run()
            self._update_screen()
            self._render_frame(stdscr)
            next_tick += self._frame_time_secs
        self._show_game_over(stdscr)

    def _get_joystick_input(self, stdscr: curses.window, deadline: float) -> int:
        joystick_input = 0
        while (remaining_time := deadline - time.monotonic()) > 0:
            stdscr.timeout(max(1, int(remaining_time * 1000)))
            input_key = stdscr.getch()
            if input_key in InteractiveCabinet._KEYMAP:
                joystick_input = InteractiveCabinet._KEYMAP[input_key]
        return joystick_input

    def _render_frame(self, stdscr: curses.window) -> None:
        stdscr.erase()
        stdscr.addstr(0, 0, "BREAKOUT", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Current score: {self.score}")
        for y, row in enumerate(self._get_screen(), start=3):
            stdscr.addstr(y, 0, ' '.join(row))
        stdscr.refresh()

    def _show_game_start(self, stdscr: curses.window) -> None:
        stdscr.addstr(2, 0, "Press any key to start")
        stdscr.refresh()
        curses.flushinp()
        stdscr.timeout(-1)
        while stdscr.getch() in {-1, curses.KEY_RESIZE}:
            pass
        stdscr.move(2, 0)
        stdscr.clrtoeol()

    def _show_game_over(self, stdscr: curses.window) -> None:
        stdscr.move(1, 0)
        stdscr.clrtoeol()
        stdscr.addstr(0, 0, "YOU WIN!" if self.get_block_count() == 0 else "GAME OVER", curses.A_BOLD)
        stdscr.addstr(1, 0, f"Final score: {self.score}")
        stdscr.addstr(2, 0, "Press any key to exit")
        stdscr.refresh()
        curses.flushinp()
        stdscr.timeout(-1)
        while stdscr.getch() in InteractiveCabinet._KEYMAP:
            pass


class Player:
    def __init__(self) -> None:
        self.move_history: list[int] = list()
        self._is_recording: bool = False

    def record_moves(self, value: bool) -> None:
        self._is_recording = value

    def clear_move_history(self) -> None:
        self.move_history = list()

    @staticmethod
    def sgn(x: int) -> int:
        return (x > 0) - (x < 0)

    def move_joystick(self, cabinet: Cabinet) -> int:
        paddle_x, paddle_y = cabinet.paddle_pos
        ball_x, ball_y = cabinet.ball_pos
        joystick_input = Player.sgn(ball_x - paddle_x)
        if self._is_recording:
            self.move_history.append(joystick_input)
        return joystick_input

    def play(self, cabinet: Cabinet):
        cabinet.play(self.move_joystick)