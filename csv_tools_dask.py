import dask.dataframe as dd
import dask.array as da
import pandas as pd
import numpy as np

import dask.dataframe as dd
import numpy as np


def open_csv(path: str, dtype=np.float64) -> tuple[dd.DataFrame, np.ndarray]:
    """
    Opens a CSV file as a Dask DataFrame.

    :param path: Path to the CSV file.
    :param dtype: Data type for the DataFrame columns.
    :return: Tuple containing the Dask DataFrame and the headers as a NumPy array.
    """
    print(path)
    print('reading columns')
    # Read only the first column to determine header rows
    col = dd.read_csv(path, usecols=[0])
    print('listing headers')
    # Determine header rows based on non-numeric values in the first column
    header_rows = {row[0] for row in enumerate(col.iloc[:, 0]) if type(row[1]) is str and not check_type(row[1])}
    # If header rows are found, add one more row as the last header row
    if len(header_rows) > 0:
        header_rows.add(max(header_rows) + 1)
    print('opening main dataframe')
    # Read the main DataFrame, skipping header rows if they exist
    if len(header_rows) > 0:
        df = dd.read_csv(path, skiprows=list(header_rows), dtype=dtype)
        # Find columns with all NaN values
        cols_with_all_nan = df.columns[df.isnull().all(axis=0).compute()]
        # Drop columns with all NaN values
        df = df.drop(cols_with_all_nan, axis=1)
        df.info(verbose=False, memory_usage="deep")
    else:
        # If no header rows, read the entire file as the DataFrame
        df = dd.read_csv(path, dtype=dtype)
        cols_with_all_nan = df.columns[df.isnull().all(axis=0).compute()]
        # Drop columns with all NaN values
        df = df.drop(cols_with_all_nan, axis=1)
        df.info(verbose=False, memory_usage="deep")
    print('opening headers')
    # Read the headers if they exist, otherwise use DataFrame columns as headers
    if len(header_rows) > 0:
        headers = dd.read_csv(path, skiprows=lambda x: x not in header_rows, dtype=str)
        headers = headers.dropna(how='all')
        headers.info(verbose=False, memory_usage="deep")
    else:
        headers = df.columns

    return df.compute(), headers.to_numpy()


def get_data(df: dd.DataFrame) -> tuple[dd.DataFrame, np.ndarray]:
    """
    trims dataframe to data
    :param df: dataframe
    :return: array of data and array of text
    """
    array = df.to_numpy()
    data = np.array([row.astype(float) for row in array if check_type(row)])
    text = np.array([row for row in array if not check_type(row)])
    return dd.DataFrame(data), text


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

print(header)
print(df)
