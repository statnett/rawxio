"""
This module contains a set of utility functions included for convenience
"""
from typing import Dict, Optional, Set

import pandas as pd


def shift_array_indices(
    df: pd.DataFrame, amount: int, cols: Optional[Set[str]] = None
) -> pd.DataFrame:
    cols = cols or {"ibus", "jbus", "kbus"}
    cols = list(cols.intersection(df.columns))
    if not cols:
        return df
    df[cols] = df[cols].applymap(lambda x: x + amount)
    return df


def one2zero_indexed(
    data: Dict[str, pd.DataFrame], cols: Optional[Set[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Shift array indices down one such that they start at zero.
    The format of the dict is the same as returned by read_rawx (or passed to write_rawx)
    """
    for k, df in data.items():
        data[k] = shift_array_indices(df, 1)
    return data


def zero2one_indexed(
    data: Dict[str, pd.DataFrame], cols: Optional[Set[str]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Shift array indices up one such that they start at one
    """
    for k, df in data.items():
        data[k] = shift_array_indices(df, -1, cols)
    return data
