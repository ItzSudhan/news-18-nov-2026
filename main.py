"""World news of Wednesday 18 November 2026 in one image.

The picture is entry.png beside this file, rendered from layout/map.html by render.sh.
This program copies it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png outside the grader).
"""

import os
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"


def main() -> None:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, out_dir / "entry.png")


if __name__ == "__main__":
    main()
