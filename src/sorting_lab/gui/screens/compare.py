"""Algorithm comparison screen with styled cards and animated feedback."""

from __future__ import annotations

from typing import List

from PySide6 import QtWidgets, QtCore, QtGui
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

from sorting_lab.analysis.runner import run_experiments
from sorting_lab import algorithms


class CompareView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._apply_theme()
        self.setLayout(QtWidgets.QVBoxLayout())
        self._build_header()
        self._build_body()

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                      stop:0 #10182d, stop:1 #0c1122); color: #eef3ff; }
            QFrame, QGroupBox {
                background-color: #151f39;
                border: 1px solid #223156;
                border-radius: 10px;
            }
            QPushButton {
                background-color: #5b8def;
                border: none;
                color: white;
                padding: 10px 14px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #739df1; transform: translateY(-1px); }
            QPushButton:pressed { background-color: #4a7bd5; }
            QPushButton:disabled { background-color: #3a4a71; color: #cfd9ff; }
            QComboBox, QSpinBox, QListWidget {
                background-color: #0f1527;
                color: #eef3ff;
                border: 1px solid #30426e;
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item { padding: 6px; }
            QListWidget::item:selected { background-color: #5b8def; color: #ffffff; }
            QComboBox QAbstractItemView {
                background-color: #0f1527;
                selection-background-color: #5b8def;
                selection-color: #ffffff;
            }
            QProgressBar {
                background-color: #0f1527;
                border: 1px solid #223156;
                border-radius: 6px;
                text-align: center;
                color: #cdd8f5;
                height: 10px;
            }
            QProgressBar::chunk { background-color: #5b8def; border-radius: 6px; }
            QLabel#title { font-size: 18px; font-weight: 700; color: #f4f7ff; }
            QLabel#subtitle { color: #a8b8de; font-size: 12px; }
            QTableWidget {
                background-color: #0c1324;
                color: #eef3ff;
                border: 1px solid #223156;
                gridline-color: #223156;
                border-radius: 10px;
            }
            """
        )

    def _build_header(self) -> None:
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Karşılaştırma")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("Birden fazla algoritmayı aynı veri seti ve boyutta kıyasla.")
        subtitle.setObjectName("subtitle")
        text_box = QtWidgets.QVBoxLayout()
        text_box.addWidget(title)
        text_box.addWidget(subtitle)
        header.addLayout(text_box)
        header.addStretch()
        self.layout().addLayout(header)

    def _build_body(self) -> None:
        body = QtWidgets.QHBoxLayout()
        body.addWidget(self._build_form_card(), 1)
        body.addWidget(self._build_result_card(), 2)
        self.layout().addLayout(body)

    def _build_form_card(self) -> QtWidgets.QFrame:
        card = self._card()
        form = QtWidgets.QFormLayout(card)

        self.algo_list = QtWidgets.QListWidget()
        for algo in algorithms.available_algorithms():
            item = QtWidgets.QListWidgetItem(algo.name)
            item.setData(QtCore.Qt.UserRole, algo.key)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.algo_list.addItem(item)
        self.algo_list.setMinimumWidth(220)
        self.algo_list.setWordWrap(True)
        self.algo_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.algo_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.algo_list.setSpacing(4)

        self.dataset_combo = QtWidgets.QComboBox()
        self.dataset_combo.addItems(["random", "partial", "reverse"])
        self.dataset_combo.setMinimumWidth(160)
        self.dataset_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

        self.size_spin = QtWidgets.QSpinBox()
        self.size_spin.setRange(10, 200_000)
        self.size_spin.setValue(20_000)
        self.size_spin.setSingleStep(5_000)

        self.runs_spin = QtWidgets.QSpinBox()
        self.runs_spin.setRange(1, 10)
        self.runs_spin.setValue(3)

        self.run_btn = QtWidgets.QPushButton("Karşılaştır")
        self.run_btn.clicked.connect(self._on_compare)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()

        form.addRow("Algoritmalar:", self.algo_list)
        form.addRow("Veri seti:", self.dataset_combo)
        form.addRow("Boyut:", self.size_spin)
        form.addRow("Tekrar (runs):", self.runs_spin)
        form.addRow("", self.run_btn)
        form.addRow("", self.progress)
        return card

    def _build_result_card(self) -> QtWidgets.QFrame:
        card = self._card()
        v = QtWidgets.QVBoxLayout(card)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Sonuçlar")
        title.setObjectName("title")
        self.status_label = QtWidgets.QLabel("Hazır.")
        self.status_label.setObjectName("subtitle")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_label)
        v.addLayout(header)

        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Algoritma", "Dataset", "N", "Ortalama (s)", "Std (s)", "Bellek Δ (MB)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(220)
        self.table.setStyleSheet("QTableWidget { background-color: #0c1324; }")

        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(4, 3)))
        container = QtWidgets.QHBoxLayout()
        container.addWidget(self.table, 3)
        container.addWidget(self.canvas, 2)
        v.addLayout(container)

        self._result_card = card
        return card

    def _card(self) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setGraphicsEffect(self._shadow_effect())
        return card

    def _shadow_effect(self) -> QtWidgets.QGraphicsDropShadowEffect:
        effect = QtWidgets.QGraphicsDropShadowEffect()
        effect.setBlurRadius(20)
        effect.setXOffset(0)
        effect.setYOffset(10)
        effect.setColor(QtGui.QColor(0, 0, 0, 90))
        return effect

    def _fade_in(self, widget: QtWidgets.QWidget) -> None:
        shadow = widget.graphicsEffect()
        effect = QtWidgets.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        anim = QtCore.QPropertyAnimation(effect, b"opacity", widget)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.finished.connect(lambda: widget.setGraphicsEffect(shadow))
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _selected_algorithms(self) -> List[str]:
        keys: List[str] = []
        for i in range(self.algo_list.count()):
            item = self.algo_list.item(i)
            if item.checkState() == QtCore.Qt.Checked:
                keys.append(item.data(QtCore.Qt.UserRole))
        return keys

    def _on_compare(self) -> None:
        algos = self._selected_algorithms()
        if not algos:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "En az bir algoritma seçin.")
            return
        dataset = self.dataset_combo.currentText()
        size = self.size_spin.value()
        runs = self.runs_spin.value()

        self.status_label.setText("Çalıştırılıyor...")
        self.progress.setRange(0, 0)
        self.progress.show()
        self.run_btn.setEnabled(False)
        QtWidgets.QApplication.processEvents()

        df = run_experiments(algos, [size], dataset, runs=runs, save_path=None)
        self._render_table(df)
        self._render_chart(df)
        self.status_label.setText("Tamamlandı.")
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self._fade_in(self._result_card)
        self._pulse_status()

    def _pulse_status(self) -> None:
        effect = QtWidgets.QGraphicsOpacityEffect()
        self.status_label.setGraphicsEffect(effect)
        anim = QtCore.QPropertyAnimation(effect, b"opacity", self.status_label)
        anim.setDuration(800)
        anim.setStartValue(0.3)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _render_table(self, df) -> None:
        self.table.setRowCount(len(df))
        for row, (_, r) in enumerate(df.iterrows()):
            self.table.setItem(row, 0, QtWidgets.QTableWidgetItem(r["algorithm"]))
            self.table.setItem(row, 1, QtWidgets.QTableWidgetItem(str(r.get("dataset", ""))))
            self.table.setItem(row, 2, QtWidgets.QTableWidgetItem(str(r.get("size", ""))))
            self.table.setItem(row, 3, QtWidgets.QTableWidgetItem(f"{r['avg_time_s']:.4f}"))
            self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(f"{r['std_time_s']:.4f}"))
            mem = "-" if r["memory_mb"] is None else f"{r['memory_mb']:.3f}"
            self.table.setItem(row, 5, QtWidgets.QTableWidgetItem(mem))
        self.table.resizeColumnsToContents()

    def _render_chart(self, df) -> None:
        ax = self.canvas.figure.subplots()
        ax.clear()
        bars = ax.bar(df["algorithm"], df["avg_time_s"], color="#5b8def")
        ax.set_ylabel("Süre (s)")
        ax.set_title(f"{self.dataset_combo.currentText()} / n={self.size_spin.value()}")
        ax.grid(axis="y", alpha=0.2)
        for bar in bars:
            bar.set_alpha(0.85)
        self.canvas.draw()
