# renderer.py
import os
import sys
import lfb.config as config
import lfb.icons as icons
import lfb.filetypes as filetypes
from lfb.state import ViewState


class Renderer:
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
        self._buf: list[str] = []

    # ── Buffer helpers ───────────────────────────────────────────────────────

    def _write(self, s: str):
        self._buf.append(s)

    def _flush(self):
        sys.stdout.write("".join(self._buf))
        sys.stdout.flush()
        self._buf.clear()

    # ── Primitives ───────────────────────────────────────────────────────────

    def clear(self):
        sys.stdout.write("\033[H\033[J") 
        # TODO fix this
        # self._write("\033[H\033[J")

    def move(self, x: int, y: int):
        self._write(f"\033[{y};{x}H")

    def hide_cursor(self):
        sys.stdout.write("\x1b[?25l")
        sys.stdout.flush()

    def show_cursor(self):
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()

    def _coloured(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m"

    # ── Composite draw calls ─────────────────────────────────────────────────

    def draw_all(self, state: ViewState, files: list[str], cwd: str,
                 size_str: str, mtime_str: str, display_footer: bool = True):
        self.clear()
        self.draw_header(cwd)
        self.draw_scroll_hint_top(state)
        self.draw_files(state, files)
        self.draw_scroll_hint_bottom(state, files)
        if display_footer:
            self.draw_footer(state, files, size_str, mtime_str)
        self._flush()

    def draw_header(self, pretty_cwd: str):
        self.move(0, 1)
        self._write(self._coloured("\033[K" + pretty_cwd, config.DIRECTORY_DISPLAY_COLOUR))

    def draw_scroll_hint_top(self, state: ViewState):
        if not config.DRAW_ICONS:
            return
        self.move(0, 2)
        self._write("\033[K" + (icons.ARROW_UP if state.min_view > 0 else ""))

    def draw_scroll_hint_bottom(self, state: ViewState, files: list[str]):
        if not config.DRAW_ICONS:
            return
        term_height = os.get_terminal_size()[1]
        self.move(0, term_height - 3)
        self._write("\033[K" + (icons.ARROW_DOWN if len(files) > state.max_view else ""))

    def draw_files(self, state: ViewState, files: list[str]):
        visible     = files[state.min_view: state.max_view]
        term_height = os.get_terminal_size()[1]
        max_rows    = term_height - 4 if config.DRAW_ICONS else term_height - 4
        start_row   = 3

        for i in range(max_rows):
            self.move(0, start_row + i)
            if i < len(visible):
                self._write(self._draw_file_row(visible[i], i, state))
            else:
                self._write("\033[K")

        self._flush()

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
            self._write(self._coloured(
                f"\033[K{pos}/{total} {mtime_str} {size_str}",
                config.FOOTER_COLOUR,
            ))
        else:
            self._write(self._coloured("0/0", config.FOOTER_COLOUR))

        self._flush()

    def _draw_file_row(self, filename: str, row: int, state: ViewState) -> str:
        icon, icon_colour, file_colour = filetypes.resolve(filename)
        is_dir    = os.path.isdir(filename)
        is_cursor = (state.display_index == row)

        cwd           = os.getcwd()
        selected_here = state.selected_files.get(cwd, [])
        marker = "\033[47m+\033[0m" if filename in selected_here else " "
        suffix = "/" if is_dir else ""

        term_width = os.get_terminal_size()[0]
        max_width  = term_width - 4 if config.DRAW_ICONS else term_width - 2
        display_name = self._truncate(filename, max_width - len(suffix)) + suffix

        if is_cursor:
            name_part = f"\033[30;47m{display_name}\033[0m"
        else:
            name_part = f"\033[{file_colour}m{display_name}\033[0m"

        if config.DRAW_ICONS:
            return f"{marker}\033[K\033[{icon_colour}m{icon} \033[0m{name_part}"
        else:
            return f"{marker}\033[0m\033[K{name_part}"

    def _truncate(self, name: str, max_width: int) -> str:
        if len(name) <= max_width:
            return name
        return name[:max_width - 3] + "..."

    def log(self, message: str, colour: str = "white"):
        code = self.LOG_COLOURS.get(colour, "0")
        _, term_height = os.get_terminal_size()
        self.move(0, term_height - 1)
        self._write(f"\033[K\033[{code}m{message}\033[0m")
        self._flush()
        self.state._log_active = True
