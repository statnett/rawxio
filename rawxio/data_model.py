from enum import Enum, auto
from typing import List

REQUIRED_PK_FIELDS = {
    "bus": ["ibus"],
    "rating": ["irate"],
    "load": ["ibus"],
    "fixshunt": ["ibus"],
    "generator": ["ibus"],
    "acline": ["ibus", "jbus"],
    "sysswd": ["ibus", "jbus"],
    "transformer": ["ibus", "jbus"],
    "area": ["iarea"],
    "twotermdc": ["name"],
    "vscdc": ["name"],
    "impcor": ["itable"],
    "ntermdc": ["name"],
    "ntermdcconv": ["name"],
    "ntermdcbus": ["name"],
    "ntermdclink": [
        "name",
        "idc",
        "jdc",
    ],
    "msline": ["ibus", "jbus"],
    "zone": ["izone"],
    "iatrans": ["arfrom", "arto"],
    "owner": ["iowner"],
    "facts": ["name"],
    "swshunt": ["ibus"],
    "gne": ["name"],
    "indmach": ["ibus"],
    "sub": ["isub"],
    "subnode": ["isub", "inode"],
    "subswd": ["isub", "inode", "jnode"],
    "subterm": ["isub", "inode", "type", "eqid", "ibus"],
}


# Fields that are optional. But if present, they should be included in the primary keys
OPTIONAL_PK_FIELDS = {
    "load": ["loadid"],
    "fixshunt": ["shntid"],
    "generator": ["machid"],
    "acline": ["ckt"],
    "sysswd": ["ckt"],
    "transformer": ["kbus", "ckt"],
    "impcor": ["tap"],
    "ntermdcconv": ["ib"],
    "ntermdcbus": ["idc"],
    "ntermdclink": ["dcckt"],
    "msline": ["mslid"],
    "iatrans": ["trid"],
    "swshunt": ["shntid"],
    "indmach": ["imid"],
    "subnode": ["ibus"],
    "subswd": ["swdid"],
    "subterm": ["jbus", "kbus"],
}

# List of fields that are required, but should not be part of the primary key
REQUIRED_NON_PK_FIELDS = {
    "twotermdc": ["ipr", "ipi"],
    "vscdc": ["ibus1", "ibus2"],
    "facts": ["ibus"],
}


def get_pk_fields(name: str) -> List[str]:
    return REQUIRED_PK_FIELDS.get(name, []) + OPTIONAL_PK_FIELDS.get(name, [])


def get_required_fields(name: str) -> List[str]:
    return REQUIRED_PK_FIELDS.get(name, []) + REQUIRED_NON_PK_FIELDS.get(name, [])


def has_primary_key(name: str) -> bool:
    return len(get_pk_fields(name)) > 0


PARAMETER_SETS = {"caseid", "general", "gauss", "newton", "adjust", "tysl", "solver"}


class DataSetType(Enum):
    """
    Rawx has two record types. ParameterSet and DataSet
    """

    PARAMETER_SET = auto()
    DATA_SET = auto()
