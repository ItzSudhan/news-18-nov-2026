"""World news of Wednesday 18 November 2026 in one image.

The picture is entry.png beside this file, rendered from layout/map.html by render.sh.
This program checks that it meets the contest's limits (a whole PNG or JPEG, at most 1 MiB and 1024x1024)
and copies its bytes unchanged to /output/entry.png ($MAKEFUN_OUTPUT_DIR/entry.png outside the grader).
Standard library only, no network; every run writes the same bytes.
"""

import os
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
MAX_BYTES = 1024 * 1024
MAX_SIDE = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(data: bytes) -> tuple[int, int]:
    """Walk every chunk, checking each CRC, and return (width, height) from IHDR."""
    pos = len(PNG_SIGNATURE)
    width = height = 0
    saw_idat = False
    while pos + 12 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if len(body) != length:
            raise ValueError(f"PNG chunk {kind!r} is truncated")
        (crc,) = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        if zlib.crc32(kind + body) & 0xFFFFFFFF != crc:
            raise ValueError(f"PNG chunk {kind!r} has a bad CRC")
        if kind == b"IHDR":
            width, height = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            saw_idat = True
        elif kind == b"IEND":
            if pos + 12 + length != len(data):
                raise ValueError("bytes after IEND")
            if not saw_idat:
                raise ValueError("PNG has no image data")
            return width, height
        pos += 12 + length
    raise ValueError("PNG ends before IEND")


def jpeg_size(data: bytes) -> tuple[int, int]:
    """Return (width, height) from the first SOF marker; require the end-of-image marker."""
    if not data.endswith(b"\xff\xd9"):
        raise ValueError("JPEG has no end marker")
    pos = 2
    while pos + 4 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("JPEG segment marker expected")
        marker = data[pos + 1]
        (seg_len,) = struct.unpack(">H", data[pos + 2:pos + 4])
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            height, width = struct.unpack(">HH", data[pos + 5:pos + 9])
            return width, height
        pos += 2 + seg_len
    raise ValueError("JPEG has no frame header")


def check(data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise ValueError(f"{len(data)} bytes is over 1 MiB")
    if data.startswith(PNG_SIGNATURE):
        kind, (w, h) = "PNG", png_size(data)
    elif data.startswith(b"\xff\xd8\xff"):
        kind, (w, h) = "JPEG", jpeg_size(data)
    else:
        raise ValueError("not a PNG or JPEG")
    if not (0 < w <= MAX_SIDE and 0 < h <= MAX_SIDE):
        raise ValueError(f"{w}x{h} is over {MAX_SIDE}x{MAX_SIDE}")
    return f"{kind} {w}x{h}, {len(data)} bytes"


def main() -> int:
    data = SOURCE.read_bytes()
    try:
        summary = check(data)
    except ValueError as err:
        print(f"entry.png rejected: {err}", file=sys.stderr)
        return 1
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    tmp = out_dir / ".entry.png.tmp"
    tmp.write_bytes(data)
    os.replace(tmp, target)
    print(f"wrote {target}: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
