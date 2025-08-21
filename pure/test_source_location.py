#!/usr/bin/env python3
"""Test the SourceLocation.from_node class method."""

import ast
from pathlib import Path

from pure.ir import Loc

# Create a simple test case
test_code = """
def hello():
    print("Hello, world!")
"""

# Parse the code
tree = ast.parse(test_code, filename="test.py")

# Find the function definition node
func_node = tree.body[0]  # The function definition

# Test the from_node class method
location = Loc.from_node("test.py", func_node)

print(f"Created SourceLocation: {location}")
print(f"Filename: {location.path}")
print(f"Line number: {location.lineno}")
print(f"Column offset: {location.col_offset}")
print(f"End line: {location.end_lineno}")
print(f"End column: {location.end_col_offset}")

# Test with a Path object too
location2 = Loc.from_node(Path("test.py"), func_node)
print(f"\nWith Path object: {location2}")
