"""Live visualization screen for step-by-step sorting."""

from __future__ import annotations

from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from sorting_lab import algorithms
from sorting_lab.utils import data_gen


class ArrayCanvas(QtWidgets.QWidget):
    """Simple bar-plot style canvas for visualizing array states."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.data: List[int] = []
        self.setMinimumHeight(240)
        self.setAutoFillBackground(True)

    def set_data(self, data: List[int]) -> None:
        self.data = list(data)
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:  # type: ignore[override]
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor("#0b1021"))
        if not self.data:
            return
        w = self.width()
        h = self.height()
        n = len(self.data)
        bar_width = max(1, w // max(n, 1))
        max_val = max(self.data)
        scale = h / max(1, max_val)
        color = QtGui.QColor("#5b8def")
        for idx, val in enumerate(self.data):
            bar_h = int(val * scale)
            x = idx * bar_width
            y = h - bar_h
            painter.fillRect(x, y, bar_width - 1, bar_h, color)
        painter.end()


class LiveView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.steps: list[list[int]] = []
        self.step_idx = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._advance)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        controls = QtWidgets.QFormLayout()

        self.algo_combo = QtWidgets.QComboBox()
        for algo in algorithms.available_algorithms():
            self.algo_combo.addItem(algo.name, algo.key)

        self.dataset_combo = QtWidgets.QComboBox()
        self.dataset_combo.addItems(["random", "partial", "reverse"])

        self.size_spin = QtWidgets.QSpinBox()
        self.size_spin.setRange(10, 5000)
        self.size_spin.setValue(100)
        self.size_spin.setSingleStep(50)

        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_slider.setRange(5, 200)
        self.speed_slider.setValue(30)
        self.speed_slider.setToolTip("Kareler arası ms")

        self.run_btn = QtWidgets.QPushButton("Başlat")
        self.run_btn.clicked.connect(self._on_run)
        self.stop_btn = QtWidgets.QPushButton("Durdur")
        self.stop_btn.clicked.connect(self._on_stop)

        controls.addRow("Algoritma:", self.algo_combo)
        controls.addRow("Veri seti:", self.dataset_combo)
        controls.addRow("Boyut:", self.size_spin)
        controls.addRow("Hız (ms):", self.speed_slider)
        controls.addRow("", self.run_btn)
        controls.addRow("", self.stop_btn)

        layout.addLayout(controls)

        self.canvas = ArrayCanvas()
        layout.addWidget(self.canvas)

        self.progress = QtWidgets.QProgressBar()
        layout.addWidget(self.progress)
        self.status = QtWidgets.QLabel("Hazır.")
        layout.addWidget(self.status)

    def _on_run(self) -> None:
        algo_key = self.algo_combo.currentData()
        dataset = self.dataset_combo.currentText()
        size = self.size_spin.value()
        self.status.setText("Veri hazırlanıyor...")
        QtWidgets.QApplication.processEvents()

        data = data_gen.generate(dataset, size)
        self.canvas.set_data(data)
        self.status.setText("Algoritma çalışıyor...")
        QtWidgets.QApplication.processEvents()

        sorted_arr, steps = algorithms.run_algorithm(algo_key, data, record_steps=True, step_limit=800)
        # Ensure initial and final states are present
        if not steps or steps[0] != data:
            steps.insert(0, list(data))
        if steps[-1] != sorted_arr:
            steps.append(sorted_arr)

        self.steps = steps
        self.step_idx = 0
        self.progress.setRange(0, len(self.steps) - 1)
        self.progress.setValue(0)

        interval_ms = max(5, self.speed_slider.value())
        self.timer.start(interval_ms)
        self.status.setText(f"Adım adım gösterim ({len(self.steps)} kare).")

    def _on_stop(self) -> None:
        self.timer.stop()
        self.status.setText("Durdu.")

    def _advance(self) -> None:
        if not self.steps:
            self.timer.stop()
            self.status.setText("Gösterilecek adım yok.")
            return
        if self.step_idx >= len(self.steps):
            self.timer.stop()
            self.status.setText("Tamamlandı.")
            return
        self.canvas.set_data(self.steps[self.step_idx])
        self.progress.setValue(self.step_idx)
        self.step_idx += 1
