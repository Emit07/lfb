import tomllib
from pathlib import Path

CONFIG_DIR = Path("~/.config/lfb")
USER_CONFIG_PATH = CONFIG_DIR / "config.toml"
USER_KEYMAP_PATH = CONFIG_DIR / "keymap.toml"


def _defaults_dir() -> Path:
    try:
        import importlib.resources as ir

        return Path(ir.files("lfb") / "defaults")
    except (ImportError, ModuleNotFoundError, TypeError):
        return Path(__file__).resolve().parent / "defaults"


def load_toml(name: str, path: Path | str | None = None) -> tuple[dict, Path, str | None]:
    target = Path(path).expanduser() if path else (CONFIG_DIR / name).expanduser()

    if target.is_file():
        return tomllib.loads(target.read_text()), target, None

    bundled = _defaults_dir() / name
    if bundled.is_file():
        warning = f"{target} not found, using bundled defaults"
        return tomllib.loads(bundled.read_text()), bundled, warning

    raise FileNotFoundError(f"Could not find {name} at {target}")


_data, _config_path, CONFIG_WARNING = load_toml("config.toml")

_paths = _data.get("paths", {})
_display = _data.get("display", {})
_programs = _data.get("programs", {})
_colours = _data.get("colours", {})

_keymap_override = _paths.get("keymap", "")
KEYMAP_PATH = Path(_keymap_override).expanduser() if _keymap_override else USER_KEYMAP_PATH.expanduser()

SHOW_HIDDEN_FILES = _display.get("show_hidden_files", False)
DRAW_ICONS = _display.get("draw_icons", False)
DATE_FORMAT = _display.get("date_format", "%d/%m/%Y %H:%M")
HOME_TILDA = _display.get("home_tilda", True)

EDITOR = _programs.get("editor", "vim")
IMAGE_PROGRAM = _programs.get("image_program", "feh")
PDF_READER = _programs.get("pdf_reader", "zathura")

DIRECTORY_DISPLAY_COLOUR = _colours.get("directory_display", "34;4")
FOOTER_COLOUR = _colours.get("footer", "34")
DIRECTORY_COLOUR = _colours.get("directory", "32")
FILE_COLOUR = _colours.get("file", "0")
MEDIA_COLOUR = _colours.get("media", "33")
TEXTS_COLOUR = _colours.get("texts", "0")
PROGRAMS_COLOUR = _colours.get("programs", "36")
