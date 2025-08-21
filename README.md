# Pure validator

Purity validator for Python code.

[![GitHub](https://img.shields.io/github/stars/jdahlin/pure?style=social)](https://github.com/jdahlin/pure)

## Overview

Pure validator is a static analysis tool for checking the purity of Python functions and modules. It analyzes Python source code and reports on side effects, global state usage, and other purity-related concerns.

Suppose you have the following code:

```python
def impure_function(): # pragma: pure
    print("This is impure!")
```

Running the purity checker, will report an error similar to:

```
example.py:3: Function 'impure_function' is marked as pure but has side effects (print statement)
```

## Features
- Recursively analyzes Python files in directories
- Reports purity violations and messages
- CLI and module entry point (`python -mpure_validator`)
- Easy integration with CI/CD

## Installation

You can install Pure via pip:

```bash
$ pip install pure-validator
```

## Usage

### Command Line


```bash
$ pure-validator file-or-directory
```

## Contributing

Contributions are welcome! Please open issues or pull requests on [GitHub](https://github.com/jdahlin/pure).

## License

This project is licensed under the terms of the license found in the `LICENSE` file.
