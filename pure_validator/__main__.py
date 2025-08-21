import sys

from pure_validator.main import print_file_analysis

_MIN_ARGS = 2


def main() -> None:
    if len(sys.argv) < _MIN_ARGS:
        print("Usage: pure-validator <file1> [<file2> ...]")  # noqa: T201
        sys.exit(1)
    for file_path in sys.argv[1:]:
        print_file_analysis(file_path)


if __name__ == "__main__":
    main()
