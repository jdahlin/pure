from __future__ import annotations

from enum import Enum, auto


class PurityStatus(Enum):
    UNKNOWN = auto()
    PURE = auto()
    IMPURE = auto()


class PuritySource(Enum):
    UNKNOWN = auto()
    # Function is explicitly marked pure by the user (attribute or pragma)
    USER_MARK = auto()
    # Function purity was inferred transitively from analyzing callees
    IMPLICIT = auto()
    # Temporary assumption of purity to break recursion cycles
    DEFERRED = auto()
    # Builtin function known to be pure
    BUILTIN = auto()
    # External function (no definition in this module)
    EXTERNAL = auto()

