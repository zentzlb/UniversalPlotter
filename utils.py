import functools
from tkinter import messagebox


def catch(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyError as e:

            messagebox.showerror('KeyError', e.__cause__.__str__())

    return wrapper
