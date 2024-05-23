import numpy as np
from math import exp, log


def rti(mx: np.ndarray, my: np.ndarray, fz: np.ndarray) -> float:
    """
    calculates tibia index from moments and axial force
    source: Lower Extremity Injuries and Associated Injury Criteria, Kuppa 2001
    :param mx: x moment in Nm
    :param my: y moment in Nm
    :param fz: z force in N
    :return: tibia index
    """
    return max(np.sqrt(np.square(mx) + np.square(my)) / 240 + np.abs(fz) / 12_000)


def tibia_ais2(ti: float):
    """
    calculates tibia ais2+ risk from tibia index
    source: Lower Extremity Injuries and Associated Injury Criteria, Kuppa 2001
    :param ti: tibia index
    :return: ais2+ risk
    """
    return 1 - exp(-exp((log(ti) - 0.2468) / 0.2728))


def ankle_ais2(fz: np.ndarray) -> tuple[float, float]:
    """
    calculates ankle ais2+ risk from lower tibia axial load
    source: Lower Extremity Injuries and Associated Injury Criteria, Kuppa 2001
    :param fz: lower tibia force
    :return: ais2+ risk
    """
    force_max = max(fz.__abs__()) / 1000
    return 1 / (1 + exp(4.572 - 0.670 * force_max)), force_max
