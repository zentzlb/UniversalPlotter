# Implementation of DAMAGE from paper "Development of a Second-Order System for Rapid Estimation of Maximum Brain
# Strain"
# Author: Bernd Schneider, TU Graz
# Fixed By: Logan Zentz, UVA

import numpy as np
from scipy.integrate import odeint
import functools
from numba import jit, njit, int_, float_, int32, float64, float32
import math
import time
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


def dy_dt(y: np.ndarray, t: np.ndarray) -> np.ndarray:
    """
    calculate derivative of data
    :param y: data array
    :param t: time array
    :return: derivative
    """
    return np.array([(y2 - y1) / (t2 - t1) for y1, y2, t1, t2 in zip(y[:-1], y[1:], t[:-1], t[1:])])


def mass_matrix(mx: float, my: float, mz: float) -> np.ndarray:
    """
    calculates mass matrix
    :param mx: mass x
    :param my: mass y
    :param mz: mass z
    :return: mass matrix
    """
    return np.array([[mx, 0, 0],
                     [0, my, 0],
                     [0, 0, mz]],
                    dtype=np.float64)


def stiffness_matrix(kxx: float, kyy: float, kzz: float, kxy: float, kyz: float, kxz: float) -> np.ndarray:
    """
    calculates stiffness matrix
    :param kxx: matrix element
    :param kyy: matrix element
    :param kzz: matrix element
    :param kxy: matrix element
    :param kyz: matrix element
    :param kxz: matrix element
    :return: stiffness matrix
    """
    return np.array([[kxx + kxy + kxz, -kxy, -kxz],
                     [-kxy, kxy + kyy + kyz, -kyz],
                     [-kxz, -kyz, kxz + kyz + kzz]])


def damping_matrix(mass: np.ndarray, stiffness: np.ndarray, a0: float, a1: float) -> np.ndarray:
    """
    calculates damping matrix
    :param mass: mass matrix
    :param stiffness: stiffness matrix
    :param a0: mass coefficient
    :param a1: stiffness coefficient
    :return: damping matrix
    """
    return a0 * mass + a1 * stiffness


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
    fetches matrices for ODE solver
    :param mx: mass matrix param
    :param my: mass matrix param
    :param mz: mass matrix param
    :param kxx: stiffness matrix param
    :param kyy: stiffness matrix param
    :param kzz: stiffness matrix param
    :param kxy: stiffness matrix param
    :param kyz: stiffness matrix param
    :param kxz: stiffness matrix param
    :param a0: damping matrix param
    :param a1: damping matrix param
    :return: Mass, Damping, and Stiffness Matrices
    """
    mass = mass_matrix(mx, my, mz)
    stiffness = stiffness_matrix(kxx, kyy, kzz, kxy, kyz, kxz)
    damping = damping_matrix(mass, stiffness, a0, a1)
    return mass, damping, stiffness


# @njit
@njit(float64[::1](float64[::1], float64, float64[:, ::1], float64[:, ::1], float64[:, ::1], float64[:, ::1],
                   float64[::1], float64[::1], float64[::1], float64[::1]))
def equation_of_motion(y: np.ndarray,
                       t: float,
                       mass: np.ndarray,
                       mass_inv: np.ndarray,
                       damping: np.ndarray,
                       stiffness: np.ndarray,
                       aax: np.ndarray,
                       aay: np.ndarray,
                       aaz: np.ndarray,
                       time_: np.ndarray) -> np.ndarray:
    """
    equation of motion for spring oscillator system
    :param y: ODE y derivatives
    :param t: instantaneous time
    :param mass: mass matrix
    :param mass_inv: inverse of mass matrix
    :param damping: damping matrix
    :param stiffness: stiffness matrix
    :param aax: x angular acceleration
    :param aay: y angular acceleration
    :param aaz: z angular acceleration
    :param time_: time array
    :return: first and second derivatives
    """
    delta_x, delta_y, delta_z, d_delta_x, d_delta_y, d_delta_z = y
    delta = np.array([delta_x, delta_y, delta_z])
    d_delta = np.array([d_delta_x, d_delta_y, d_delta_z])

    a = np.array([np.interp(t, time_, aax), np.interp(t, time_, aay), np.interp(t, time_, aaz)],
                 dtype=np.float64)

    dd_delta = np.dot(mass_inv, np.dot(mass, a) - (np.dot(damping, d_delta) + np.dot(stiffness, delta)))
    return np.array([d_delta_x, d_delta_y, d_delta_z, dd_delta[0], dd_delta[1], dd_delta[2]])


@timed
def calc_damage(aax: np.ndarray, aay: np.ndarray, aaz: np.ndarray, time_: np.ndarray) -> float:
    """
    calculates brain strain from angular acceleration
    :param aax: x angular acceleration
    :param aay: y angular acceleration
    :param aaz: z angular acceleration
    :param time_: time
    :return: damage score
    """
    # initial values of delta and delta' are zero
    y0 = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    # mx, my, mz, kxx, kyy, kzz, kxy, kyx, kxz, a0, a1, beta
    mass, damping, stiffness = create_matrices(1, 1, 1,
                                               32142, 23493, 16935, 0, 0, 1636.3,
                                               0, 0.0059148)
    mass_inv = np.linalg.inv(mass)

    # since mass matrix is identity matrix with parameters from settings file this could be considered in the
    # calculation if speed is an issue
    sol = odeint(equation_of_motion, y0, time_,
                 args=(mass, mass_inv, damping, stiffness, aax, aay, aaz, time_))
    delta = sol[:, :3]
    delta_norm = np.linalg.norm(delta, axis=1)
    damage = 2.9903 * np.max(delta_norm)
    return damage


def dmg_ais(damage: float) -> tuple[float, float, float]:
    """
    This function calculates the Risk curve for damage injury criteria
    :param damage: damage value
    :return: [P(AIS1+), P(AIS2+), P(AIS4+)]
    """
    P_Head_DAMAGE_AIS1 = 1 - math.exp(-math.exp(math.log(0.957 * damage + 0.017) * 4.078 - math.log(0.394) * 4.078))
    P_Head_DAMAGE_AIS2 = 1 - math.exp(-math.exp(math.log(0.957 * damage + 0.017) * 3.875 - math.log(0.459) * 3.875))
    P_Head_DAMAGE_AIS4 = 1 - math.exp(-math.exp(math.log(0.957 * damage + 0.017) * 6.051 - math.log(0.646) * 6.051))
    return P_Head_DAMAGE_AIS1, P_Head_DAMAGE_AIS2, P_Head_DAMAGE_AIS4


if __name__ == '__main__':
    # njit(float64[::1](float64[::1], float64, float64[::1, :], float64[::1, :], float64[::1, :], float64[::1, :],
    #                   float64[::1], float64[::1], float64[::1], float64[::1]))(equation_of_motion).inspect_types()

    def main():
        n = 4000
        T = np.linspace(0, 1, n)
        Wx = np.array([50 * math.sin(i / 100) for i in range(n)])
        Wy = np.array([50 * math.sin(i / 70) for i in range(n)])
        Wz = np.array([50 * math.sin(i / 120) for i in range(n)])
        Ax = dy_dt(Wx, T)
        Ay = dy_dt(Wy, T)
        Az = dy_dt(Wz, T)
        print(dmg := calc_damage(Ax, Ay, Az, T[1:]))
        print(dmg := calc_damage(Ax, Ay, Az, T[1:]))
        print(dmg_ais(dmg))
        # print(Damg_to_AIS(dmg)) 0.28514911121460335


    main()
