import numpy as np
from math import exp


def femur_ais2(force_x: np.ndarray,
               force_y: np.ndarray,
               force_z: np.ndarray) -> tuple[float, float]:
    """
    calculates the AIS2+ femur injury risk \n
    source: Development of ImprovedInjury Criteria
    for theAssessment of AdvancedAutomotive
    Restraint Systems - II
    :param force_x: force in the x direction
    :param force_y: force in the y direction
    :param force_z: force in the z direction
    :return: risk of AIS2+ femur injury, max force
    """
    force = np.sqrt(np.square(force_x) + np.square(force_y) + np.square(force_z))
    force_max = max(force)
    return 1 / (1 + exp(5.795 - 0.5196 * force_max)), force_max
