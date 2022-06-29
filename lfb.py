import math
import os
import shutil
import sys
import time
from subprocess import call

import click

import config
import icons


class Draw:
    def __init__(self):
        self._selected_index = 0
        self._display_index = 0
        self._show_hidden_files = config.SHOW_HIDDEN_FILES
        self._min_view = 0
        self._max_view = os.get_terminal_size()[1] - 6
        self._display_files = None
        self._selected = {}

        self.hide_cursor()

        self.clear()
        self.draw_directory()
        self.draw_files()
        self.draw_footer()

    def clear(self):
        print("\033[H\033[J", end="")

    def move_cursor(self, x: int, y: int):
        print("\033[%d;%dH" % (y, x), end="")

    def hide_cursor(self):
        print("\x1b[?25l", end="")

    def show_cursor(self):
        print("\x1b[?25h", end="")

    def colour(self, text: str, code: str):
        print(f"\033[{code}m{text}\033[0m")

    def lsdir(self):
        files = os.listdir()

        if not self._show_hidden_files:
            files = [
                file
                for file in files
                if not file.startswith(".") or file == ".gitignore"
            ]

        dir_files = []
        ndir_files = []

        for file in files:
            if os.path.isdir(file):
                dir_files.append(file)
            else:
                ndir_files.append(file)

        files = sorted(dir_files) + sorted(ndir_files)
        return files

    def draw_directory(self):
        self.move_cursor(0, 0)

        cwd = os.getcwd()

        if config.HOME_TILDA:
            pwd = os.path.expanduser("~")

            if cwd.startswith(pwd):
                pretty_dir = cwd.replace(pwd, "~")
            else:
                pretty_dir = cwd
        else:
            pretty_dir = cwd

        self.colour("\033[K" + pretty_dir, config.DIRECTORY_DISPLAY_COLOUR)

    def print_file(self, file: str, index: int):
        if os.path.isdir(file):
            file_colour = config.DIRECTORY_COLOUR
            icon_colour = config.DIRECTORY_COLOUR
            is_dir = True
            icon = icons.DIRECTORY_ICON
        else:
            file_colour = config.FILE_COLOUR
            is_dir = False
            extension = file.split(".")[-1]

            if extension in config.IMAGE_EXTENSIONS:
                icon = icons.IMAGE_FILE
                icon_colour = config.MEDIA_COLOUR
            elif extension in config.VECTOR_EXTENSIONS:
                icon = icons.VECTOR_FILE
                icon_colour = config.MEDIA_COLOUR
            elif extension in config.MUSIC_EXTENSIONS:
                icon = icons.MUSIC_FILE
                icon_colour = config.MEDIA_COLOUR
            elif extension in config.VIDEO_EXTENSIONS:
                icon = icons.VIDEO_FILE
                icon_colour = config.MEDIA_COLOUR
            elif extension in config.ADVANCED_TEXT:
                icon = icons.ADVANCED_TEXT
                icon_colour = config.TEXTS_COLOUR
            elif extension in config.C_EXTENSIONS:
                icon = icons.C_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.CPP_EXTENSIONS:
                icon = icons.CPLUSPLUS_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.HASKELL_EXTENSIONS:
                icon = icons.HASKELL_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.HTML_EXTENSIONS:
                icon = icons.HTML_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.JSON_EXTENSIONS:
                icon = icons.JSON_FILE
                icon_colour = config.TEXTS_COLOUR
            elif extension in config.JAVA_EXTENSIONS:
                icon = icons.JAVA_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.JS_EXTENSIONS:
                icon = icons.JS_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.PYTHON_EXTENSIONS:
                icon = icons.PYTHON_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.REACT_EXTENSIONS:
                icon = icons.REACT_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.RUBY_EXTENSIONS:
                icon = icons.RUBY_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.SCRIPT_EXTENSIONS:
                icon = icons.SCRIPT_FILE
                icon_colour = config.PROGRAMS_COLOUR
            elif extension in config.CONFIG_EXTENSIONS or file.endswith("rc"):
                icon = icons.CONFIG
                icon_colour = config.PROGRAMS_COLOUR
            elif file.lower() == "makefile":
                icon = icons.MAKEFILE
                icon_colour = config.PROGRAMS_COLOUR
            elif file == ".gitignore":
                icon = icons.CONFIG
                icon_colour = config.PROGRAMS_COLOUR
            else:
                icon = icons.FILE_ICON
                icon_colour = config.FILE_COLOUR

        cwd = os.getcwd()
        if cwd not in self._selected:
            self._selected[cwd] = []
        if cwd in self._selected:
            leading_space = "\033[47m+\033[0m" if file in self._selected[cwd] else " "
        # if len(file) > os.get_terminal_size()[1]-3:
        # file =
        if self._display_index == index:
            print(
                f"{leading_space}\033[K\033[{icon_colour}m{icon} \033[0m\033[30;47m{file}\033[0m{'/' if is_dir else ''}"
            )
        else:
            print(
                f"{leading_space}\033[K\033[{icon_colour}m{icon} \033[0m\033[{file_colour}m{file}\033[0m{'/' if is_dir else ''}"
            )

    def draw_files(self):
        self.move_cursor(0, 3)

        if not self._display_files:
            files = self.lsdir()
        else:
            files = self._display_files
        show_files = files[self._min_view : self._max_view]

        for index, file in enumerate(show_files):
            self.move_cursor(0, 3 + index)
            self.print_file(file, index)

        if self._min_view > 0:
            self.move_cursor(0, 2)
            print("\033[K" + icons.ARROW_UP)
        else:
            self.move_cursor(0, 2)
            print("\033[K")

        if len(self.lsdir()) > self._max_view:
            self.move_cursor(0, os.get_terminal_size()[1] - 3)
            print("\033[K" + icons.ARROW_DOWN)
        else:
            self.move_cursor(0, os.get_terminal_size()[1] - 3)
            print("\033[K")

        self._display_files = None

    def format_size(self, size_bytes: int):
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s%s" % (int(s), size_name[i])

    def draw_footer(self):
        x, y = os.get_terminal_size()

        self.move_cursor(0, y - 1)
        self.move_cursor(0, y - 1)

        files = self.lsdir()
        if len(files) != 0:
            file = files[self._selected_index]

            formatted_size = self.format_size(os.path.getsize(file))

            self.colour(
                f"\033[K{self._selected_index+1}/{len(self.lsdir())} {time.strftime(config.DATE_FORMAT, time.gmtime(os.stat(file).st_mtime))} {formatted_size}",
                config.FOOTER_COLOUR,
            )
        else:
            self.colour("0/0", "34")


class Lfb:
    def __init__(self):
        self._draw = Draw()
        self._previous_letter = 0

        self._clipboard = ""
        self._clipboard_mode = ""

        while 1:
            try:
                self.keys()
            except KeyboardInterrupt:
                self.exit()

    def cwd_files_length(self) -> int:
        files = self._draw.lsdir()

        return len(files)

    def draw_screen(self):
        self._draw.clear()
        self._draw.draw_directory()
        self._draw.draw_files()
        self._draw.draw_footer()

    def draw_files(self):
        self._draw.draw_files()
        self._draw.draw_footer()

    def open_editor(self, file: str = None):
        if not file:
            files = self._draw.lsdir()
            file = files[self._draw._selected_index]

        call([config.EDITOR, file])

        self._draw.hide_cursor()
        self.draw_screen()

    def forward(self):
        files = self._draw.lsdir()
        if len(files) > 0:
            file = files[self._draw._selected_index]

            if os.path.isdir(file):
                os.chdir(file)

                self._draw._selected_index = 0
                self._draw._display_index = 0

                self._draw._min_view = 0
                self._draw._max_view = os.get_terminal_size()[1] - 6

                self.draw_screen()

            else:
                extension = file.split(".")[-1]

                if extension in config.IMAGE_EXTENSIONS:
                    os.system(f"{config.IMAGE_PROGRAM} '{file}'")
                elif extension in ("pdf"):
                    os.system(f"zathura '{file}' &")
                    self._draw.clear()
                    self.draw_screen()
                elif extension in ("mp4", "mkv", "webm", "mov", "gif", "mp3", "wav"):
                    self._draw.clear()
                    os.system(f"mpv '{file}' &")
                    self.draw_screen()
                else:
                    self.open_editor(file)

    def back_directory(self):
        cwd = os.getcwd()
        old_dir = cwd.split("/")[-1]

        if cwd != "/":
            os.chdir("..")
        else:
            return

        files = self._draw.lsdir()

        self._draw._selected_index = [i for i, f in enumerate(files) if old_dir == f][0]

        if self.cwd_files_length() > os.get_terminal_size()[1] - 6:
            self._draw._display_index = (
                2 if self._draw._selected_index - 2 > 0 else self._draw._selected_index
            )
            self._draw._min_view = (
                self._draw._selected_index - 2
                if self._draw._selected_index - 2 > 0
                else 0
            )
        else:
            self._draw._display_index = self._draw._selected_index
            self._draw._min_view = 0
        self._draw._max_view = self._draw._min_view + os.get_terminal_size()[1] - 6

        self.draw_screen()

    def delete_file(self, file):
        if os.path.isdir(file):
            if len(os.listdir(file)) == 0:
                os.rmdir(file)
            else:
                self._draw.show_cursor()
                cmd = input("Confirm [y/n]: ")
                self._draw.hide_cursor()
                if cmd.lower() in ("y"):
                    shutil.rmtree(file)

        else:
            os.remove(file)

    def delete(self):
        cwd = os.getcwd()

        if len(self._draw._selected[cwd]) > 0:
            for file in self._draw._selected[cwd]:
                self.delete_file(file)
                file_index = [
                    i for i, f in enumerate(self._draw._selected[cwd]) if f == file
                ]
                if len(file_index) > 0:
                    file_index = file_index[0]

        else:
            files = self._draw.lsdir()
            file = files[self._draw._selected_index]

            self.delete_file(file)

        if self._draw._selected_index != 0:
            self._draw._selected_index -= 1
            self._draw._display_index -= 1

        self.draw_screen()

    def make_dir(self):
        self._draw.move_cursor(0, os.get_terminal_size()[1])
        self._draw.show_cursor()
        dir_name = input("Directory Name: ")
        self._draw.hide_cursor()
        if dir_name != "":
            os.mkdir(dir_name)

        self.draw_screen()

    def touch_file(self):
        self._draw.move_cursor(0, os.get_terminal_size()[1])
        self._draw.show_cursor()
        file_name = input("File Name: ")
        self._draw.hide_cursor()
        if file_name != "":
            with open(file_name, "a") as f:
                f.close()

        self.draw_screen()

    def paste_file(self, original, full_path):
        if self._clipboard_mode == "copy":
            if os.path.isdir(original):
                shutil.copytree(original, full_path)
            else:
                shutil.copy(original, full_path)
        elif self._clipboard_mode == "cut":
            if os.path.isdir(original):
                shutil.copytree(original, full_path)
            else:
                shutil.copy(original, full_path)

            # Change to self.delete()
            if os.path.isdir(original):
                if len(os.listdir(original)) == 0:
                    os.rmdir(original)
                else:
                    shutil.rmtree(original)
            else:
                os.remove(original)

    def paste(self):
        if self._clipboard:
            cwd = os.getcwd()

            if isinstance(self._clipboard, str):
                full_path = cwd + "/" + self._clipboard.split("/")[-1]
                self.paste_file(self._clipboard, full_path)
            else:
                for file in self._clipboard:
                    full_path = cwd + "/" + file.split("/")[-1]
                    self.paste_file(file, full_path)

            self.draw_screen()

    def copy(self, mode: str):
        cwd = os.getcwd()
        if len(self._draw._selected[cwd]) == 0:
            files = self._draw.lsdir()
            file = files[self._draw._selected_index]

            self._clipboard = cwd + "/" + file
            self._clipboard_mode = mode
        else:
            self._clipboard = [(cwd + "/" + file) for file in self._draw._selected[cwd]]

        x, y = os.get_terminal_size()

        self._draw.move_cursor(0, y - 1)
        print(" " * int(x / 2))
        self._draw.move_cursor(0, y - 1)
        self._clipboard_mode = mode
        if mode == "copy":
            print("Yanked")
        elif mode == "cut":
            print("Cut")

    def rename(self):
        files = self._draw.lsdir()
        file = files[self._draw._selected_index]

        self._draw.show_cursor()
        new_name = input("Rename: ")
        self._draw.hide_cursor()

        if new_name == "":
            self.draw_screen()
            return

        self._draw.move_cursor(0, os.get_terminal_size()[1])
        os.rename(file, new_name)

        self.draw_screen()

    def scroll_up(self):
        if self._draw._selected_index != 0:
            self._draw._selected_index -= 1
            self._draw._display_index -= 1

        if self._draw._display_index <= 1:
            if self._draw._min_view > 0:
                self._draw._max_view -= 1
                self._draw._min_view -= 1
                self._draw._display_index += 1
                self.draw_files()
                return

        self._draw.draw_files()
        self._draw.draw_footer()

    def scroll_down(self):
        if self._draw._selected_index != self.cwd_files_length() - 1:
            self._draw._selected_index += 1
            self._draw._display_index += 1

        if self._draw._display_index >= self._draw._max_view - self._draw._min_view - 2:
            if self._draw._max_view < self.cwd_files_length():
                self._draw._max_view += 1
                self._draw._min_view += 1
                self._draw._display_index -= 1
                self.draw_files()
                return

        self._draw.draw_files()
        self._draw.draw_footer()

    def shift_down(self):
        if self._draw._max_view < self.cwd_files_length():
            self._draw._max_view += 1
            self._draw._min_view += 1
            if self._draw._display_index > 2:
                self._draw._display_index -= 1
            else:
                self._draw._selected_index += 1
            self.draw_files()
            return

    def shift_up(self):
        if self._draw._min_view > 0:
            self._draw._max_view -= 1
            self._draw._min_view -= 1
            if self._draw._display_index < os.get_terminal_size()[1] - 9:
                self._draw._display_index += 1
            else:
                self._draw._selected_index -= 1
            self.draw_files()
            return

    def help_screen(self):
        self._draw.move_cursor(0, 3)
        print("\033[K\033[1mMovement:")
        print("\033[K\t\033[1mh:\033[0m Backwards")
        print("\033[K\t\033[1ml:\033[0m Forwards")
        print("\033[K\t\033[1mj:\033[0m Down")
        print("\033[K\t\033[1mk:\033[0m Up")
        print("\033[K\t\033[1mg:\033[0m Top of Directory")
        print("\033[K\t\033[1mG:\033[0m Bottom of Directory")
        print("\033[K\t\033[1mH:\033[0m Top of Current View")
        print("\033[K\t\033[1mM:\033[0m Middle of Current View")
        print("\033[K\t\033[1mL:\033[0m Bottom of Current View")
        print("\033[K\033[1mFiles:")
        print("\033[K\t\033[1mmf:\033[0m Create a File")
        print("\033[K\t\033[1mmd:\033[0m Create a Directory")
        print("\033[K\t\033[1myy:\033[0m Copy a File")
        print("\033[K\t\033[1mdd:\033[0m Cut a File")
        print("\033[K\t\033[1mpp:\033[0m Paste a File")
        print("\033[K\t\033[1mrm:\033[0m Remove File")
        print("\033[K\t\033[1mcw:\033[0m Rename File")
        print("\033[K\033[1mCommands:")
        print("\033[K\t\033[1m':':\033[0m Built in Commands")
        print("\033[K\t\033[1m'!':\033[0m Bash Command")

        input("\nPress Enter to Continue...")
        self.draw_screen()

    def keys(self):
        k = click.getchar()
        c = ord(k[0]) if len(k) == 1 else ord(k[-1])

        if c == 65 or c == 107:
            self.scroll_up()
        elif c == 66 or c == 106:
            self.scroll_down()
        elif c == 25:
            self.shift_up()
        elif c == 5:
            self.shift_down()
        elif c == 72:
            if self._draw._min_view != 0:
                self._draw._display_index = 2
            else:
                self._draw._display_index = 0
            self._draw._selected_index = (
                self._draw._min_view + self._draw._display_index
            )
            self._draw.draw_files()
            self._draw.draw_footer()
        elif c == 76:
            if self.cwd_files_length() < self._draw._max_view:
                self._draw._display_index = self.cwd_files_length() - 1
                self._draw._selected_index = self._draw._display_index
            else:
                self._draw._display_index = os.get_terminal_size()[1] - 9
                self._draw._selected_index = self._draw._max_view - 3
            self._draw.draw_files()
            self._draw.draw_footer()
        elif c == 77:
            if self.cwd_files_length() < self._draw._max_view:
                self._draw._display_index = 0
                self._draw._selected_index = 0
                self._draw._display_index = int(self.cwd_files_length() / 2)
                self._draw._selected_index = int(self.cwd_files_length() / 2)
            else:
                self._draw._display_index = int((os.get_terminal_size()[1] - 6) / 2)
                self._draw._selected_index = (
                    self._draw._min_view + self._draw._display_index
                )
            self._draw.draw_files()
            self._draw.draw_footer()
        elif c == 9:
            if self.cwd_files_length() > self._draw._max_view:
                incr = int((os.get_terminal_size()[1] - 6) / 2)
                self._draw._selected_index += incr
                self._draw._min_view += incr
                self._draw._max_view += incr
                self.draw_screen()
        elif c == 21:
            if self.cwd_files_length() > self._draw._max_view:
                incr = int((os.get_terminal_size()[1] - 6) / 2)
                self._draw._selected_index -= incr
                self._draw._min_view -= incr
                self._draw._max_view -= incr
                self.draw_screen()

        elif c == 108 or c == 13:
            self.forward()
        elif c == 104:
            self.back_directory()
        elif c == 100 and self._previous_letter == 109:
            self.make_dir()
        elif c == 102 and self._previous_letter == 109:
            self.touch_file()
        elif c == 119 and self._previous_letter == 99:
            self.rename()
        elif c == 121 and self._previous_letter == 121:
            self.copy(mode="copy")
        elif c == 100 and self._previous_letter == 100:
            self.copy(mode="cut")
        elif c == 112 and self._previous_letter == 112:
            self.paste()
        elif c == 109 and self._previous_letter == 114:
            self.delete()
        elif c == 101:
            self.open_editor()
        elif c == 111:
            files = self._draw.lsdir()
            file = files[self._draw._selected_index]
            os.system(f"{config.IMAGE_PROGRAM} '{file}'")
        elif c == 32:
            files = self._draw.lsdir()
            file = files[self._draw._selected_index]
            cwd = os.getcwd()
            if cwd in self._draw._selected:
                if file not in self._draw._selected[cwd]:
                    self._draw._selected[cwd].append(file)
                elif file in self._draw._selected[cwd]:
                    file_index = [
                        i for i, f in enumerate(self._draw._selected[cwd]) if f == file
                    ]
                    if len(file_index) > 0:
                        file_index = file_index[0]
                        self._draw._selected[cwd].pop(file_index)
            else:
                self._draw._selected[cwd] = []
            self.scroll_down()
            self.draw_files()
        elif c == 103:
            self._draw._selected_index = 0
            self._draw._display_index = 0

            self._draw._min_view = 0
            self._draw._max_view = os.get_terminal_size()[1] - 6

            self._draw.draw_files()
            self._draw.draw_footer()

            self._draw.move_cursor(0, 2)
            print("\033[K")
        elif c == 71:
            self._draw._selected_index = self.cwd_files_length() - 1
            bottom_size = os.get_terminal_size()[1] - 7
            if self.cwd_files_length() - 1 < bottom_size:
                self._draw._display_index = self.cwd_files_length() - 1
            else:
                self._draw._display_index = os.get_terminal_size()[1] - 7
                self._draw._min_view = self.cwd_files_length() - (
                    os.get_terminal_size()[1] - 6
                )
                self._draw._max_view = self.cwd_files_length()

            self._draw.draw_footer()
            self._draw.draw_files()

            self._draw.move_cursor(0, os.get_terminal_size()[1] - 3)
            print("\033[K")
        elif c == 58:
            self._draw.move_cursor(0, os.get_terminal_size()[1])
            self._draw.show_cursor()
            cmd = input(":")
            self._draw.hide_cursor()
            if cmd != "":
                if cmd[-1].lower() == "g":
                    line = list(cmd)
                    line.pop(-1)
                    self._draw._selected_index = int("".join(line)) - 1
                    self._draw._display_index = 2
                    self._draw._min_view = self._draw._selected_index - 2
                    self._draw._max_view = (
                        self._draw._min_view + os.get_terminal_size()[1] - 6
                    )
                    self.draw_screen()
                elif cmd.lower() == "q":
                    self._draw.clear()
                    self.exit()
        elif c == 33:
            self._draw.move_cursor(0, os.get_terminal_size()[1])
            self._draw.show_cursor()
            cmd = input("!")
            os.system(cmd)
            self._draw.hide_cursor()
            self.draw_screen()
        elif c == 47:
            self._draw.move_cursor(0, os.get_terminal_size()[1])
            self._draw.show_cursor()
            cmd = input("/")

            if cmd != "":
                files = self._draw.lsdir()

                files = [i for i, f in enumerate(files) if f.startswith(cmd)]
                if len(files) > 0:
                    self._draw._selected_index = files[0]

                    if self.cwd_files_length() > os.get_terminal_size()[1] - 6:
                        self._draw._display_index = (
                            2
                            if self._draw._selected_index - 2 > 0
                            else self._draw._selected_index
                        )
                        self._draw._min_view = (
                            self._draw._selected_index - 2
                            if self._draw._selected_index - 2 > 0
                            else 0
                        )
                    else:
                        self._draw._display_index = self._draw._selected_index
                        self._draw._min_view = 0
                    self._draw._max_view = (
                        self._draw._min_view + os.get_terminal_size()[1] - 6
                    )
                    self._draw.hide_cursor()
                    self.draw_screen()

                else:
                    self._draw.hide_cursor()
                    self.draw_screen()

                    self._draw.move_cursor(0, os.get_terminal_size()[1] - 1)
                    print("\033[K\033[31mError Not Found\033[0m")

        elif c == 100 and self._previous_letter == 99:
            self._draw._selected_index = 0
            self._draw._display_index = 0
            self._draw._min_view = 0
            self._draw._max_view = os.get_terminal_size()[1] - 6
            os.chdir(os.path.expanduser("~"))

            self._previous_letter = 0

            self.draw_screen()

        elif c == 102 and self._previous_letter == 99:
            self._draw._selected_index = 0
            self._draw._display_index = 0
            self._draw._min_view = 0
            self._draw._max_view = os.get_terminal_size()[1] - 6
            os.chdir(os.path.expanduser("~") + "/" + ".config")

            self._previous_letter = 0

            self.draw_screen()

        elif c == 115 and self._previous_letter == 100:
            self._draw._selected_index = 0
            self._draw._display_index = 0
            self._draw._min_view = 0
            self._draw._max_view = os.get_terminal_size()[1] - 6
            os.chdir(os.path.expanduser("~") + "/" + "Documents")

            self._previous_letter = 0

            self.draw_screen()

        elif c == 127:
            self._draw._show_hidden_files = (
                False if self._draw._show_hidden_files else True
            )
            self._draw._selected_index = 0
            self._draw._display_index = 0
            self.draw_screen()
        elif c == 102 and self._previous_letter == 114:
            self.draw_screen()
        elif c == 27:
            self._previous_letter = 0
        elif c == 63:
            self.help_screen()
        elif c == 113:
            self._draw.clear()
            self.exit()
        self._previous_letter = c

    def exit(self):
        self._draw.clear()
        self._draw.show_cursor()
        sys.exit()


if __name__ == "__main__":
    lfb = Lfb()
    lfb.keys()
