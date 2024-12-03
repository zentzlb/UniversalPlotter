import numpy as np
from math import sqrt, exp


# from math import sqrt

def bric(wx: np.ndarray, wy: np.ndarray, wz: np.ndarray) -> float:
    """
    Function calculates the Maximum BrIC score \n
    source: Injury Criteria for the THOR 50th Male ATD
    :param wx: x angular velocity in rads/s
    :param wy: y angular velocity in rads/s
    :param wz: z angular velocity in rads/s
    :return: Maximum BrIC score
    """
    maxwx = np.abs(wx).max()
    maxwy = np.abs(wy).max()
    maxwz = np.abs(wz).max()
    wxc = 66.25
    wyc = 56.45
    wzc = 42.87

    return np.sqrt(np.square(maxwx / wxc) + np.square(maxwy / wyc) + np.square((maxwz / wzc)))


def bric_csdm_ais(bric_score: float) -> tuple[float, float, float, float, float]:
    """
    This function calculates the Risk curve for BrIC based on CSDM \n
    source: Injury Criteria for the THOR 50th Male ATD
    :param bric_score: Maximum BrIC Score
    :return: [P(AIS1), P(AIS2), P(AIS3), P(AIS4), P(AIS5+)] based on CSDM
    """
    ais1plus: float = 1 - exp(-(((bric_score - 0.523) / 0.065) ** 1.8))
    ais2plus: float = 1 - exp(-(((bric_score - 0.523) / 0.324) ** 1.8))
    ais3plus: float = 1 - exp(-(((bric_score - 0.523) / 0.531) ** 1.8))
    ais4plus: float = 1 - exp(-(((bric_score - 0.523) / 0.647) ** 1.8))
    ais5plus: float = 1 - exp(-(((bric_score - 0.523) / 0.673) ** 1.8))
    ais1: float = ais1plus - ais2plus
    ais2: float = ais2plus - ais3plus
    ais3: float = ais3plus - ais4plus
    ais4: float = ais4plus - ais5plus

    return ais1, ais2, ais3, ais4, ais5plus


def bric_mps_ais(bric_score: float) -> tuple[float, float, float, float, float]:
    """
    This function calculates the Risk curve for BrIC based on MPS \n
    source: Injury Criteria for the THOR 50th Male ATD
    :param bric_score: Maximum BrIC Score
    :return: [P(AIS1+), P(AIS2+), P(AIS3+), P(AIS4+), P(AIS5+)] based on MPS
    """
    ais1plus: float = 1 - exp(-((bric_score / 0.120) ** 2.84))
    ais2plus: float = 1 - exp(-((bric_score / 0.602) ** 2.84))
    ais3plus: float = 1 - exp(-((bric_score / 0.987) ** 2.84))
    ais4plus: float = 1 - exp(-((bric_score / 1.204) ** 2.84))
    ais5plus: float = 1 - exp(-((bric_score / 1.252) ** 2.84))
    ais1: float = ais1plus - ais2plus
    ais2: float = ais2plus - ais3plus
    ais3: float = ais3plus - ais4plus
    ais4: float = ais4plus - ais5plus
    return ais1plus, ais2plus, ais3plus, ais4plus, ais5plus


if __name__ == '__main__':
    # import random as rnd
    #
    # n = 100_000
    # Wx = np.array([20 * rnd.random() for i in range(n)])
    # Wy = np.array([20 * rnd.random() for i in range(n)])
    # Wz = np.array([20 * rnd.random() for i in range(n)])
    #

    # Wx = np.array([0])
    # Wy = np.array([0])
    # Wz = np.array([25])
    # print(BrIC := bric(Wx, Wy, Wz))
    # # print(bric_csdm_ais(BrIC))
    # print(bric_mps_ais(BrIC))
    print(bric_mps_ais(0.4))
    # ais_mps.__annotations__

