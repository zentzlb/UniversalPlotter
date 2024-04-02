import functools
import numpy as np
import math
import time
from numba import njit, float64
from numba.core.types import UniTuple
import random as rnd
from scipy.stats import norm
from typing import Callable


def timed(fn: Callable) -> Callable:
    """
    adds runtime counter
    :param fn: function
    :return: timed function
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        a = fn(*args, **kwargs)
        t2 = time.time()
        print(f"{fn.__name__} run time: {t2 - t1}s")
        return a

    return wrapper


@timed
@njit(UniTuple(float64, 2)(float64[::1], float64[::1], float64[::1], float64[::1]))
def hic15(my_time: np.ndarray,
          ax: np.ndarray,
          ay: np.ndarray,
          az: np.ndarray) -> tuple[float, float]:
    """
    find maximum HIC15 value
    :param my_time: time (s)
    :param ax: x acceleration (g)
    :param ay: y acceleration (g)
    :param az: z acceleration (g)
    :return: HIC15 score
    """

    hic = 0
    hic_t = 0
    dt = 0.015
    n = len(my_time)
    acc = np.sqrt(np.square(ax) + np.square(ay) + np.square(az))
    vel = [0]
    for a1, a2, t1, t2 in zip(acc[:-1], acc[1:], my_time[:-1], my_time[1:]):
        vel.append(vel[-1] + 0.5 * (a2 + a1) * (t2 - t1))

    vel = np.array(vel)
    for i, t0_v0 in enumerate(zip(my_time, vel)):
        t0, v0 = t0_v0
        for j in range(i+1, n):
            delta_t = my_time[j] - t0
            if delta_t <= dt:
                h = ((vel[j] - v0) ** 2.5) / delta_t ** 1.5
                if h > hic:
                    hic = h
                    hic_t = t0
            else:
                break

    return hic, hic_t


def hic_ais(hic: float) -> tuple[float, float]:
    """
    calculate AIS2+ risk from HIC15 score \n
    source: Injury Criteria for the THOR 50th Male ATD
    :param hic: HIC15 score
    :return: AIS2, AIS3+ injury risk
    """
    p2 = (math.log(hic) - 6.96362) / 0.84687
    p3 = (math.log(hic) - 7.45231) / 0.73998
    ais2 = norm.cdf(p2)
    ais3 = norm.cdf(p3)
    return min(ais2 - ais3, 0), ais3


if __name__ == '__main__':
    t = np.linspace(0, 10, 100001)
    Ax = np.array([100 * rnd.random() for i in range(len(t))])
    Ay = np.array([100 * rnd.random() for i in range(len(t))])
    Az = np.array([100 * rnd.random() for i in range(len(t))])

    hic15(t, Ax, Ay, Az)
    Hic, Hic_t = hic15(t, Ax, Ay, Az)
    print(Hic, Hic_t)


