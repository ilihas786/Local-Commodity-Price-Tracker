import pandas as pd


def convert_to_datetime(column: object) -> pd.Series:
    return pd.to_datetime(column)
