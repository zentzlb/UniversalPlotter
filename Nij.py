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


def neck_AIS(nij: float, age: int = 45) -> tuple[float, float]:
    """
    calculates AIS2 and AIS3+ neck injury risk from Nij \n
    source: Injury Criteria for the THOR 50th Male ATD
    :param nij: Nij Score
    :param age: surrogate age in years
    :return: AIS2, AIS3+ injury risk
    """
    ais2 = 1 / (1 + exp(9.031 - 5.681 * nij - 0.0803 * age))
    ais3 = 1 / (1 + exp(7.447 - 5.440 * nij - 0.0350 * age))

    return min(ais2 - ais3, 0), ais3
