"""PySide6 GUI entrypoint."""

from __future__ import annotations

import sys
from PySide6 import QtWidgets

from sorting_lab.gui.screens.compare import CompareView
from sorting_lab.gui.screens.live_view import LiveView
from sorting_lab.gui.screens.single_run import SingleRunView


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Sorting Lab")
        self.resize(960, 640)
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(SingleRunView(), "Çalıştırma")
        tabs.addTab(CompareView(), "Karşılaştırma")
        tabs.addTab(LiveView(), "Adım Adım")
        tabs.setStyleSheet(
            """
            QTabWidget::pane { border: 1px solid #223156; background: #0b1222; }
            QTabBar::tab {
                background: #1a2440;
                color: #c7d6ff;
                padding: 10px 16px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2f70ff, stop:1 #3ac7ff);
                color: #ffffff;
            }
            """
        )
        self.setCentralWidget(tabs)


def run() -> int:
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
