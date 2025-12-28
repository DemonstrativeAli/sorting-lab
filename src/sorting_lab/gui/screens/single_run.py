"""Single algorithm run screen with styled layout and subtle animation."""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from sorting_lab import algorithms
from sorting_lab.utils import data_gen, metrics


class SingleRunView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._apply_theme()
        self.setLayout(QtWidgets.QVBoxLayout())
        self._build_header()
        self._build_body()
        self._build_footer()

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                      stop:0 #10182d, stop:1 #0c1122); color: #eef3ff; }
            QGroupBox, QFrame {
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
                transition: all 120ms ease-in-out;
            }
            QPushButton:hover { background-color: #739df1; transform: translateY(-1px); }
            QPushButton:pressed { background-color: #4a7bd5; }
            QPushButton:disabled { background-color: #3a4a71; color: #cfd9ff; }
            QComboBox, QSpinBox, QTextEdit {
                background-color: #0f1527;
                color: #eef3ff;
                border: 1px solid #30426e;
                border-radius: 8px;
                padding: 6px;
            }
            QTableWidget {
                background-color: #0c1324;
                color: #eef3ff;
                border: 1px solid #223156;
                gridline-color: #223156;
                border-radius: 10px;
            }
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
            QHeaderView::section { background-color: #0f1629; color: #d8e4ff; border: none; }
            """
        )

    def _build_header(self) -> None:
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Tek Deneme")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("Algoritma seç, veriyi üret, süre/bellek ölçümlerini anında gör.")
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

        self.algo_combo = QtWidgets.QComboBox()
        for algo in algorithms.available_algorithms():
            self.algo_combo.addItem(algo.name, algo.key)
        self.algo_combo.setMinimumWidth(220)
        self.algo_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.algo_combo.setView(QtWidgets.QListView())
        self.algo_combo.currentIndexChanged.connect(self._update_algo_info)

        self.dataset_combo = QtWidgets.QComboBox()
        self.dataset_combo.addItems(["random", "partial", "reverse"])
        self.dataset_combo.setMinimumWidth(160)

        self.size_spin = QtWidgets.QSpinBox()
        self.size_spin.setRange(10, 200_000)
        self.size_spin.setValue(5_000)
        self.size_spin.setSingleStep(1_000)

        self.run_btn = QtWidgets.QPushButton("Çalıştır")
        self.run_btn.clicked.connect(self._on_run)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 1)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        self.progress.hide()

        self.algo_info = QtWidgets.QLabel("")
        self.algo_info.setWordWrap(True)
        self.algo_info.setObjectName("subtitle")
        self._update_algo_info()

        form.addRow("Algoritma:", self.algo_combo)
        form.addRow("", self.algo_info)
        form.addRow("Veri seti:", self.dataset_combo)
        form.addRow("Boyut:", self.size_spin)
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

        self.runtime_label = QtWidgets.QLabel("Süre: -")
        self.memory_label = QtWidgets.QLabel("Bellek (Δ): -")
        meta = QtWidgets.QHBoxLayout()
        meta.addWidget(self.runtime_label)
        meta.addWidget(self.memory_label)
        meta.addStretch()
        v.addLayout(meta)

        self.preview_table = QtWidgets.QTableWidget(20, 2)
        self.preview_table.setHorizontalHeaderLabels(["Giriş (ilk 20)", "Sıralı (ilk 20)"])
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.preview_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.preview_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.preview_table.setMaximumHeight(260)
        v.addWidget(self.preview_table)

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
        # Preserve existing shadow by restoring it after animation.
        shadow = widget.graphicsEffect()
        effect = QtWidgets.QGraphicsOpacityEffect()
        widget.setGraphicsEffect(effect)
        anim = QtCore.QPropertyAnimation(effect, b"opacity", widget)
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.finished.connect(lambda: widget.setGraphicsEffect(shadow))
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)

    def _on_run(self) -> None:
        algo_key = self.algo_combo.currentData()
        dataset = self.dataset_combo.currentText()
        size = self.size_spin.value()

        self.run_btn.setEnabled(False)
        self.progress.show()
        self.progress.setRange(0, 0)  # indeterminate
        self.status_label.setText("Çalıştırılıyor...")
        QtWidgets.QApplication.processEvents()

        base_data = data_gen.generate(dataset, size)

        result = metrics.measure(lambda: algorithms.run_algorithm(algo_key, base_data)[0])

        sorted_arr = result.output
        self._render_preview(base_data, sorted_arr)
        self.runtime_label.setText(f"Süre: {result.duration:.4f} s")
        if result.memory_mb is not None:
            self.memory_label.setText(f"Bellek (Δ): {result.memory_mb:.3f} MB")
        else:
            self.memory_label.setText("Bellek (Δ): ölçülmedi")
        self.status_label.setText("Tamamlandı.")
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self._fade_in(self._result_card)
        self._pulse_status()

    def _render_preview(self, before: list[int], after: list[int]) -> None:
        max_rows = self.preview_table.rowCount()
        for row in range(max_rows):
            b_val = str(before[row]) if row < len(before) else ""
            a_val = str(after[row]) if row < len(after) else ""
            self.preview_table.setItem(row, 0, QtWidgets.QTableWidgetItem(b_val))
            self.preview_table.setItem(row, 1, QtWidgets.QTableWidgetItem(a_val))
        self.preview_table.resizeColumnsToContents()

    def _build_footer(self) -> None:
        info = QtWidgets.QLabel("Not: Önizleme tablosu giriş ve çıkış dizilerinin ilk 20 elemanını gösterir; büyük veri setlerinde performans için sınırlıdır.")
        info.setWordWrap(True)
        info.setObjectName("subtitle")
        self.layout().addWidget(info)

    def _update_algo_info(self) -> None:
        data = {
            "quick": "Quick Sort: Ortalama O(n log n), kötü durumda O(n^2); in-place, böl ve fethet.",
            "heap": "Heap Sort: Her zaman O(n log n); in-place; tam ikili ağaç (heap) tabanlı.",
            "shell": "Shell Sort: Aralıklı insertion; pratikte hızlı, teorik üst sınır aralık dizisine bağlı.",
            "merge": "Merge Sort: O(n log n); ek bellek O(n); stabil ve böl/fethet yaklaşımı.",
            "radix": "Radix Sort: Sayısal verilere O(d*(n+k)); sabit tabanla çok hızlı, ek bellek gerektirir.",
        }
        key = self.algo_combo.currentData()
        self.algo_info.setText(data.get(key, ""))

    def _pulse_status(self) -> None:
        # Gentle pulse on status text after completion
        effect = QtWidgets.QGraphicsOpacityEffect()
        self.status_label.setGraphicsEffect(effect)
        anim = QtCore.QPropertyAnimation(effect, b"opacity", self.status_label)
        anim.setDuration(800)
        anim.setStartValue(0.3)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QtCore.QEasingCurve.InOutQuad)
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
