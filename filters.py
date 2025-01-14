import numpy as np
from scipy.signal import filtfilt
import math


def CFC(T: float, cfc: int) -> tuple[list[float], list[float]]:
    """
    calculates CFC parameters \n
    credit to: KEVIN KOPP
    :param T: time step between datapoints
    :param cfc: filter type
    :return: b and a constants
    """

    pi = math.pi

    wd = 2.0 * pi * cfc * 2.0775
    wa = (math.sin(wd * T / 2.0)) / (math.cos(wd * T / 2.0))

    a0: float = (wa ** 2.0) / (1.0 + wa * (2.0 ** .5) + wa ** 2.0)
    a1: float = 2 * a0
    a2: float = a0
    b1 = -2.0 * ((wa ** 2.0) - 1.0) / (1.0 + wa * (2.0 ** .5) + wa ** 2.0)
    b2 = (-1.0 + wa * (2.0 ** .5) - wa ** 2.0) / (1.0 + wa * (2.0 ** .5) + wa ** 2.0)

    A = [1, -b1, -b2]
    B = [a0, a1, a2]

    return B, A


def CFC_filter(T: float, data: np.ndarray, cfc: int) -> np.ndarray:
    """
    applies CFC filter to data
    :param T: time step between datapoints
    :param data: series to be filtered
    :param cfc: filter type
    :return: filtered data
    """
    b, a = CFC(T, cfc)
    return filtfilt(b, a, data)
