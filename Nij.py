from math import exp
import numpy as np


# def neck_AIS(nij: float) -> tuple[float, float, float, float]:
#     """
#
#     :param nij:
#     :return:
#     """
#     ais5 = 1 / (1 + math.exp(3.817 - 1.195 * nij))
#     ais4 = 1 / (1 + math.exp(2.693 - 1.195 * nij))
#     ais3 = 1 / (1 + math.exp(3.227 - 1.969 * nij))
#     ais2 = 1 / (1 + math.exp(2.054 - 1.195 * nij))
#
#     return ais2 - ais3, ais3 - ais4, ais4 - ais5, ais5

def nij(fz: np.ndarray, my: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    calculates Nij score from axial loading and moment of the neck \n
    source: Injury Criteria for the THOR 50th Male ATD
    :param fz: axial loading along z-axis -> compression/tension
    :param my: moment around y-axis -> flexion/extension
    :return: Nij score
    """
    flex_ext = lambda x: x / 310 if x > 0 else -x / 125
    ten_comp = lambda x: x / 6806 if x > 0 else -x / 6160
    fz_norm = np.array([ten_comp(f) for f in fz])  # (fz / 4500).__abs__()
    my_norm = np.array([flex_ext(m) for m in my])
    nij_history = fz_norm + my_norm
    return nij_history, fz_norm, my_norm


def neck_ais(nij_score: float, age: int = 45) -> tuple[float, float, float]:
    """
    calculates AIS2 and AIS3+ neck injury risk from Nij \n
    source: Injury Criteria for the THOR 50th Male ATD \n
    & \n
    Development of Improved Injury Criteria for the
    Assessment of Advanced Automotive Restraint Systems - II
    :param nij_score: Nij Score
    :param age: surrogate age in years
    :return: AIS2, AIS3+ injury risk, old AIS3+ injury risk curve
    """
    ais2 = 1 / (1 + exp(9.031 - 5.681 * nij_score - 0.0803 * age))
    ais3 = 1 / (1 + exp(7.447 - 5.440 * nij_score - 0.0350 * age))
    ais3old = 1 / (1 + exp(3.227 - 1.969 * nij_score))

    return min(ais2 - ais3, 0), ais3, ais3old


if __name__ == '__main__':
    print(neck_ais(2.66, 45))

