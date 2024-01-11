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
    return Binout(path)


def read_binout(binout: Binout, options: tuple) -> list | np.ndarray:
    """

    :param binout: lasso binout object
    :param options: tuple of options to select data from binout
    :return:
    """
    return binout.read(*options)


if __name__ == '__main__':
    path = (r"C:\Users\Logan.Zentz\OneDrive - University of Virginia\Documents"
            r"\Drop_Tests\sims\airbag\videos2"
            r"\drop_vent_d3.0_start1000_term2000_height12_blow_v14000_blow_s300_ea0.75_sim"
            r"\binout0000")

