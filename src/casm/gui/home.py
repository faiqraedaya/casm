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

DESCRIPTION = (
    "Samples release scenarios, prepares them for Phast or Safeti, and trains "
    "a neural network on the results. The trained model predicts release "
    "consequences in milliseconds anywhere inside the sampled range."
)


class HomePage(QWidget):
    """Logo, title, description and the five stages, centred as one block."""

    LOGO_SIZE = 96
    TILE_W = 128
    TILE_H = 96
    TILE_ICON = 24
    # Wide enough for two lines at body size, narrow enough to read as a lead.
    TEXT_W = 520

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

        title = ly.title("Consequence Analysis Surrogate Model")
        title.setAlignment(Qt.AlignCenter)
        outer.addWidget(title, 0, Qt.AlignHCenter)
        outer.addSpacing(T.SPACING_ROW)

        lead = QLabel(DESCRIPTION)
        lead.setProperty("role", "lead")
        lead.setWordWrap(True)
        lead.setAlignment(Qt.AlignCenter)
        # Fixed, not maximum: a wrapping label with only a ceiling asks for its
        # narrowest width and wraps to a column of single words.
        lead.setFixedWidth(self.TEXT_W)
        # A wrapped label in a box layout is otherwise given its one-line
        # height, and the stretches above and below take the rest.
        lead.ensurePolished()
        lead.setMinimumHeight(lead.heightForWidth(self.TEXT_W))
        outer.addWidget(lead, 0, Qt.AlignHCenter)
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
