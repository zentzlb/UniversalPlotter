from typing import Tuple
import functools
import numpy as np
import math
import time
import numba
import random as rnd
from scipy.stats import norm
from typing import Callable


def timed(fn: Callable) -> Callable:
    """
    time function execution
    :param fn: function
    :return: timed function
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t1 = time.process_time()
        a = fn(*args, **kwargs)
        t2 = time.process_time()
        print(t2-t1)
        return a
    return wrapper


@timed
def hic15(t: np.ndarray, ax: np.ndarray, ay: np.ndarray, az: np.ndarray):
    """

    :param t: time in s
    :param ax: x acceleration in gs
    :param ay: y acceleration in gs
    :param az: z acceleration in gs
    :return: HIC15
    """
    n = len(t)
    hic = 0
    hic_t = 0
    V = np.zeros_like(t)
    A = np.sqrt(np.square(ax) + np.square(ay) + np.square(az))
    for i in range(1, n):
        V[i] = V[i-1] + 0.5 * (A[i] + A[i-1]) * (t[i] - t[i-1])
        for j in range(i-1, 0, -1):
            dt = t[i] - t[j]
            if dt < 0.015:
                h = dt * ((V[i] - V[j]) / dt) ** 2.5
                if h > hic:
                    hic = h
                    hic_t = t[j]
    return hic, hic_t


@timed
@numba.njit
def Hic15(mytime: np.ndarray[float], ax: np.ndarray, ay: np.ndarray, az: np.ndarray) -> tuple[float, float]:
    """
    find maximum HIC15 value
    :param mytime: time in s
    :param ax: x acceleration in gs
    :param ay: y acceleration in gs
    :param az: z acceleration in gs
    :return: HIC15
    """

    hic = 0
    hic_t = 0
    dt = 0.015
    n = len(mytime)
    acc = np.sqrt(np.square(ax) + np.square(ay) + np.square(az))
    vel = [0]
    # vel = np.trapz(acc, x=mytime)
    for a1, a2, t1, t2 in zip(acc[:-1], acc[1:], mytime[:-1], mytime[1:]):
        vel.append(vel[-1] + 0.5 * (a2 + a1) * (t2 - t1))

    index15 = 0
    for i, t0_v0 in enumerate(zip(mytime, vel)):
        t0, v0 = t0_v0
        for j in range(i+1, n):
            delta_t = mytime[j] - t0
            if delta_t <= dt:
                h = ((vel[j] - v0) ** 2.5) / delta_t ** 1.5
                if h > hic:
                    hic = h
                    hic_t = t0
            else:
                break
        # index15, t1 = find_next(mytime, t0, index15, dt)
        # for j in range(index15, i, -1):
        #     delta_t = mytime[j] - t0
        #     h = ((vel[j] - v0) ** 2.5) / delta_t ** 1.5
        #     if h > hic:
        #         hic = h
        #         hic_t = t0

    return hic, hic_t


def hicAIS2(hic15):
    """
    calculate AIS2+ risk from HIC15 score
    :param hic15: HIC15 score
    :return: risk of injury
    """
    p = (math.log(hic15) - 6.96352) / 0.84664
    return norm.cdf(p)


def find_next(array: np.ndarray[float], start_val: float, start_ind: int, delta: float)\
        -> tuple[int, float]:
    """
    finds closest array value that doesn't go over delta
    :param array: numpy array, MUST be ordered and increasing
    :param start_val: starting value
    :param start_ind:
    :param delta:
    :return:
    """
    for i in range(start_ind, len(array)):
        if array[i] - start_val > delta:
            return i-1, array[i-1]
    return len(array) - 1, array[-1]


def closure(fn):
    v = [0]

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        v[0] += fn(*args, **kwargs)
        return v[0]
    return wrapper


def integrate(x, y):
    @closure
    def fn(z):
        return 2 * z


if __name__ == '__main__':
    Time = np.linspace(0, 10, 10001)
    Ax = np.array([100 * rnd.random() for i in range(10001)])
    Ay = np.array([100 * rnd.random() for i in range(10001)])
    Az = np.array([100 * rnd.random() for i in range(10001)])

    hic, hic_t = hic15(Time, Ax, Ay, Az)
    print(hic, hic_t)

    hic, hic_t = Hic15(Time, Ax, Ay, Az)
    print(hic, hic_t)

