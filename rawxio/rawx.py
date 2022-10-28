"""Convert between base case and PSS/E rawx format.

"""
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union
from uuid import UUID

import pandas as pd

from rawxio.data_model import (
    PARAMETER_SETS,
    DataSetType,
    get_pk_fields,
    get_required_fields,
    has_primary_key,
)

logger = logging.getLogger(__name__)


def get_rawx_record_type(data: Union[List[Any], List[List[Any]]]) -> DataSetType:
    return DataSetType.DATA_SET if isinstance(data[0], list) else DataSetType.PARAMETER_SET


def uuid(value: Any) -> str:
    h = hashlib.md5(usedforsecurity=False)
    h.update(repr(value).encode("utf-8"))
    return str(UUID(bytes=h.digest()))


def read_rawx(fname: Path) -> Dict[str, pd.DataFrame]:
    """
    Read data from rawx format. The index of the returned dataframe is constructed in the
    following priotized order

    1. mrid (Master Resource Identifier) is used if present in a column
    2. uid (Unique Identifier) is used if present in a column
    3. If the table has primary keys, a uid is constructed by hashing the tuple of
        primary keys
    4. If none of the above apply, no index is set

    If a dataset has defined primary keys in the RAWX
    documentation, an index constructed by hashing the tuple of primary keys is added.
    The name of index is uid (Unique Identifier). If an uid alrady exists,
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
        elif "uid" in df.columns:
            df = df.set_index("uid")
        elif has_primary_key(key):
            # The frame has primary keys. We produce a hash value to use for index based
            # on the primary keys
            pk_fields = list(set(get_pk_fields(key)).intersection(df.columns))
            index = [uuid(t) for t in df[sorted(pk_fields)].itertuples()]
            df = df.set_index(pd.Index(index, name="uid"))
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
