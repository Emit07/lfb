import os
import lfb.config as config

class ViewState:
    def __init__(self):
        self.selected_index: int = 0      # absolute index into file list
        self.display_index: int = 0       # row on screen (0 = top of view)
        self.show_hidden: bool = config.SHOW_HIDDEN_FILES
        self.previous_key: int = 0        # for two-key combos like 'yy', 'dd'

        term_height = os.get_terminal_size()[1]
        self.min_view: int = 0            # first file index in the scroll window
        self.max_view: int = term_height - 6  # last file index (exclusive)

        # Per-directory multi-select: { "/path/to/dir": ["file1", "file2"] }
        self.selected_files: dict[str, list[str]] = {}

        self._log_active = False

    def reset_viewport(self):
        term_height = os.get_terminal_size()[1]
        self.selected_index = 0
        self.display_index = 0
        self.min_view = 0
        self.max_view = term_height - 6

    def page_height(self) -> int:
        return os.get_terminal_size()[1] - 6
