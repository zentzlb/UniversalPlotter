import functools
import numpy as np
import math
import time
import numba
import random as rnd
from scipy.stats import norm
import itertools


def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        a = fn(*args, **kwargs)
        t2 = time.time()
        print(f"function run time: {t2-t1}s")
        return a
    return wrapper


@timed
@numba.njit
def hic15(mytime: np.ndarray[float], ax: np.ndarray, ay: np.ndarray, az: np.ndarray) -> tuple[float, float]:
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
    for a1, a2, t1, t2 in zip(acc[:-1], acc[1:], mytime[:-1], mytime[1:]):
        vel.append(vel[-1] + 0.5 * (a2 + a1) * (t2 - t1))

    vel = np.array(vel)
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

    return hic, hic_t


def hic_ais(hic: float) -> tuple[float, float]:
    """
    calculate AIS2+ risk from HIC15 score
    :param hic: HIC15 score
    :return: risk of injury
    """
    p2 = (math.log(hic) - 6.96362) / 0.84687
    p3 = (math.log(hic) - 7.45231) / 0.73998
    return norm.cdf(p2), norm.cdf(p3)


if __name__ == '__main__':
    t = np.linspace(0, 10, 100001)
    Ax = np.array([100 * rnd.random() for i in range(len(t))])
    Ay = np.array([100 * rnd.random() for i in range(len(t))])
    Az = np.array([100 * rnd.random() for i in range(len(t))])

    Hic, Hic_t = hic15(t, Ax, Ay, Az)
    print(Hic, Hic_t)


