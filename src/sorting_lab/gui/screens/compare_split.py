"""Side-by-side comparison views (manual + detailed batch)."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from sorting_lab.gui.screens.compare import CompareView
from sorting_lab.gui.screens.detail_compare import DetailCompareView


class CompareSplitView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._apply_theme()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("QSplitter::handle { background-color: #223156; }")
        splitter.addWidget(self._wrap_card(CompareView(), "Karşılaştırma"))
        splitter.addWidget(self._wrap_card(DetailCompareView(), "Detaylı Karşılaştırma"))
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        root.addWidget(splitter)

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background-color: #0b1222; color: #eef3ff; }
            QLabel#title { font-size: 18px; font-weight: 800; color: #f5f8ff; }
            QLabel#subtitle { color: #9fb2d9; font-size: 12px; }
            """
        )

    def _wrap_card(self, widget: QtWidgets.QWidget, title: str) -> QtWidgets.QFrame:
        frame = QtWidgets.QFrame()
        frame.setObjectName("card-wrapper")
        frame.setStyleSheet(
            """
            QFrame#card-wrapper {
                background-color: #111a30;
                border: 1px solid #223156;
                border-radius: 12px;
            }
            """
        )
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)

        h = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(title)
        lbl.setObjectName("title")
        h.addWidget(lbl)
        h.addStretch()
        layout.addLayout(h)

        widget.setMinimumHeight(400)
        widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(widget)

        frame.setGraphicsEffect(self._shadow())
        return frame

    def _shadow(self) -> QtWidgets.QGraphicsDropShadowEffect:
        effect = QtWidgets.QGraphicsDropShadowEffect()
        effect.setBlurRadius(24)
        effect.setXOffset(0)
        effect.setYOffset(12)
        effect.setColor(QtGui.QColor(0, 0, 0, 100))
        return effect


__all__ = ["CompareSplitView"]
