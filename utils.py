import functools
from tkinter import messagebox
import os
from tkinter import Toplevel, Label
from tkinter import ttk as TTK

import numpy as np
import pandas as pd
from scipy import integrate
from numpy import ndarray

from filters import CFC_filter
from typing import Callable, Any, Tuple
from math import inf


class SimpleChoiceBox:
    def __init__(self, title, text, choices):
        self.t = Toplevel()
        self.t.title(title if title else "")
        self.selection = None
        Label(self.t, text=text if text else "").grid(row=0, column=0)
        self.c = TTK.Combobox(self.t, values=choices, state="readonly")
        self.c.grid(row=0, column=1)
        self.c.bind("<<ComboboxSelected>>", self.combobox_select)

    def combobox_select(self, event):
        self.selection = self.c.get()
        self.t.destroy()


def catch(fn: Callable) -> Callable:
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except KeyError as e:
            messagebox.showerror('KeyError', e.__str__())
        except TypeError as e:
            messagebox.showerror('TypeError', e.__str__())
        except ValueError as e:
            messagebox.showerror('ValueError', e.__str__())
        except NameError as e:
            messagebox.showerror('NameError', e.__str__())
        except ZeroDivisionError as e:
            messagebox.showerror('ZeroDivisionError', e.__str__())

    return wrapper


def enumerator(fn: Callable[[Any], str]) -> Callable[[Any], str]:
    """
    count number of string occurrences and adds enumeration
    :param fn: string returning function
    :return: string returning function with enumerator
    """
    my_list = []

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        my_list.append(string := fn(*args, **kwargs))
        return string + f'({my_list.count(string)})'

    return wrapper


def check_file(path: str) -> bool:
    """
    determines whether file is csv or binout
    :param path: full file path
    :return:
    """
    filename, file_extension = os.path.splitext(path)
    if file_extension in {'.csv', ''}:
        return True
    else:
        return False


def check_ext(path: str) -> str:
    """
    return file extension of file provided by path
    :param path: path to file
    :return: file extension
    """
    return os.path.splitext(path)[1]


def trim_series(xdata: pd.Series, ydata: pd.Series, lim: tuple[float, float]) -> tuple[pd.Series, pd.Series]:
    """
    trims x and y data to specified x values
    :param xdata: x data
    :param ydata: y data
    :param lim: x data limits
    :return: trimmed x and y data
    """
    index = xdata[(xdata >= lim[0]) & (xdata <= lim[1])].index
    return xdata[index[0]:index[-1] + 1], ydata[index[0]:index[-1] + 1]


def process_series(dic: dict) -> tuple[np.ndarray, np.ndarray]:
    """
    filter and transform data
    :param dic: dictionary of data and transformations
    :return: array of data
    """
    xseries: pd.Series = dic['xdata'].copy()
    yseries: pd.Series = dic['ydata'].copy()
    index = xseries[(xseries >= dic['trim'][0]) & (xseries <= dic['trim'][1])].index
    xseries, yseries = xseries[index[0]:index[-1] + 1], yseries[index[0]:index[-1] + 1]

    if dic['cfc'] != 0 and type(dic['cfc']) is int:
        ydata = CFC_filter(1 / 10000, yseries.to_numpy(), dic['cfc'])
    else:
        ydata = yseries.to_numpy()

    xdata = xseries.to_numpy() * dic['xscale'] + dic['xoffset']
    ydata = ydata * dic['yscale'] + dic['yoffset']
    return xdata, ydata


def trim_arrays(*args: np.ndarray, xdata: np.ndarray = np.array([]), lim: tuple[float, float] = (-inf, inf)) -> tuple:
    """
    trims x and y data to specified x values
    :param xdata: x data
    :param ydata: y data
    :param lim: x data limits
    :return: trimmed x and y data
    """
    index = np.where((xdata >= lim[0]) & (xdata <= lim[1]))[0]
    trimmed = [arg[index[0]:index[-1] + 1] for arg in args]

    return xdata[index[0]:index[-1] + 1], *trimmed


def filter_arrays(*args: np.ndarray, T: float = 1 / 10000, cfc: int = 1000) -> list[ndarray]:
    """

    :param args: arrays to filter
    :param T: frequency
    :param cfc: filter type
    :return: filtered arrays
    """
    filtered = [CFC_filter(T, arg, cfc) for arg in args]

    return filtered


def integrate_data(xdata: pd.Series, ydata: pd.Series) -> float:
    return integrate.trapezoid(ydata, xdata)


if __name__ == '__main__':
    import random as rnd

    n = 1001
    X = np.linspace(-10, 10, n)
    Y2 = np.array([rnd.random() for i in range(n)])
    Y1 = np.linspace(-100, 100, n)

    Xt, Y1t, Y2t = trim_arrays(Y1, Y2, xdata=X, lim=(-1, 1))

    print(Xt)
    print(Y1t)
    print(Y2t)
