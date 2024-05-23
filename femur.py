import numpy as np
from math import exp


def femur_ais(force_z: np.ndarray) -> tuple[float, float, float]:
    """
    calculates the AIS2+ femur injury risk \n
    source: Lower Extremity Injuries and Associated Injury Criteria, Kuppa 2001
    :param force_z: force (N) in the z direction
    :return: risk of AIS2+ femur injury, risk of AIS3+ femur injury, max force in kN
    """
    # force = np.sqrt(np.square(force_x) + np.square(force_y) + np.square(force_z))
    force_max = max(force_z.__abs__()) / 1000  # convert to kN
    return 1 / (1 + exp(5.7949 - 0.5196 * force_max)), 1 / (1 + exp(4.9795 - 0.326 * force_max)), force_max


if __name__ == '__main__':
    pass