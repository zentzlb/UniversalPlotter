# import extensions.my_fn as f
#
# while True:
#     x = int(input('enter number'))
#     print([fn[1](x) for fn in f.__dict__.items() if callable(fn[1])])

from os.path import dirname, basename, isfile, join
import sys
from os import getcwd
import glob

def check_function(fn: object) -> bool:
    """

    :param fn:
    :return:
    """
    pass

sys.path.insert(0, getcwd())
print('starting')
dir_path = getcwd()
print(dir_path)
files = glob.glob(join(dir_path, "*.py"))
imports = [basename(f)[:-3] for f in files if isfile(f)]
print(imports)
modules = [__import__(imp) for imp in imports]
functions = [fn[1] for mod in modules for fn in mod.__dict__.items() if callable(fn[1])]

# while True:
x = int(input('enter number: '))
try:
    pass
    # print([fn(x) for fn in functions])
except ImportError as e:
    print(e)
    # print([fn(x) for fn in functions])
# modules = glob.glob(join(dirname(__file__)+'/extensions2', "*.py"))
#
# print(modules)
