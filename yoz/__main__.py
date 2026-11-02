"""Convert stdin to stdout: ``python -m yoz < old.txt > new.txt``."""

import sys

from .converter import convert


def main() -> int:
    if len(sys.argv) > 1:
        sys.stdout.write(convert(" ".join(sys.argv[1:])) + "\n")
    else:
        sys.stdout.write(convert(sys.stdin.read()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
