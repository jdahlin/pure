import sys

from pure_validator.main import print_file_analysis


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: pure-validator <file1> [<file2> ...]")
        sys.exit(1)
    for file_path in sys.argv[1:]:
        print_file_analysis(file_path)

if __name__ == "__main__":
    main()
