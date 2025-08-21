import ast
import tokenize
from pathlib import Path

from pure.ir_constructor import IRConstructor
from pure.message import Message
from pure.purity_checker import PurityChecker


class PureError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def check_file(filename: str | Path) -> list[Message]:
    file_path = Path(filename)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    # Use tokenize.open() to handle different encodings, sometimes
    # specified as a leading '# -*- coding: utf-8 -*-' comment
    with tokenize.open(file_path) as f:
        source = f.read()

    # Pass 1: AST -> IR
    tree = ast.parse(source, filename=str(file_path))
    ir_constructor = IRConstructor(file_path, source=source)
    ir_constructor.visit(tree)
    module = ir_constructor.module

    # Pass 2: IR -> Purity Check
    purity_checker = PurityChecker(module)
    purity_checker.check()
    messages = purity_checker.messages

    return messages


def print_file_analysis(file_path: str | Path) -> None:
    for msg in check_file(file_path):
        print(msg)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)

    print_file_analysis(sys.argv[1])
