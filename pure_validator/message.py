import ast
import dataclasses
import pathlib


@dataclasses.dataclass(frozen=True)
class Loc:
    """Stores source location information without keeping AST nodes."""

    path: pathlib.Path
    lineno: int | None = None
    col_offset: int | None = None
    end_lineno: int | None = None
    end_col_offset: int | None = None

    @classmethod
    def from_node(cls, path: pathlib.Path, node: ast.AST) -> "Loc":
        return cls(
            path=path,
            lineno=getattr(node, "lineno", None),
            col_offset=getattr(node, "col_offset", None),
            end_lineno=getattr(node, "end_lineno", None),
            end_col_offset=getattr(node, "end_col_offset", None),
        )

    def __str__(self) -> str:
        return f"{self.path}:{self.lineno or 0}:{self.col_offset or 0}"


@dataclasses.dataclass(frozen=True)
class Message:
    message: str
    loc: Loc

    def __str__(self) -> str:
        return f"{self.loc.path}:{self.loc.path}:{self.loc.col_offset}: {self.message}"
