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
        self._last_df = None
        self._apply_theme()
        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().setSpacing(12)
        self._build_header()
        self._build_body()

    def _apply_theme(self) -> None:
        self.setStyleSheet(
            """
            QWidget { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                      stop:0 #10182d, stop:1 #0c1122); color: #eef3ff; font-family: "Poppins", "Segoe UI", "Arial"; font-size: 12px; }
            QFrame#card {
                background-color: #151f39;
                border: 1px solid #223156;
                border-radius: 12px;
            }
            QFrame#info-card {
                background-color: #0f1a33;
                border: 1px dashed #2a3c63;
                border-radius: 10px;
            }
            QFrame#info-bar {
                background-color: #0f1a33;
                border-left: 4px solid #ffb347;
                border-radius: 8px;
            }
            QFrame#toggle-bar {
                background-color: #0f1a33;
                border: 1px solid #2a3c63;
                border-radius: 8px;
            }
            QToolButton#toggle-button {
                color: #dfe8ff;
                font-weight: 600;
                padding: 6px;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ff8f2f, stop:1 #ffb347);
                border: none;
                color: white;
                padding: 10px 14px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #ffa64a; transform: translateY(-1px); }
            QPushButton:pressed { background-color: #ff8f2f; }
            QPushButton:disabled { background-color: #3a4a71; color: #cfd9ff; }
            QComboBox, QSpinBox, QListWidget {
                background-color: #0f1527;
                color: #eef3ff;
                border: 1px solid #30426e;
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item { padding: 6px; }
            QListWidget::item:selected { background-color: #ffb347; color: #1a1a1a; }
            QListWidget::item:hover { background-color: #202a45; }
            QComboBox QAbstractItemView {
                background-color: #0f1527;
                selection-background-color: #ffb347;
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
            QProgressBar::chunk { background-color: #ffb347; border-radius: 6px; }
            QLabel#title { font-size: 18px; font-weight: 700; color: #f4f7ff; }
            QLabel#subtitle { color: #a8b8de; font-size: 12px; }
            QLabel#section-title { font-size: 13px; font-weight: 700; color: #d7e3ff; }
            QTableWidget {
                background-color: #0c1324;
                color: #eef3ff;
                border: 1px solid #223156;
                gridline-color: #223156;
                border-radius: 10px;
            }
            QHeaderView::section { background-color: #0f1629; color: #d8e4ff; border: none; padding: 4px; }
            QPushButton#chart-toggle {
                background-color: #1a2440;
                color: #c7d6ff;
                padding: 6px 12px;
                border-radius: 8px;
            }
            QPushButton#chart-toggle:checked {
                background-color: #ffb347;
                color: #1a1a1a;
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
        body.setSpacing(12)
        body.addWidget(self._build_form_card(), 1)
        body.addWidget(self._build_result_card(), 2)
        self.layout().addLayout(body)

    def _build_form_card(self) -> QtWidgets.QFrame:
        card = self._card()
        form = QtWidgets.QFormLayout(card)
        form.setVerticalSpacing(10)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.algo_list = QtWidgets.QListWidget()
        for algo in algorithms.available_algorithms():
            item = QtWidgets.QListWidgetItem(algo.name)
            item.setData(QtCore.Qt.UserRole, algo.key)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            self.algo_list.addItem(item)
        self.algo_list.setMinimumWidth(240)
        self.algo_list.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.algo_list.setWordWrap(True)
        self.algo_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.algo_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.algo_list.setSpacing(4)
        self.algo_list.itemClicked.connect(self._on_algo_clicked)
        self.algo_list.setCurrentRow(0)

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

        self.algo_info_card = QtWidgets.QFrame()
        self.algo_info_card.setObjectName("info-card")
        info_layout = QtWidgets.QVBoxLayout(self.algo_info_card)
        info_layout.setContentsMargins(8, 8, 8, 8)
        info_layout.setSpacing(6)
        self.algo_info_title = QtWidgets.QLabel("")
        self.algo_info_title.setObjectName("section-title")
        self.algo_info_desc = QtWidgets.QLabel("")
        self.algo_info_desc.setWordWrap(True)
        self.algo_info_desc.setObjectName("subtitle")
        info_layout.addWidget(self.algo_info_title)
        info_layout.addWidget(self.algo_info_desc)

        hint = QtWidgets.QLabel("İpucu: Çoklu karşılaştırma için kutuları işaretleyin.")
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)

        form.addRow(self._section_header("Seçimler"))
        form.addRow("Algoritmalar:", self.algo_list)
        form.addRow("", self.algo_info_card)
        form.addRow("", hint)
        form.addRow("Veri seti:", self.dataset_combo)
        form.addRow("Boyut:", self.size_spin)
        form.addRow("Tekrar (runs):", self.runs_spin)
        form.addRow("", self.run_btn)
        form.addRow("", self.progress)
        self._update_algo_info(self.algo_list.currentItem())
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

        controls = QtWidgets.QHBoxLayout()
        controls.addWidget(QtWidgets.QLabel("Grafik:"))
        self.bar_btn = QtWidgets.QPushButton("Bar")
        self.bar_btn.setObjectName("chart-toggle")
        self.bar_btn.setCheckable(True)
        self.line_btn = QtWidgets.QPushButton("Line")
        self.line_btn.setObjectName("chart-toggle")
        self.line_btn.setCheckable(True)
        self.bar_btn.setChecked(True)
        self.chart_type = "bar"
        self.bar_btn.clicked.connect(lambda: self._set_chart_type("bar"))
        self.line_btn.clicked.connect(lambda: self._set_chart_type("line"))
        controls.addWidget(self.bar_btn)
        controls.addWidget(self.line_btn)
        self.reset_chart_btn = QtWidgets.QPushButton("Grafiği Sıfırla")
        self.reset_chart_btn.clicked.connect(self._reset_chart)
        controls.addWidget(self.reset_chart_btn)
        controls.addStretch()
        v.addLayout(controls)

        self.table_toggle = QtWidgets.QToolButton()
        self.table_toggle.setObjectName("toggle-button")
        self.table_toggle.setText("Performans Tablosu")
        self.table_toggle.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.table_toggle.setArrowType(QtCore.Qt.DownArrow)
        self.table_toggle.setCheckable(True)
        self.table_toggle.setChecked(True)
        self.table_toggle.toggled.connect(self._toggle_table)
        toggle_bar = QtWidgets.QFrame()
        toggle_bar.setObjectName("toggle-bar")
        toggle_layout = QtWidgets.QHBoxLayout(toggle_bar)
        toggle_layout.setContentsMargins(6, 4, 6, 4)
        toggle_layout.addWidget(self.table_toggle)
        toggle_layout.addStretch()

        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Algoritma", "Dataset", "N", "Ortalama (s)", "Std (s)", "Bellek Δ (MB)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(220)
        self.table.setStyleSheet("QTableWidget { background-color: #0c1324; }")

        self.table_container = QtWidgets.QWidget()
        table_layout = QtWidgets.QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(6)
        table_layout.addWidget(toggle_bar)
        table_layout.addWidget(self.table)

        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(4, 3)))
        self.canvas.setMinimumWidth(420)
        container = QtWidgets.QHBoxLayout()
        container.addWidget(self.table_container, 2)
        container.addWidget(self.canvas, 4)
        container.setStretch(0, 2)
        container.setStretch(1, 4)
        v.addLayout(container)

        self.summary_bar = QtWidgets.QFrame()
        self.summary_bar.setObjectName("info-bar")
        bar_layout = QtWidgets.QHBoxLayout(self.summary_bar)
        bar_layout.setContentsMargins(10, 8, 10, 8)
        self.summary_label = QtWidgets.QLabel("Seçim yapıp karşılaştırmayı başlatın.")
        self.summary_label.setObjectName("subtitle")
        bar_layout.addWidget(self.summary_label)
        v.addWidget(self.summary_bar)

        self._result_card = card
        return card

    def _card(self) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setObjectName("card")
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
        self._update_summary(df)
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
        self._last_df = df
        ax = self.canvas.figure.subplots()
        ax.clear()
        self._apply_chart_style(ax)
        colors = self._chart_colors(len(df))
        y = list(df["avg_time_s"])
        labels = list(df["algorithm"])
        if self.chart_type == "line":
            x = list(range(len(y)))
            ax.plot(x, y, color="#3ac7ff", linewidth=2)
            ax.scatter(x, y, c=colors, s=50, zorder=3)
            ax.set_xticks(x)
            ax.set_xticklabels(labels)
            ax.fill_between(x, y, color="#3ac7ff", alpha=0.08)
        else:
            ax.bar(labels, y, color=colors)
        ax.set_ylabel("Süre (s)")
        ax.set_title(f"{self.dataset_combo.currentText()} / n={self.size_spin.value()}")
        ax.grid(axis="y", alpha=0.2)
        self.canvas.figure.tight_layout()
        self.canvas.draw()

    def _chart_colors(self, count: int) -> list[str]:
        palette = ["#3ac7ff", "#ffb347", "#7effa1", "#ff7a7a", "#b48bff", "#ffd166"]
        return [palette[i % len(palette)] for i in range(count)]

    def _apply_chart_style(self, ax) -> None:
        self.canvas.figure.set_facecolor("#0c1324")
        ax.set_facecolor("#0c1324")
        ax.tick_params(axis="x", colors="#d8e4ff", labelsize=9)
        ax.tick_params(axis="y", colors="#d8e4ff", labelsize=9)
        ax.yaxis.label.set_color("#d8e4ff")
        ax.title.set_color("#f4f7ff")
        for spine in ax.spines.values():
            spine.set_color("#223156")

    def _toggle_table(self, checked: bool) -> None:
        self.table.setVisible(checked)
        self.table_toggle.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)

    def _set_chart_type(self, chart_type: str) -> None:
        self.chart_type = chart_type
        self.bar_btn.setChecked(chart_type == "bar")
        self.line_btn.setChecked(chart_type == "line")
        if self._last_df is not None:
            self._render_chart(self._last_df)

    def _reset_chart(self) -> None:
        self._last_df = None
        self.canvas.figure.clear()
        ax = self.canvas.figure.subplots()
        self._apply_chart_style(ax)
        ax.set_title("Grafik sıfırlandı")
        self.canvas.draw()

    def _update_algo_info(self, item: QtWidgets.QListWidgetItem | None) -> None:
        if item is None:
            self.algo_info_title.setText("")
            self.algo_info_desc.setText("")
            return
        data = {
            "quick": "Böl ve fethet; pivot etrafında bölme. Pratikte hızlı, worst O(n^2).",
            "heap": "Heap tabanlı; O(n log n) ve in-place.",
            "shell": "Aralıklı insertion; pratikte hızlı, teori aralığa bağlı.",
            "merge": "Stabil ve O(n log n); ek bellek O(n).",
            "radix": "Basamak bazlı; sayısal veride çok hızlı.",
        }
        key = item.data(QtCore.Qt.UserRole)
        self.algo_info_title.setText(item.text())
        self.algo_info_desc.setText(data.get(key, ""))

    def _on_algo_clicked(self, item: QtWidgets.QListWidgetItem) -> None:
        self._update_algo_info(item)

    def _update_summary(self, df) -> None:
        if df.empty:
            self.summary_label.setText("Sonuç yok.")
            return
        fastest = df.loc[df["avg_time_s"].idxmin()]
        text = f"En hızlı: {fastest['algorithm']} ({fastest['avg_time_s']:.4f} s) | Dataset: {fastest['dataset']} | N: {fastest['size']}"
        self.summary_label.setText(text)

    def _section_header(self, title: str) -> QtWidgets.QWidget:
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(title)
        label.setObjectName("section-title")
        line = QtWidgets.QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffb347, stop:1 #ff8f2f);"
        )
        layout.addWidget(label)
        layout.addWidget(line, 1)
        return wrapper
