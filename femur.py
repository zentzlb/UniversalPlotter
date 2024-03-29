import numpy as np
from math import exp


def femur_ais2(force_z: np.ndarray) -> tuple[float, float]:
    """
    calculates the AIS2+ femur injury risk \n
    source: Development of Improved Injury Criteria
    for the Assessment of Advanced Automotive
    Restraint Systems - II
    :param force_z: force (N) in the z direction
    :return: risk of AIS2+ femur injury, max force in kN
    """
    # force = np.sqrt(np.square(force_x) + np.square(force_y) + np.square(force_z))
    force_max = max(force_z.__abs__()) / 1000  # convert to kN
    return 1 / (1 + exp(5.795 - 0.5196 * force_max)), force_max
