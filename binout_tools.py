import lasso.dyna
from lasso.dyna import D3plot, ArrayType, Binout
import os
from utils import catch
import numpy as np
import re


@catch
def get_binout(path: str) -> Binout:
    """
    open key file and convert to string
    :param path: path to
    :return: text (string)
    """
    pattern = re.compile(r"([\d%]*)$")
    path = re.subn(pattern, '*', path, 1)[0]
    print(path)
    # if os.path.isdir(path):
    return Binout(path)
    # else:
    #     return Binout(path)


def read_binout(binout: Binout, keys: tuple[str, str, str]) -> tuple:
    """

    :param binout: lasso binout object
    :param keys:
    :return:
    """

    # if keys[2]:
    #     index = list(binout.read(keys[0], 'ids')).index(int(keys[2]))  # NOQA
    # else:
    #     index = 0

    if keys[0] and keys[1]:
        options1 = [keys[0], 'time']
        options2 = [keys[0], keys[1]]

        if keys[2]:
            index = list(binout.read(keys[0], 'ids')).index(int(keys[2]))  # NOQA
            return binout.read(*options1), binout.read(*options2)[:, index]
        else:
            return binout.read(*options1), binout.read(*options2)

    else:
        return None, None




if __name__ == '__main__':
    PATH = (r"\\cab-fs07.mae.virginia.edu\NewData\DOT\2021-RR-Safety\1Simulation\FInal_Stunt_AB_models\5_CAB_AB_Drop_calibration\A10000\24ft\binout*")

