from os.path import dirname, basename, isfile, join
import glob
from typing import Callable
from types import ModuleType
from os import getcwd

files: list[str] = glob.glob(join(dirname(__file__), "*.py"))
imports: list[str] = [basename(f)[:-3] for f in files if isfile(f) and not f.endswith('__init__.py')]
modules: list[ModuleType] = [__import__(imp) for imp in imports]
functions: list[Callable] = [fn[1] for mod in modules for fn in mod.__dict__.items() if callable(fn[1])]
__all__ = [fn.__name__ for fn in functions]

print(__all__)
