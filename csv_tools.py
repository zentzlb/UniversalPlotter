import dask as d
import dask.dataframe as dd
import dask.array as da

from functools import lru_cache


# import pyarrow


def open_csv(path: str, dtype=da.float64) -> tuple[dd.DataFrame, da.Array]:
    """
    opens csv file
    :param path: path to csv file
    :param dtype:
    :return: dataframe
    """
    print('reading columns')
    col = dd.read_csv(path, usecols=[0])
    print('listing headers')
    header_rows = {row[0] for row in enumerate(col.iloc[:, 0]) if type(row[1]) is str and not check_type(row[1])}
    header_rows.add(max(header_rows) + 1)
    print('opening main dataframe')
    df = pd.read_csv(path, skiprows=header_rows, dtype=dtype)
    print('opening headers')
    headers = pd.read_csv(path, skiprows=lambda x: x not in header_rows, dtype=str)
    print('dropping unused columns')
    headers.dropna(how='all', axis=1, inplace=True)
    headers.info(verbose=False, memory_usage="deep")
    df.dropna(how='all', axis=1, inplace=True)
    df.info(verbose=False, memory_usage="deep")

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



# import time
# t1 = time.time()
# df, header = open_csv(r"C:\DTS\SLICEWare\1.08.0868\Data\CSV\Drop Test Series\Drop_4.csv", dtype=np.float32)
# t2 = time.time()
# print(t2-t1)