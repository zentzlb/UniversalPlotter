import lasso.dyna
from lasso.dyna import D3plot, ArrayType, Binout
import os
from utils import catch
import numpy as np


@catch
def get_binout(path: str) -> Binout:
    """
    open key file and convert to string
    :param path: path to
    :return: text (string)
    """
    print(path)
    return Binout(path)


def read_binout(binout: Binout, keys: tuple[str, str, str]) -> tuple:
    """

    :param binout: lasso binout object
    :param keys:
    :return:
    """

    if keys[2]:
        index = list(binout.read(keys[0], 'ids')).index(int(keys[2]))  # NOQA
    else:
        index = 0

    if keys[0] and keys[1]:
        options1 = [keys[0], 'time']
        options2 = [keys[0], keys[1]]

        return binout.read(*options1), binout.read(*options2)[:, index]

    else:
        return None, None


if __name__ == '__main__':
    path = (r"C:\Users\Logan.Zentz"
            r"\OneDrive - University of Virginia\Documents"
            r"\Drop_Tests\sims\airbag\final\3inch vent\12ft\ea 0.1"
            r"\drop_vent_d3.0_start1000_term2000_height12_blow_v14000_blow_s300_ea0.1_sim\binout0000")

