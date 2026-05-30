import os
import lfb.config as config
import lfb.extensions as extensions
import lfb.icons as icons

def _build_ext_map() -> dict[str, tuple[str, str]]:
    groups = [
        (extensions.IMAGE_EXTENSIONS,   icons.IMAGE_FILE,     config.MEDIA_COLOUR),
        (extensions.VECTOR_EXTENSIONS,  icons.VECTOR_FILE,    config.MEDIA_COLOUR),
        (extensions.MUSIC_EXTENSIONS,   icons.MUSIC_FILE,     config.MEDIA_COLOUR),
        (extensions.VIDEO_EXTENSIONS,   icons.VIDEO_FILE,     config.MEDIA_COLOUR),
        (extensions.ADVANCED_TEXT,      icons.ADVANCED_TEXT,  config.TEXTS_COLOUR),
        (extensions.JSON_EXTENSIONS,    icons.JSON_FILE,      config.TEXTS_COLOUR),
        (extensions.C_EXTENSIONS,       icons.C_FILE,         config.PROGRAMS_COLOUR),
        (extensions.CPP_EXTENSIONS,     icons.CPLUSPLUS_FILE, config.PROGRAMS_COLOUR),
        (extensions.HASKELL_EXTENSIONS, icons.HASKELL_FILE,   config.PROGRAMS_COLOUR),
        (extensions.HTML_EXTENSIONS,    icons.HTML_FILE,      config.PROGRAMS_COLOUR),
        (extensions.JAVA_EXTENSIONS,    icons.JAVA_FILE,      config.PROGRAMS_COLOUR),
        (extensions.JS_EXTENSIONS,      icons.JS_FILE,        config.PROGRAMS_COLOUR),
        (extensions.PYTHON_EXTENSIONS,  icons.PYTHON_FILE,    config.PROGRAMS_COLOUR),
        (extensions.REACT_EXTENSIONS,   icons.REACT_FILE,     config.PROGRAMS_COLOUR),
        (extensions.RUBY_EXTENSIONS,    icons.RUBY_FILE,      config.PROGRAMS_COLOUR),
        (extensions.SCRIPT_EXTENSIONS,  icons.SCRIPT_FILE,    config.PROGRAMS_COLOUR),
        (extensions.CONFIG_EXTENSIONS,  icons.CONFIG,         config.PROGRAMS_COLOUR),
    ]
    return {
        ext: (icon, colour)
        for exts, icon, colour in groups
        for ext in (exts if isinstance(exts, tuple) else (exts,))
    }

_EXT_MAP = _build_ext_map()


def resolve(filename: str) -> tuple[str, str, str]:
    if os.path.isdir(filename):
        return icons.DIRECTORY_ICON, config.DIRECTORY_COLOUR, config.DIRECTORY_COLOUR

    name_lower = filename.lower()
    if name_lower == "makefile" or name_lower.endswith("rc") or filename == ".gitignore":
        return icons.CONFIG, config.PROGRAMS_COLOUR, config.FILE_COLOUR

    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    icon, icon_colour = _EXT_MAP.get(ext, (icons.FILE_ICON, config.FILE_COLOUR))
    return icon, icon_colour, config.FILE_COLOUR
