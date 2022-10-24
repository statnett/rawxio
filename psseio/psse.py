"""Convert between base case and PSS/E rawx format.

"""
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Hashable, List, Union

import pandas as pd

from psseio.data_model import (
    PARAMETER_SETS,
    DataSetType,
    get_pk_fields,
    get_required_fields,
    has_primary_key,
)

logger = logging.getLogger(__name__)

HASH_SHIFT = sys.maxsize + 1  # Amount hash values must be shifted to avoid negative numbers


def get_rawx_record_type(data: Union[List[Any], List[List[Any]]]) -> DataSetType:
    return DataSetType.DATA_SET if isinstance(data[0], list) else DataSetType.PARAMETER_SET


def hex_uuid(value: Hashable) -> str:
    return hex(hash(value) + HASH_SHIFT)


def read_rawx(fname: Path) -> Dict[str, pd.DataFrame]:
    """
    Read data from rawx format. If a dataset has defined primary keys in the RAWX
    documentation, an index constructed by hashing the tuple of primary keys is added.
    The name of index is mrid (Master Resource Unique ID). If an mrid alrady exists,
    it will be used as index
    """
    with open(fname, "r") as infile:
        data = json.load(infile)

    result = {}
    for key, d in data["network"].items():
        data = d["data"]
        if get_rawx_record_type(data) == DataSetType.PARAMETER_SET:
            data = [data]
        df = pd.DataFrame(data, columns=d["fields"])

        if "mrid" in df.columns:
            df = df.set_index("mrid")
        elif has_primary_key(key):
            # The frame has primary keys. We produce a hash value to use for index based
            # on the primary keys
            pk_fields = list(set(get_pk_fields(key)).intersection(df.columns))
            index = [hex_uuid(t) for t in df[sorted(pk_fields)].itertuples()]
            df = df.set_index(pd.Index(index, name="mrid"))
        result[key] = df
    return result


def write_rawx(fname: Path, data: Dict[str, pd.DataFrame]):
    """
    Write dataframes to rawx format. If a dataframe as a named index, it will be included
    as a regular column
    """
    rawx_data = {}
    for k, df in data.items():
        if df.index.name:
            # If there is a named index, make it a regular column
            df = df.reset_index()
        raise_on_missing_required_field(k, df)
        fields = df.columns.tolist()
        d = df.to_dict(orient="split")["data"]
        if k in PARAMETER_SETS:
            d = d[0]
        rawx_data[k] = {"fields": fields, "data": d}

    with open(fname, "w") as out:
        json.dump({"network": rawx_data}, out, indent=4)


def raise_on_missing_required_field(name: str, df: pd.DataFrame):
    req_fields = set(get_required_fields(name))
    if not req_fields.issubset(set(df.columns)):
        raise ValueError(
            f"The following fields must be present for data frame {name}: "
            f"{req_fields}. Got {df.columns.tolist()}"
        )
