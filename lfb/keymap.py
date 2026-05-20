import os
import tomllib
from pathlib import Path
from typing import Callable

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
    "cd":              "_reset_and_chdir",
}

ACTIONS_WITH_ARG = {"copy", "cd"}

SPECIAL_KEYS: dict[str, int] = {
    "↑":   65,
    "↓":   66,
    "DEL": 127,
    "\\n": 13,
    "^A":  1,  "^B":  2,  "^C":  3,  "^D":  4,  "^E":  5,
    "^F":  6,  "^G":  7,  "^H":  8,  "^I":  9,  "^J":  10,
    "^K":  11, "^L":  12, "^M":  13, "^N":  14, "^O":  15,
    "^P":  16, "^Q":  17, "^R":  18, "^S":  19, "^T":  20,
    "^U":  21, "^V":  22, "^W":  23, "^X":  24, "^Y":  25,
    "^Z":  26,
}


def _parse_key(s: str) -> int:
    if s in SPECIAL_KEYS:
        return SPECIAL_KEYS[s]
    if len(s) == 1:
        return ord(s)
    raise ValueError(
        f"Unrecognised key {s!r} — use a single character, "
        f"an arrow (↑ ↓), DEL, or a ctrl sequence like ^Y."
    )


def _resolve_action(app, action_name: str, arg: str | None = None) -> Callable:
    if action_name not in ACTION_MAP:
        raise ValueError(
            f"Unknown action: {action_name!r}. "
            f"Run with --list-actions to see valid options."
        )

    method = getattr(app, ACTION_MAP[action_name])

    if arg is not None:
        if action_name not in ACTIONS_WITH_ARG:
            raise ValueError(f"Action {action_name!r} does not accept arguments.")
        if action_name == "cd":
            path = os.path.expanduser(arg)
            return lambda: method(path)
        return lambda: method(arg)

    return method


def load_keymap(
    app,
    config_path: Path | None = None,
) -> tuple[dict[int, Callable], dict[tuple[int, int], Callable], str | None]:
    if config_path is None:
        config_path = Path(os.environ.get(
            "FILEBROWSER_CONFIG",
            Path.home() / ".config" / "filebrowser" / "keymap.toml"
        ))

    config_path = Path(config_path).expanduser()

    warning: str | None = None
    default_path = Path.home() / ".config" / "lfb" / "keymap.toml"

    try:
        with open(config_path, "rb") as f:
            raw = tomllib.load(f)
    except FileNotFoundError:
        warning = f"Config file {config_path} not found, using defaults at {default_path}"
        with open(default_path, "rb") as f:
            raw = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"Invalid TOML in {config_path}: {e}")

    keymap: dict[int, Callable] = {}
    for key_str, value in raw.get("keys", {}).items():
        key = _parse_key(key_str)
        action_name, arg = (value[0], value[1]) if isinstance(value, list) else (value, None)
        keymap[key] = _resolve_action(app, action_name, arg)

    combo_map: dict[tuple[int, int], Callable] = {}
    for combo_str, value in raw.get("combos", {}).items():
        k1, k2 = (_parse_key(k) for k in combo_str.split(","))
        action_name, arg = (value[0], value[1]) if isinstance(value, list) else (value, None)
        combo_map[(k1, k2)] = _resolve_action(app, action_name, arg)

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

