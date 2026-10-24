"""
this thing is used all over the show so ive bundled it into one file, used so I can build the program in pyinstaller
"""

import os, sys

def resource_path(relative_path): # used so program can be built
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)