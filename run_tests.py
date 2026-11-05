"""Run the suite and fail if anything was skipped.

`python -m unittest` prints "OK (skipped=20)" when aiogram is missing, which
reads as success while the handler, command-menu, donation and spelling tests
never ran. CI must never accept that, so a skip is an error here.
"""

import sys
import unittest


def main() -> int:
    suite = unittest.defaultTestLoader.discover("tests", top_level_dir=".")
    result = unittest.TextTestRunner(verbosity=2).run(suite)

    if result.skipped:
        print(f"\n{len(result.skipped)} test(s) skipped — all of them must run here:")
        for test, reason in result.skipped:
            print(f"  {test}: {reason}")
        print("\nInstall the dependencies: pip install -r requirements.txt")
        return 1

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
