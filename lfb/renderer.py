# renderer.py
import os
import time
import lfb.config as config
import lfb.icons as icons
import lfb.filetypes as filetypes
from lfb.state import ViewState

class Renderer:
    """
    Draws the UI. Reads ViewState; never writes to it.
    All terminal escape codes live here and nowhere else.
    """

    LOG_COLOURS: dict[str, str] = {
        "red":     "31",
        "green":   "32",
        "yellow":  "33",
        "blue":    "34",
        "magenta": "35",
        "cyan":    "36",
        "white":   "37",
        "default": "0",
    }

    def __init__(self, state: ViewState):
        self.state = state

    def clear(self):
        print("\033[H\033[J", end="")

    def move(self, x: int, y: int):
        print(f"\033[{y};{x}H", end="")

    def hide_cursor(self):
        print("\x1b[?25l", end="")

    def show_cursor(self):
        print("\x1b[?25h", end="")

    def coloured(self, text: str, code: str):
        print(f"\033[{code}m{text}\033[0m")


    def draw_all(self, state: ViewState, files: list[str], cwd: str,
                 size_str: str, mtime_str: str, display_footer: bool = True):
        """Redraws everything. Pass pre-computed strings to keep this pure."""
        self.clear()
        self.draw_header(cwd)
        self.draw_scroll_hint_top(state)
        self.draw_files(state, files)
        self.draw_scroll_hint_bottom(state, files)
        if display_footer:
            self.draw_footer(state, files, size_str, mtime_str)

    def draw_header(self, pretty_cwd: str):
        self.move(0, 0)
        self.coloured("\033[K" + pretty_cwd, config.DIRECTORY_DISPLAY_COLOUR)

    def draw_scroll_hint_top(self, state: ViewState):
        if not config.DRAW_ICONS:
            return
        self.move(0, 2)
        print("\033[K" + (icons.ARROW_UP if state.min_view > 0 else ""))

    def draw_scroll_hint_bottom(self, state: ViewState, files: list[str]):
        if not config.DRAW_ICONS:
            return
        term_height = os.get_terminal_size()[1]
        self.move(0, term_height - 3)
        print("\033[K" + (icons.ARROW_DOWN if len(files) > state.max_view else ""))

    def draw_files(self, state: ViewState, files: list[str]):
        visible     = files[state.min_view: state.max_view]
        term_height = os.get_terminal_size()[1]
        max_rows    = term_height - 6 if config.DRAW_ICONS else term_height - 5
        start_row   = 3

        for i in range(max_rows):
            self.move(0, start_row + i)
            if i < len(visible):
                self._draw_file_row(visible[i], i, state)
            else:
                print("\033[K", end="")

    def draw_footer(self, state: ViewState, files: list[str],
                    size_str: str, mtime_str: str):
        if self.state._log_active:
            self.state._log_active = False
            return

        _, term_height = os.get_terminal_size()
        self.move(0, term_height - 1)
        if files:
            total = len(files)
            pos   = state.selected_index + 1
            self.coloured(
                f"\033[K{pos}/{total} {mtime_str} {size_str}",
                config.FOOTER_COLOUR,
            )
        else:
            self.coloured("0/0", config.FOOTER_COLOUR)
    
    def _draw_file_row(self, filename: str, row: int, state: ViewState):
        icon, icon_colour, file_colour = filetypes.resolve(filename)
        is_dir    = os.path.isdir(filename)
        is_cursor = (state.display_index == row)

        cwd           = os.getcwd()
        selected_here = state.selected_files.get(cwd, [])
        marker = "\033[47m+\033[0m" if filename in selected_here else " "
        suffix = "/" if is_dir else ""

        term_width = os.get_terminal_size()[0]
        if config.DRAW_ICONS:
            max_width = term_width - 4  # marker + icon + space + suffix
        else:
            max_width = term_width - 2  # marker + suffix

        display_name = self._truncate(filename, max_width - len(suffix)) + suffix

        if config.DRAW_ICONS:
            name_part = (
                f"\033[30;47m{display_name}\033[0m" if is_cursor
                else f"\033[{file_colour}m{display_name}\033[0m"
            )
            print(f"{marker}\033[K\033[{icon_colour}m{icon} \033[0m{name_part}")
        else:
            name_part = (
                f"\033[30;47m{display_name}\033[0m" if is_cursor
                else f"\033[{file_colour}m{display_name}\033[0m"
            )
            print(f"{marker}\033[0m\033[K{name_part}")

    def _truncate(self, name: str, max_width: int) -> str:
        if len(name) <= max_width:
            return name
        return name[:max_width - 3] + "..."

    def log(self, message: str, colour: str = "white"):
        code = self.LOG_COLOURS.get(colour, "0")

        _, term_height = os.get_terminal_size()

        self.move(1, term_height)   # column 1, last row

        print(
            f"\033[K\033[{code}m{message}\033[0m",
            end="",
            flush=True
        )
        self.coloured(
            f"\033[K{pos}/{total} {mtime_str} {size_str}",
            code,
        )

        self.state._log_active = True
