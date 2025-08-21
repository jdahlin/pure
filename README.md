# Pure

Purity checker for Python code.

[![GitHub](https://img.shields.io/github/stars/jdahlin/pure?style=social)](https://github.com/jdahlin/pure)

## Overview

Pure is a static analysis tool for checking the purity of Python functions and modules. It analyzes Python source code and reports on side effects, global state usage, and other purity-related concerns.

## Features
- Recursively analyzes Python files in directories
- Reports purity violations and messages
- CLI and module entry point (`python -mpure`)
- Easy integration with CI/CD

## Installation

You can install Pure using [uv](https://github.com/astral-sh/uv):

```bash
uv pip install -e .
```

Or build a wheel:

```bash
uv build
```

## Usage

### Command Line

Analyze a single file:

```bash
python -mpure path/to/file.py
```

Analyze all Python files in a directory (recursively):

```bash
python -mpure path/to/directory
```

### As a Library

You can also use Pure programmatically:

```python
from pure.main import check_file
messages = check_file("path/to/file.py")
for msg in messages:
    print(msg)
```

## Project Structure

- `pure/` - Main source code
- `pure/tests/` - Test suite
- `pyproject.toml` - Project metadata and build configuration

## Contributing

Contributions are welcome! Please open issues or pull requests on [GitHub](https://github.com/jdahlin/pure).

## License

This project is licensed under the terms of the license found in the `LICENSE` file.

