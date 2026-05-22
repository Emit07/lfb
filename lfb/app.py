import os
import sys
import time
import click
import lfb.config as config
from lfb.state import ViewState
from lfb.filesystem import FileSystem
from lfb.renderer import Renderer
from lfb.keymap import load_keymap


class App:
    def __init__(self):
        self.state  = ViewState()
        self.fs     = FileSystem()
        self.render = Renderer(self.state)

        self._clipboard: str | list[str] = ""
        self._clipboard_mode: str = ""   # "copy" | "cut"

        keymap_path = config.KEYMAP_CONFIG or "~/.config/lfb/keymap.toml"

        self._keymap, self._combo_map, _keymap_warning = load_keymap(
            self, keymap_path
        )

        self.render.hide_cursor()

        if _keymap_warning:
            self._redraw(draw_footer = False)
            self.render.log(_keymap_warning, "yellow")
        else:
            self._redraw()

        while True:
            try:
                self._handle_key(click.getchar())
            except KeyboardInterrupt:
                self._exit()

    def _redraw(self, draw_footer: bool = True):
        files    = self.fs.list_dir(self.state.show_hidden)
        cwd      = self.fs.pretty_cwd(config.HOME_TILDA)
        size_str = mtime_str = ""
        if files:
            f         = files[self.state.selected_index]
            size_str  = self.fs.format_size(os.path.getsize(f))
            mtime_str = time.strftime(
                config.DATE_FORMAT,
                time.gmtime(self.fs.file_stat(f).st_mtime)
            )

        self.render.draw_all(self.state, files, cwd, size_str, mtime_str, draw_footer)

    def _files(self) -> list[str]:
        return self.fs.list_dir(self.state.show_hidden)

    def _selected_file(self) -> str | None:
        files = self._files()
        if not files:
            return None
        return files[self.state.selected_index]

    def _chdir(self, path: str):
        self.fs.chdir(path)
        self.state.reset_viewport()
        self._redraw()

    # ── Navigation ───────────────────────────────────────────────────────────

    def _scroll_up(self):
        s = self.state
        if s.selected_index == 0:
            return
        s.selected_index -= 1
        s.display_index  -= 1
        if s.display_index <= 1 and s.min_view > 0:
            s.min_view -= 1
            s.max_view -= 1
            s.display_index += 1
        files = self._files()
        self.render.draw_files(s, files)
        self.render.draw_footer(s, files, *self._footer_strings(files))

    def _scroll_down(self):
        s     = self.state
        files = self._files()
        if s.selected_index >= len(files) - 1:
            return
        s.selected_index += 1
        s.display_index  += 1
        if s.display_index >= (s.max_view - s.min_view - 2) and s.max_view < len(files):
            s.max_view += 1
            s.min_view += 1
            s.display_index -= 1
        self.render.draw_files(s, files)
        self.render.draw_footer(s, files, *self._footer_strings(files))

    def _shift_down(self):
        """Scroll viewport down, keeping cursor visually pinned (Ctrl-E)."""
        s     = self.state
        files = self._files()

        if s.max_view >= len(files):
            return

        s.max_view += 1
        s.min_view += 1

        if s.display_index > 2:
            s.display_index -= 1
        else:
            s.selected_index += 1

        self.render.draw_files(s, files)
        self.render.draw_footer(s, files, *self._footer_strings(files))

    def _shift_up(self):
        """Scroll viewport up, keeping cursor visually pinned (Ctrl-Y)."""
        s     = self.state
        files = self._files()

        if s.min_view <= 0:
            return

        s.max_view -= 1
        s.min_view -= 1

        if s.display_index < os.get_terminal_size()[1] - 9:
            s.display_index += 1
        else:
            s.selected_index -= 1

        self.render.draw_files(s, files)
        self.render.draw_footer(s, files, *self._footer_strings(files))

    def _footer_strings(self, files: list[str]) -> tuple[str, str]:
        if not files:
            return "", ""
        f         = files[self.state.selected_index]
        size_str  = self.fs.format_size(os.path.getsize(f))
        mtime_str = time.strftime(config.DATE_FORMAT, time.gmtime(self.fs.file_stat(f).st_mtime))
        return size_str, mtime_str

    def _go_top(self):
        s = self.state
        s.selected_index = 0
        s.display_index  = 0
        s.min_view = 0
        s.max_view = s.page_height()
        self._redraw()

    def _go_bottom(self):
        s     = self.state
        files = self._files()
        n     = len(files)
        s.selected_index = n - 1
        ph    = s.page_height()
        if n - 1 < ph:
            s.display_index = n - 1
        else:
            s.display_index = ph - 1
            s.min_view = n - ph
            s.max_view = n
        self._redraw()

    def _view_top(self):
        s     = self.state
        files = self._files()

        if s.min_view != 0:
            s.display_index = 2
        else:
            s.display_index  = 0
            s.selected_index = s.min_view + s.display_index

        self.render.draw_files(s, files)
        self.render.draw_footer(s, files, *self._footer_strings(files))

    def _view_middle(self):
        s     = self.state
        files = self._files()

        files_length = len(self.fs.list_dir(s.show_hidden))

        if files_length < s.max_view:
            s.display_index  = int(files_length / 2)
            s.selected_index = int(files_length / 2)
        else:
            s.display_index  = int((os.get_terminal_size()[1] - 6) / 2)
            s.selected_index = s.min_view + s.display_index

        self.render.draw_files(s, files)
        self.render.draw_footer(s, files, *self._footer_strings(files))

    def _view_bottom(self):
        s     = self.state
        files = self._files()

        files_length = len(self.fs.list_dir(s.show_hidden))

        if files_length < s.max_view:
            s.display_index  = files_length - 1
            s.selected_index = s.display_index
        else:
            s.display_index  = os.get_terminal_size()[1] - 9
            s.selected_index = s.max_view - 3

        self.render.draw_files(s, files)
        self.render.draw_footer(s, files, *self._footer_strings(files))

    def _forward(self):
        f = self._selected_file()
        if not f:
            return
        if os.path.isdir(f):
            self._chdir(f)
        else:
            ext = f.rsplit(".", 1)[-1] if "." in f else ""
            if ext in config.IMAGE_EXTENSIONS:
                os.system(f"{config.IMAGE_PROGRAM} '{f}'")
            elif ext == "pdf":
                os.system(f"{config.PDF_READER} '{f}' &")
            elif ext in (*config.VIDEO_EXTENSIONS, *config.MUSIC_EXTENSIONS):
                os.system(f"mpv '{f}' &")
            else:
                self._open_editor(f)
            self._redraw()

    def _back(self):
        cwd = os.getcwd()
        if cwd == "/":
            return
        old_dir = cwd.split("/")[-1]
        self.fs.chdir("..")
        files = self._files()
        s     = self.state
        s.reset_viewport()
        try:
            idx = next(i for i, f in enumerate(files) if f == old_dir)
            s.selected_index = idx
            ph = s.page_height()
            if len(files) > ph:
                s.display_index = min(2, idx)
                s.min_view      = max(0, idx - 2)
            else:
                s.display_index = idx
            s.max_view = s.min_view + ph
        except StopIteration:
            pass
        self._redraw()

    # ── File operations ──────────────────────────────────────────────────────

    def _open_editor(self, path: str = None):
        if path is None:
            path = self._selected_file()
        if path:
            __import__("subprocess").call([config.EDITOR, path])
        self.render.hide_cursor()
        self._redraw()

    def _make_dir(self):
        self.render.move(0, os.get_terminal_size()[1])
        self.render.show_cursor()
        name = input("Directory name: ").strip()
        self.render.hide_cursor()
        if name:
            self.fs.mkdir(name)
        self._redraw()

    def _touch_file(self):
        self.render.move(0, os.get_terminal_size()[1])
        self.render.show_cursor()
        name = input("File name: ").strip()
        self.render.hide_cursor()
        if name:
            self.fs.touch(name)
        self._redraw()

    def _rename(self):
        f = self._selected_file()
        if not f:
            return
        self.render.show_cursor()
        new_name = input("Rename: ").strip()
        self.render.hide_cursor()
        if new_name:
            self.fs.rename(f, new_name)
        self._redraw()

    def _delete(self):
        cwd     = os.getcwd()
        targets = self.state.selected_files.get(cwd) or (
            [self._selected_file()] if self._selected_file() else []
        )
        for target in targets:
            deleted = self.fs.delete(target)
            if not deleted:
                self.render.show_cursor()
                confirm = input(f"Delete non-empty '{target}'? [y/N]: ").strip().lower()
                self.render.hide_cursor()
                if confirm == "y":
                    self.fs.delete(target, confirmed=True)
        s = self.state
        if s.selected_index > 0:
            s.selected_index -= 1
            s.display_index  -= 1
        self._redraw()

    def _copy(self, mode: str):
        cwd   = os.getcwd()
        multi = self.state.selected_files.get(cwd, [])
        if multi:
            self._clipboard = [os.path.join(cwd, f) for f in multi]
        else:
            self._clipboard = os.path.join(cwd, self._selected_file())
        self._clipboard_mode = mode
        label = "Yanked" if mode == "copy" else "Cut"
        x, y  = os.get_terminal_size()
        self.render.move(0, y - 1)
        print(f"\033[K{label}")

    def _paste(self):
        if not self._clipboard:
            return
        cwd     = os.getcwd()
        sources = [self._clipboard] if isinstance(self._clipboard, str) else self._clipboard
        for src in sources:
            dst = os.path.join(cwd, os.path.basename(src))
            if self._clipboard_mode == "copy":
                self.fs.copy(src, dst)
            else:
                self.fs.move(src, dst)
        self._redraw()

    def _toggle_selected(self):
        f      = self._selected_file()
        cwd    = os.getcwd()
        bucket = self.state.selected_files.setdefault(cwd, [])
        if f in bucket:
            bucket.remove(f)
        else:
            bucket.append(f)
        self._scroll_down()

    def _toggle_hidden(self):
        self.state.show_hidden = not self.state.show_hidden
        self.state.reset_viewport()
        self._redraw()

    def _handle_key(self, raw: str):
        if self.state._log_active:
            self._redraw()
            self.state._log_active = False

        c    = ord(raw[0]) if len(raw) == 1 else ord(raw[-1])
        prev = self.state.previous_key

        action = self._combo_map.get((prev, c)) or self._keymap.get(c)

        if action:
            action()

        self.state.previous_key = c

    def _exit(self):
        self.render.clear()
        self.render.show_cursor()
        sys.exit()
