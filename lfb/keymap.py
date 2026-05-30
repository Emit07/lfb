import os
from pathlib import Path
from typing import Callable

from lfb.config import load_toml, USER_KEYMAP_PATH

ACTION_MAP: dict[str, str] = {
    "scroll_up":       "_scroll_up",
    "scroll_down":     "_scroll_down",
    "shift_up":        "_shift_up",
    "shift_down":      "_shift_down",
    "go_top":          "_go_top",
    "go_bottom":       "_go_bottom",
    "view_top":        "_view_top",
    "view_middle":     "_view_middle",
    "view_bottom":     "_view_bottom",
    "forward":         "_forward",
    "back":            "_back",
    "open_editor":     "_open_editor",
    "toggle_selected": "_toggle_selected",
    "toggle_hidden":   "_toggle_hidden",
    "exit":            "_exit",
    "make_dir":        "_make_dir",
    "touch_file":      "_touch_file",
    "rename":          "_rename",
    "copy":            "_copy",
    "paste":           "_paste",
    "delete":          "_delete",
    "cd":              "_chdir",
}

SPECIAL_KEYS: dict[str, int] = {
    "↑": 65, "↓": 66, "DEL": 127, "\\n": 13,
    **{f"^{c}": i for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ", 1)},
}

DEFAULT_PATH = USER_KEYMAP_PATH


def _parse_key(s: str) -> int:
    if s in SPECIAL_KEYS:
        return SPECIAL_KEYS[s]
    if len(s) == 1:
        return ord(s)
    raise ValueError(f"Unrecognised key {s!r}")


def _bind(app, action_name: str, arg: str | None) -> Callable:
    if action_name not in ACTION_MAP:
        raise ValueError(f"Unknown action: {action_name!r}")
    method = getattr(app, ACTION_MAP[action_name])
    if arg is None:
        return method
    path = os.path.expanduser(arg) if action_name == "cd" else arg
    return lambda: method(path)


def load_keymap(
    app,
    config_path: Path | str | None = None,
) -> tuple[dict[int, Callable], dict[tuple[int, int], Callable], str | None]:

    path = Path(config_path).expanduser() if config_path else USER_KEYMAP_PATH.expanduser()
    raw, _, warning = load_toml("keymap.toml", path)

    def unpack(v):
        return (v[0], v[1]) if isinstance(v, list) else (v, None)

    keymap = {
        _parse_key(k): _bind(app, *unpack(v))
        for k, v in raw.get("keys", {}).items()
    }

    combo_map = {
        tuple(_parse_key(k) for k in combo.split(",")): _bind(app, *unpack(v))
        for combo, v in raw.get("combos", {}).items()
    }

    return keymap, combo_map, warning





















"""
from app import *

KEYMAP: dict[int, callable] = {
        # Movement
        65:  self._scroll_up,       # ↑
        107: self._scroll_up,       # k
        66:  self._scroll_down,     # ↓
        106: self._scroll_down,     # j
        25:  self._shift_up,        # Ctrl-Y
        5:   self._shift_down,      # Ctrl-E
        103: self._go_top,          # g
        71:  self._go_bottom,       # G
        72:  self._view_top,        # H
        77:  self._view_middle,     # M
        76:  self._view_bottom,     # L
        # TODO 9:   self._half_page_down,  # Tab
        # TODO 21:  self._half_page_up,    # Ctrl-U
        # Navigation
        108: self._forward,         # l
        13:  self._forward,         # Enter
        104: self._back,            # h
        # Misc
        101: self._open_editor,     # e
        32:  self._toggle_selected, # Space
        127: self._toggle_hidden,   # Del
        # TODO
        #58:  self._command_mode,    # :
        #33:  self._shell_mode,      # !
        #47:  self._search_mode,     # /
        #63:  self._help,            # ?
        113: self._exit,            # q
        }

COMBO_MAP: dict[tuple[int, int], callable] = {
        (109, 100): self._make_dir,               # md
        (109, 102): self._touch_file,             # mf
        (99,  119): self._rename,                 # cw
        (121, 121): lambda: self._copy("copy"),   # yy
        (100, 100): lambda: self._copy("cut"),    # dd
        (112, 112): self._paste,                  # pp
        (114, 109): self._delete,                 # rm
        (99,  100): lambda: self._reset_and_chdir(os.path.expanduser("~")),           # cd
        (99,  102): lambda: self._reset_and_chdir(os.path.expanduser("~/.config")),   # cf
        (100, 115): lambda: self._reset_and_chdir(os.path.expanduser("~/Documents")), # ds
        }

def resolve(keypress: int) -> callable:


"""

