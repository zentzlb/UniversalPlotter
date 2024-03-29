from typing import Callable

import numba
import numpy as np
import math
import random as rnd
from scipy.interpolate import interp1d
from scipy.integrate import odeint
import functools
import time


rnd.seed(15)


def timed(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        a = fn(*args, **kwargs)
        t2 = time.time()
        print(f"function run time: {t2-t1}s")
        return a
    return wrapper


def deriv(y: np.ndarray, t: np.ndarray):
    """
    COMMENT THIS FUNCTION
    :param y:
    :param t:
    :return:
    """
    return [(v2 - v1) / (t2 - t1) for v1, v2, t1, t2 in zip(y[:-1], y[1:], t[:-1], t[1:])]

# Implementation of DAMAGE from paper "Development of a Second-Order System for Rapid Estimation of Maximum Brain
# Strain"
# Author: Bernd Schneider, TU Graz


def mass_matrix(mx, my, mz):
    return np.array([[mx, 0, 0],
                     [0, my, 0],
                     [0, 0, mz]])


def stiffness_matrix(kxx, kyy, kzz, kxy, kyz, kxz):
    return np.array([[kxx + kxy + kxz, -kxy, -kxz],
                     [-kxy, kxy + kyy + kyz, -kyz],
                     [-kxz, -kyz, kxz + kyz + kzz]])


def damping_matrix(m, k, a0, a1):
    return a0 * m + a1 * k


def create_matrices(mx: float,
                    my: float,
                    mz: float,
                    kxx: float,
                    kyy: float,
                    kzz: float,
                    kxy: float,
                    kyz: float,
                    kxz: float,
                    a0: float,
                    a1: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """

    :param mx:
    :param my:
    :param mz:
    :param kxx:
    :param kyy:
    :param kzz:
    :param kxy:
    :param kyz:
    :param kxz:
    :param a0:
    :param a1:
    :return:
    """


    m = mass_matrix(mx, my, mz)
    k = stiffness_matrix(kxx, kyy, kzz, kxy, kyz, kxz)
    c = damping_matrix(m, k, a0, a1)
    return m, c, k


# @numba.njit
def equation_of_motion(y, t, m, m_inv, c, k, ang_acc_x, ang_acc_y, ang_acc_z, time_ang_acc):
    delta_x, delta_y, delta_z, d_delta_x, d_delta_y, d_delta_z = y
    delta = np.array([delta_x, delta_y, delta_z])
    d_delta = np.array([d_delta_x, d_delta_y, d_delta_z])
    f_a_x = interp1d(time_ang_acc, ang_acc_x, fill_value='extrapolate')
    f_a_y = interp1d(time_ang_acc, ang_acc_y, fill_value='extrapolate')
    f_a_z = interp1d(time_ang_acc, ang_acc_z, fill_value='extrapolate')
    a = np.array([f_a_x(t), f_a_y(t), f_a_z(t)])
    dd_delta = np.dot(m_inv, np.dot(m, a) - (np.dot(c, d_delta) + np.dot(k, delta)))
    dydt = [d_delta_x, d_delta_y, d_delta_z, dd_delta[0], dd_delta[1], dd_delta[2]]
    return dydt


@timed
# @numba.jit(nopython=False)
def calc_damage(wx: np.ndarray,
                wy: np.ndarray,
                wz: np.ndarray,
                t: np.ndarray,
                m: np.ndarray,
                c: np.ndarray,
                k: np.ndarray) -> float:
    """
    Calculates the damage from the angular velocity
    :param wx: x angular velocity
    :param wy: y angular velocity
    :param wz: z angular velocity
    :param t: time
    :param m:
    :param c:
    :param k:
    :param solver:
    :return: Damage
    """
    # initial values of delta and delta' are zero
    ang_acc_x = [(w2 - w1) / (t2 - t1) for w1, w2, t1, t2 in zip(wx[:-1], wx[1:], t[:-1], t[1:])]
    ang_acc_y = [(w2 - w1) / (t2 - t1) for w1, w2, t1, t2 in zip(wy[:-1], wy[1:], t[:-1], t[1:])]
    ang_acc_z = [(w2 - w1) / (t2 - t1) for w1, w2, t1, t2 in zip(wz[:-1], wz[1:], t[:-1], t[1:])]
    y0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


    m_inv = np.linalg.inv(m)

    t1 = time.time()
    sol = odeint(equation_of_motion, y0, t,
                 args=(m, m_inv, c, k, ang_acc_x, ang_acc_y, ang_acc_z, t[:-1]))
    t2 = time.time()
    print(f"odeint run time: {t2-t1}")
    delta = sol[:, :3]
    delta_norm = np.linalg.norm(delta, axis=1)
    damage = 2.9903 * np.max(delta_norm)
    return damage


def Damg_to_AIS(damage: float) -> tuple[float, float, float]:
    """
    This function calculates the Risk curve for damage
    :param damage: damage value
    :return: [P(AIS1+), P(AIS2+), P(AIS4+)]
    """
    P_Head_DAMAGE_AIS1 = 1 - math.exp(-math.exp(math.log(0.957 * damage + 0.017) * 4.078 - math.log(0.394) * 4.078))
    P_Head_DAMAGE_AIS2 = 1 - math.exp(-math.exp(math.log(0.957 * damage + 0.017) * 3.875 - math.log(0.459) * 3.875))
    P_Head_DAMAGE_AIS4 = 1 - math.exp(-math.exp(math.log(0.957 * damage + 0.017) * 6.051 - math.log(0.646) * 6.051))
    return P_Head_DAMAGE_AIS1, P_Head_DAMAGE_AIS2, P_Head_DAMAGE_AIS4


if __name__ == '__main__':

    # mx, my, mz, kxx, kyy, kzz, kxy, kyx, kxz, a0, a1, beta
    M, C, K = create_matrices(
        1, 1, 1, 32142, 23493, 16935, 0, 0, 1636.3, 0, 0.0059148)

    n = 1000
    T = np.linspace(0, 1, n)
    Wx = np.array([50 * math.sin(i / 100) for i in range(n)])
    Wy = np.array([50 * math.sin(i / 70) for i in range(n)])
    Wz = np.array([50 * math.sin(i / 120) for i in range(n)])
    print(dmg := calc_damage(Wx, Wy, Wz, T, M, C, K))
    print(Damg_to_AIS(dmg))
