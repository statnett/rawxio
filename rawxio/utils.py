"""This module contains a set of utility functions included for convenience."""

import pandas as pd


def shift_array_indices(
    df: pd.DataFrame, amount: int, cols: set[str] | None = None
) -> pd.DataFrame:
    cols = cols or {"ibus", "jbus", "kbus"}
    columns = list(cols.intersection(df.columns))
    if not cols:
        return df
    df[columns] = df[columns].applymap(lambda x: x + amount)
    return df


def one2zero_indexed(
    data: dict[str, pd.DataFrame], cols: set[str] | None = None
) -> dict[str, pd.DataFrame]:
    """Shift array indices down one such that they start at zero.

    The format of the dict is the same as returned by read_rawx (or passed to write_rawx)
    """
    for k, df in data.items():
        data[k] = shift_array_indices(df, 1, cols)
    return data


def zero2one_indexed(
    data: dict[str, pd.DataFrame], cols: set[str] | None = None
) -> dict[str, pd.DataFrame]:
    """Shift array indices up one such that they start at one."""
    for k, df in data.items():
        data[k] = shift_array_indices(df, -1, cols)
    return data
