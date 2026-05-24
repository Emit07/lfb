import os
import shutil
import math
from pathlib import Path

class FileSystem:
    """
    Wraps all OS interactions. Never draws anything, never reads input.
    Returns plain data (lists, strings, ints).
    """

    def list_dir(self, show_hidden: bool) -> list[str]:
        files = os.listdir()

        if not show_hidden:
            files = [f for f in files if not f.startswith(".") or f == ".gitignore"]

        dirs  = sorted(f for f in files if os.path.isdir(f))
        nondirs = sorted(f for f in files if not os.path.isdir(f))
        return dirs + nondirs
    
    # TODO introduce future compatibility with pathlib
    def getsize(self, path: str | Path) -> int:
        path = Path(path)

        if path.is_file():
            return os.path.getsize(path)

        if path.is_dir():
            total = 0

            for root, _, files in os.walk(path):
                for file in files:
                    file_path = Path(root) / file

                    try:
                        total += os.path.getsize(file_path)
                    except (FileNotFoundError, PermissionError):
                        pass
            
            # TODO should it be total + 4KB?
            return total

        raise FileNotFoundError(f"{path} does not exist")

    
    # TODO Move to renderer
    def format_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0B"
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        s = round(size_bytes / math.pow(1024, i), 2)
        return f"{int(s)}{units[i]}"

    # TODO Move to renderer
    def pretty_cwd(self, use_tilda: bool) -> str:
        cwd = os.getcwd()
        if use_tilda:
            home = os.path.expanduser("~")
            if cwd.startswith(home):
                return cwd.replace(home, "~", 1)
        return cwd

    def file_stat(self, path: str) -> os.stat_result:
        return os.stat(path)

    def chdir(self, path: str):
        os.chdir(path)

    def mkdir(self, name: str):
        os.mkdir(name)

    def touch(self, name: str):
        open(name, "a").close()

    def rename(self, old: str, new: str):
        os.rename(old, new)

    def delete(self, path: str, confirmed: bool = False) -> bool:
        """
        Returns True if deletion happened, False if it was cancelled.
        confirmed=True skips the non-empty directory prompt.
        """
        if os.path.isdir(path):
            if not os.listdir(path) or confirmed:
                shutil.rmtree(path)
                return True
            return False   # caller must ask user and retry with confirmed=True
        else:
            os.remove(path)
            return True

    def copy(self, src: str, dst: str):
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)

    def move(self, src: str, dst: str):
        self.copy(src, dst)
        self.delete(src, confirmed=True)
