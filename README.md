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

This program only works from the terminal.

to use run with

```
python3 lfb.py
```

Until I make the program installable, I have it aliased in my bashrc

```
alias lfb="~/Documents/lfb/lfb.py"
```

## TODOs

* [ ] Fix scrolling view
* [ ] finish moving over commands that are in the keymap
* [ ] improve integrity in filesystem interactions
* [ ] move the keymap so that users can define it, make a command map as well so users do not get direct access
* [ ] do the same thing with the icons, though this doesnt need a map since they do not have access to App class
* [ ] Seperate the icons, colors, and extensions into different files or at least a seperate file from the user config
* [ ] refactor some code and clean it up
* [ ] Move the size calculating functions and formatting functions from filesystem to renderer
* [ ] Restructure rendering library, preferabbly transfer it to curses or something from scratch (no click)
* [ ] Comment code and write docs
