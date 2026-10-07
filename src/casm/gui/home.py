"""The landing page: what the application is, and a way into each stage.

It carries no state and runs nothing. The five tiles repeat the rail's
destinations in the same order, with the same numbers and icons, so the page
teaches the rail rather than offering a second way of naming things.
"""

from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel, QSizePolicy, QToolButton, QWidget

from .. import theme as T
from . import layout as ly
from .icons import icon, logo_pixmap
from .sidebar import PAGES

class HomePage(QWidget):
    """Logo, name, full name and the five stages, centred as one block."""

    LOGO_SIZE = 96
    TILE_W = 128
    TILE_H = 96
    TILE_ICON = 24

    def __init__(self, open_page: Callable[[int], None], parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Home")
        outer = ly.vbox(self, spacing=0)
        outer.addStretch(1)

        logo = QLabel()
        logo.setPixmap(logo_pixmap(self.LOGO_SIZE))
        logo.setFixedSize(self.LOGO_SIZE, self.LOGO_SIZE)
        outer.addWidget(logo, 0, Qt.AlignHCenter)
        outer.addSpacing(T.SPACING_GROUP)

        name = ly.title("CASM")
        outer.addWidget(name, 0, Qt.AlignHCenter)
        outer.addSpacing(T.SPACING_ROW // 2)

        full_name = QLabel("Consequence Analysis Surrogate Model")
        full_name.setProperty("role", "lead")
        outer.addWidget(full_name, 0, Qt.AlignHCenter)
        outer.addSpacing(T.SPACING_SECTION)

        tiles = ly.hbox(spacing=T.SPACING_ROW + 4)
        tiles.addStretch(1)
        self.tiles: list[QToolButton] = []
        for index, (_key, label, glyph) in enumerate(PAGES):
            if _key == "home":
                continue
            tile = QToolButton()
            tile.setProperty("variant", "tile")
            tile.setText(label)
            tile.setIcon(icon(glyph, self.TILE_ICON))
            tile.setIconSize(QSize(self.TILE_ICON, self.TILE_ICON))
            tile.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            tile.setFixedSize(self.TILE_W, self.TILE_H)
            tile.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            tile.setCursor(Qt.PointingHandCursor)
            tile.clicked.connect(lambda _checked=False, i=index: open_page(i))
            tiles.addWidget(tile)
            self.tiles.append(tile)
        tiles.addStretch(1)
        outer.addLayout(tiles)

        outer.addStretch(1)
