import sys
import os
import importlib

def delete_path(dir_path):
    for path in sys.path:
        if path == dir_path:
            sys.path.remove(path)

    for module in list(sys.modules):
        if module.startswith('src'):
            del sys.modules[module]

def get_dir_path():
    return os.path.dirname(os.path.abspath(__file__))

def onMaxDroppedPythonFile():
    SetupIKUI.start()

# Function called when a Python file is dropped into Maya
def onMayaDroppedPythonFile(*args, **kwargs):
    SetupIKUI.start()
    pass

dir_path = get_dir_path()

if dir_path != sys.path[0]:
    sys.path.insert(0, dir_path)


if not dir_path in sys.path:
    sys.path.append(dir_path)

from src.ui import SetupIKUI