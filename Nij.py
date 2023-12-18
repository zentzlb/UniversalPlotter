import math
import numpy as np


def neck_AIS(nij: float) -> tuple[float, float, float, float]:
    """

    :param nij:
    :return:
    """
    ais5 = 1 / (1 + math.exp(3.817 - 1.195 * nij))
    ais4 = 1 / (1 + math.exp(2.693 - 1.195 * nij))
    ais3 = 1 / (1 + math.exp(3.227 - 1.969 * nij))
    ais2 = 1 / (1 + math.exp(2.054 - 1.195 * nij))

    return ais2 - ais3, ais3 - ais4, ais4 - ais5, ais5
