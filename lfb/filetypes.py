import os
import lfb.config as config
import lfb.icons as icons

_EXT_MAP: dict[str, tuple[str, str]] = {}

def _register(extensions, icon, colour):
    for ext in (extensions if isinstance(extensions, tuple) else (extensions,)):
        _EXT_MAP[ext] = (icon, colour)


_register(config.IMAGE_EXTENSIONS,   icons.IMAGE_FILE,     config.MEDIA_COLOUR)
_register(config.VECTOR_EXTENSIONS,  icons.VECTOR_FILE,    config.MEDIA_COLOUR)
_register(config.MUSIC_EXTENSIONS,   icons.MUSIC_FILE,     config.MEDIA_COLOUR)
_register(config.VIDEO_EXTENSIONS,   icons.VIDEO_FILE,     config.MEDIA_COLOUR)
_register(config.ADVANCED_TEXT,      icons.ADVANCED_TEXT,  config.TEXTS_COLOUR)
_register(config.JSON_EXTENSIONS,    icons.JSON_FILE,      config.TEXTS_COLOUR)
_register(config.C_EXTENSIONS,       icons.C_FILE,         config.PROGRAMS_COLOUR)
_register(config.CPP_EXTENSIONS,     icons.CPLUSPLUS_FILE, config.PROGRAMS_COLOUR)
_register(config.HASKELL_EXTENSIONS, icons.HASKELL_FILE,   config.PROGRAMS_COLOUR)
_register(config.HTML_EXTENSIONS,    icons.HTML_FILE,      config.PROGRAMS_COLOUR)
_register(config.JAVA_EXTENSIONS,    icons.JAVA_FILE,      config.PROGRAMS_COLOUR)
_register(config.JS_EXTENSIONS,      icons.JS_FILE,        config.PROGRAMS_COLOUR)
_register(config.PYTHON_EXTENSIONS,  icons.PYTHON_FILE,    config.PROGRAMS_COLOUR)
_register(config.REACT_EXTENSIONS,   icons.REACT_FILE,     config.PROGRAMS_COLOUR)
_register(config.RUBY_EXTENSIONS,    icons.RUBY_FILE,      config.PROGRAMS_COLOUR)
_register(config.SCRIPT_EXTENSIONS,  icons.SCRIPT_FILE,    config.PROGRAMS_COLOUR)
_register(config.CONFIG_EXTENSIONS,  icons.CONFIG,         config.PROGRAMS_COLOUR)


def resolve(filename: str) -> tuple[str, str, str]:
    """
    Returns (icon, icon_colour, file_colour) for a given filename.
    The caller uses icon_colour for the icon glyph, file_colour for the name text.
    """
    if os.path.isdir(filename):
        return icons.DIRECTORY_ICON, config.DIRECTORY_COLOUR, config.DIRECTORY_COLOUR

    # Special whole-filename matches first
    if filename.lower() == "makefile":
        return icons.MAKEFILE, config.PROGRAMS_COLOUR, config.FILE_COLOUR
    if filename == ".gitignore":
        return icons.CONFIG, config.PROGRAMS_COLOUR, config.FILE_COLOUR
    if filename.endswith("rc"):
        return icons.CONFIG, config.PROGRAMS_COLOUR, config.FILE_COLOUR

    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    icon, icon_colour = _EXT_MAP.get(ext, (icons.FILE_ICON, config.FILE_COLOUR))
    return icon, icon_colour, config.FILE_COLOUR
