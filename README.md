# lfb

lfb (light file browser) is a terminal file browser. The whole program is a mess as of now. In the feature I will remove the need for external dependencies, tidy up the code, make an actual readme, add documentation, and change the name.

[WARNING] the source for this program is a mess, look at it at your own risk.

## Dependencies

There is one dependency being used right now.

To install it use

```
pip install click
```

## Executing

You can manually build and install it with the following commands:

```
python -m build
pip install dist/lfb-0.1.0-py3-none-any.whl
```

You can also execute it manually

```
python3 lfb/main.py
```

## TODOs

* [x] Fix scrolling view
* [ ] finish moving over commands that are in the keymap
* [ ] improve integrity in filesystem interactions
* [x] move the keymap so that users can define it, make a command map as well so users do not get direct access
* [ ] do the same thing with the icons, though this doesnt need a map since they do not have access to App class
* [x] Fix loading flash
* [ ] Seperate the icons, colors, and extensions into different files or at least a seperate file from the user config
* [ ] refactor some code and clean it up
* [ ] Move the size calculating functions and formatting functions from filesystem to renderer
* [ ] Restructure rendering library, preferabbly transfer it to curses or something from scratch (no click)
* [ ] Comment code and write docs
* [x] make it so when selecting a file you see the size of it and all its contents. Right now whenever you selecte a file it just says 4KB
* [ ] When you exit out of a directory the size says 4KB, but normally it says its actual size
* [x] If the directories are large the program stops working until it recursively calculates the size
* [ ] Fix the arrow hints when scrolling (right now the bottom one is always on display and the top one is never on display)
* [ ] Fix slow rendering on startup
* [ ] fix magic numbers especially on the rendering side of things
* [ ] fix _viewbottom and jumps and all that and magic numbers

