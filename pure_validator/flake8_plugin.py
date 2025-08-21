import ast
import dataclasses
import importlib.metadata
from collections.abc import Generator, Iterable
from typing import Any

from pure_validator.main import (
    check_file as pure_check_file,  # expected: returns iterable of messages
)


@dataclasses.dataclass
class _Message:
    line: int
    col: int
    code: str
    text: str


def _normalize_messages(raw: Iterable[Any]) -> Iterable[_Message]:
    for m in raw:
        if hasattr(m, "line") and hasattr(m, "col"):
            code = getattr(m, "code", "PUR000")
            text = getattr(m, "text", str(m))
            yield _Message(int(m.line), int(m.col), str(code), str(text))
        elif isinstance(m, dict):
            yield _Message(
                int(m.get("line", 1)),
                int(m.get("col", 0)),
                str(m.get("code", "PUR000")),
                str(m.get("text", "")),
            )
        else:
            # FIXME: add internal category for messages
            line, col, text = 1, 0, str(m)
            if isinstance(m, str) and ":" in m:
                parts = m.split(":", 2)
                line = int(parts[0])
                col = int(parts[1]) if len(parts) > 1 else 0
                text = parts[2].strip() if len(parts) > 2 else text
            yield _Message(line, col, "PUR000", text)


Result = tuple[int, int, str, type["PureFlake8Plugin"]]


class PureFlake8Plugin:
    name = "flake8-pure"
    version = importlib.metadata.version("pure-validator")
    CODE_PREFIX = "PUR"

    def __init__(self, tree: ast.AST, filename: str, lines: list[str]) -> None:
        self._tree = tree
        self._filename = filename
        self._lines = lines

    def run(self) -> Generator[Result, None, None]:
        if self._filename == "stdin":
            raise NotImplementedError

        raw = pure_check_file(self._filename)
        for m in _normalize_messages(raw):
            if m.code.startswith(self.CODE_PREFIX):
                code = m.code
            else:
                code = f"{self.CODE_PREFIX}000"
            yield (m.line, m.col, f"{code} {m.text}", type(self))
