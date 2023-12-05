import numpy as np
import math


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
    for i in range(2, n):
        V[i] = V[i-1] + 0.5 * (A[i] + A[i-1]) * (t[i] - t[i-1])
        for j in range(i-1, 0, -1):
            dt = t[i] - t[j]
            if dt < 0.015:
                h = dt * ((V[i] - V[j]) / dt) ** 2.5
                if h > hic:
                    hic = h
                    hic_t = t[i]
    return hic, hic_t


