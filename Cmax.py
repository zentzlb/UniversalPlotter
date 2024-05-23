import math


def chest_AIS3(cmax: float) -> float:
    """
    calculates AIS3+ chest injury risk from chest deflection \n
    source: The Hybrid III Dummy as a Discriminator of Injurious
    and Non-Injurious Restraint Loading
    :param cmax: chest deflection (mm)
    :return: AIS3+ injury risk
    """
    a = -14.4135
    B = [
        -2.1944,  # sex
        -0.0425,  # mass
        0.0692,  # age
        0.2518,  # sled speed (km/hr)
        1.0193,  # is driver
        -8.4238,  # airbag loading
        -3.8875,  # combined loading
        0.1696  # cmax
    ]

    x = [
        1,  # male
        77.7,  # mass (kg)
        45,  # age
        56.327,  # sled speed (km/hr) 51.5
        0,  # is driver
        1,  # airbag loading
        0,  # combined loading
        cmax
    ]

    q = a + sum([x[0] * x[1] for x in zip(B, x)])

    return 1 / (1 + math.exp(-q))


def chest_AIS3_old(cmax: float) -> tuple[float, float, float, float]:
    """
    calculates chest injury from old risk curves \n
    source: Development of Improved
    Injury Criteria for the
    Assessment of Advanced
    Automotive Restraint Systems - II
    :param cmax: chest deflection (mm)
    :return: AIS 2+, AIS 3+, AIS 4+, AIS 5+, injury risk
    """
    ais2 = 1 / (1 + math.exp(1.8706 - 0.04439 * cmax))
    ais3 = 1 / (1 + math.exp(3.7124 - 0.0475 * cmax))
    ais4 = 1 / (1 + math.exp(5.0952 - 0.0475 * cmax))
    ais5 = 1 / (1 + math.exp(8.8274 - 0.0459 * cmax))
    return ais2, ais3, ais4, ais5


if __name__ == '__main__':
    print(chest_AIS3(24.1))
    print()
    print(chest_AIS3_old(24.1))
