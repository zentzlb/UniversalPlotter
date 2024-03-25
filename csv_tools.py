import dask.dataframe as dd
import dask.array as da
import pandas as pd
import numpy as np

from functools import lru_cache


# import pyarrow


def open_csv(path: str, dtype=np.float64) -> tuple[pd.DataFrame, np.ndarray]:
    """
    opens csv file
    :param path: path to csv file
    :param dtype:
    :return: dataframe
    """
    print(path)
    print('reading columns')
    col = pd.read_csv(path, usecols=[0])
    print('listing headers')
    # Determine header rows based on non-numeric values in the first column
    header_rows = {row[0] for row in enumerate(col.iloc[:, 0]) if type(row[1]) is str and not check_type(row[1])}
    # If header rows are found, add one more row as the last header row
    if len(header_rows) > 0:
        header_rows.add(max(header_rows) + 1)
    print('opening main dataframe')
    df = pd.read_csv(path, skiprows=list(header_rows), dtype=dtype)
    df.dropna(how='all', axis=1, inplace=True)
    df.info(verbose=False, memory_usage="deep")
    print('opening headers')
    # Read the headers if they exist, otherwise use DataFrame columns as headers
    if len(header_rows) > 0:
        headers = pd.read_csv(path, skiprows=lambda x: x not in header_rows, dtype=str)
        headers.dropna(how='all', axis=1, inplace=True)
        headers.info(verbose=False, memory_usage="deep")
    else:
        headers = df.columns

    return df, headers.to_numpy()


def get_data(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    """
    trims dataframe to data
    :param df: dataframe
    :return: array of data and array of text
    """
    array = df.to_numpy()
    data = np.array([row.astype(float) for row in array if check_type(row)])
    text = np.array([row for row in array if not check_type(row)])
    return pd.DataFrame(data), text


def check_type(string: str) -> bool:
    """
    check if elements of array are numeric
    :param string: tring to check if numeric
    :return: true or false
    """
    try:
        float(string)
        return True
    except ValueError:
        return False

# Usage example
df, header = open_csv(r"C:\Users\ved.thakare\OneDrive - University of Virginia\Documents\CFC1000_Drop_33.csv", dtype=np.float32)
# Perform further processing with the Dask DataFrame 'df' and the headers array 'header'
