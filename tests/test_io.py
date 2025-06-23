from copy import deepcopy
from pathlib import Path

import pandas as pd
import pytest

from rawxio.rawx import (
    MissingRequiredFieldError,
    raise_on_missing_required_field,
    read_rawx,
    write_rawx,
)
from rawxio.utils import one2zero_indexed, zero2one_indexed


def minimal_rawx() -> Path:
    return Path(__file__).parent / "data" / "minimal_rawx.json"


def test_read():
    result = read_rawx(minimal_rawx())
    assert len(result) == 5  # noqa: PLR2004

    with_uid = ("bus", "load", "generator", "acline")
    assert all(result[k].index.name == "uid" for k in with_uid)


def test_read_write_round_trip(tmpdir: Path):
    result = read_rawx(minimal_rawx())
    outfname = tmpdir / "out.json"

    write_rawx(outfname, result)
    result2 = read_rawx(outfname)
    assert result.keys() == result2.keys()
    assert all(result[k].equals(result2[k]) for k in result)


def test_array_index_shifting():
    result = read_rawx(minimal_rawx())
    dfs = deepcopy(result)

    # Make sure all dfs where deep-copied
    assert all(dfs[k] is not result[k] for k in result)
    dfs = one2zero_indexed(dfs)
    dfs = zero2one_indexed(dfs)
    assert all(dfs[k].equals(result[k]) for k in result)


def test_raise_on_missing():
    df = pd.DataFrame({"a": []})

    with pytest.raises(MissingRequiredFieldError) as exc:
        raise_on_missing_required_field("bus", df)

    msg = "The following fields must be present for data frame bus: {'ibus'}. Got ['a']"

    assert msg in str(exc)


@pytest.mark.parametrize("index_name", ["mrid", "uid"])
def test_read_pick_up_index(tmpdir: Path, index_name: list[str]):
    df = pd.DataFrame({"ibus": 1}, index=pd.Index(["0xab"], name=index_name))
    out = tmpdir / "rawx.json"
    write_rawx(out, {"bus": df})
    result = read_rawx(out)
    assert result["bus"].index.name == index_name
