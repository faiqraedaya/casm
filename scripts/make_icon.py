"""Rebuild ``casm.ico`` from ``casm.svg``.

Run after editing the SVG: ``uv run python scripts/make_icon.py``.

Each size is rendered from the vector separately, so the small entries are
drawn at their own pixel grid rather than scaled down from 256 px. The ICO
holds PNG-compressed entries, which Windows has read since Vista.
"""

from __future__ import annotations

import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402

ASSETS = Path(__file__).resolve().parents[1] / "src" / "casm" / "gui" / "assets"
SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)


def render_png(renderer: QSvgRenderer, size: int) -> bytes:
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing, True)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)


def pack_ico(images: list[tuple[int, bytes]]) -> bytes:
    """ICONDIR, one ICONDIRENTRY per image, then the PNG payloads."""
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    entries, payload = b"", b""
    for size, png in images:
        dim = 0 if size >= 256 else size  # 0 means 256 in an ICO entry
        entries += struct.pack("<BBBBHHII", dim, dim, 0, 0, 1, 32, len(png), offset)
        payload += png
        offset += len(png)
    return header + entries + payload


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication(sys.argv)  # noqa: F841
    renderer = QSvgRenderer(str(ASSETS / "casm.svg"))
    if not renderer.isValid():
        print("casm.svg did not parse", file=sys.stderr)
        return 1
    images = [(size, render_png(renderer, size)) for size in SIZES]
    target = ASSETS / "casm.ico"
    target.write_bytes(pack_ico(images))
    print(f"{target} ({', '.join(str(s) for s in SIZES)} px)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
