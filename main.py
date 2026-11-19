"""Entrypoint for the 19 November 2026 news-image entry.

The picture itself is drawn by render.py and shipped in this repository as
entry.png. All this program does is place a copy of that file where the
grader expects it: /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png
when that variable is set). It reads nothing from the network and writes
exactly the bytes of the shipped image, so two runs agree byte for byte.
"""

import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    if not os.path.isfile(source):
        print("error: entry.png is missing next to main.py", file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    shutil.copyfile(source, target)
    size = os.path.getsize(target)
    print("entry.png -> %s (%d bytes)" % (target, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
