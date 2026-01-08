"""Detailed batch comparison view for fixed dataset/size matrix."""

from __future__ import annotations

from statistics import mean, stdev

import pandas as pd
from PySide6 import QtCore, QtWidgets
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

from sorting_lab import algorithms
from sorting_lab.gui.screens.compare import CompareView
from sorting_lab.utils import data_gen, metrics


class DetailCompareWorker(QtCore.QObject):
    finished = QtCore.Signal(object)
    canceled = QtCore.Signal()
    progress = QtCore.Signal(int, int, str)
    error = QtCore.Signal(str)

    def __init__(self, algos: list[str], datasets: list[str], sizes: list[int], runs: int) -> None:
        super().__init__()
        self.algos = list(algos)
        self.datasets = list(datasets)
        self.sizes = list(sizes)
        self.runs = runs
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run(self) -> None:
        try:
            records: list[dict[str, object]] = []
            total = len(self.algos) * len(self.datasets) * len(self.sizes)
            current = 0
            for dataset in self.datasets:
                for size in self.sizes:
                    if self._stop:
                        self.canceled.emit()
                        return
                    base_data = data_gen.generate(dataset, size)
                    for algo_key in self.algos:
                        if self._stop:
                            self.canceled.emit()
                            return
                        durations: list[float] = []
                        mems: list[float] = []
                        mem_peaks: list[float] = []
                        for _ in range(self.runs):
                            if self._stop:
                                self.canceled.emit()
                                return
                            result = metrics.measure(lambda: algorithms.run_algorithm(algo_key, base_data)[0])
                            durations.append(result.duration)
                            if result.memory_mb is not None:
                                mems.append(result.memory_mb)
                            if result.memory_peak_mb is not None:
                                mem_peaks.append(result.memory_peak_mb)
                        avg = mean(durations) if durations else 0.0
                        std = stdev(durations) if len(durations) > 1 else 0.0
                        memory = mean(mems) if mems else None
                        memory_peak = mean(mem_peaks) if mem_peaks else None
                        records.append(
                            {
                                "algorithm": algo_key,
                                "dataset": dataset,
                                "size": size,
                                "runs": self.runs,
                                "avg_time_s": avg,
                                "std_time_s": std,
                                "memory_mb": memory,
                                "memory_peak_mb": memory_peak,
                            }
                        )
                        current += 1
                        self.progress.emit(current, total, f"{dataset}/{size} - {algo_key}")
            df = pd.DataFrame.from_records(records)
            self.finished.emit(df)
        except Exception as exc:  # pragma: no cover - UI error reporting
            self.error.emit(str(exc))


class DetailCompareView(CompareView):
    def __init__(self) -> None:
        self._datasets = ["random", "partial", "reverse"]
        self._sizes = [1_000, 10_000, 100_000]
        self._full_df: pd.DataFrame | None = None
        self._bulk_canvases: dict[str, dict[int, FigureCanvasQTAgg]] = {}
        self._bulk_animations: dict[tuple[str, int], FuncAnimation] = {}
        self._dataset_frames: dict[str, QtWidgets.QFrame] = {}
        self._dataset_checks: dict[str, QtWidgets.QCheckBox] = {}
        self._fullscreen_window: QtWidgets.QMainWindow | None = None
        self._fullscreen_canvases: dict[tuple[str, int], FigureCanvasQTAgg] = {}
        self._fullscreen_animations: dict[tuple[str, int], FuncAnimation] = {}
        self._fullscreen_metric_combo: QtWidgets.QComboBox | None = None
        self._fullscreen_bar_btn: QtWidgets.QPushButton | None = None
        self._fullscreen_line_btn: QtWidgets.QPushButton | None = None
        self.fullscreen_btn: QtWidgets.QPushButton | None = None
        super().__init__()
        self._bulk_animation_duration_s = 0.175
        self._fullscreen_animation_duration_s = 0.175
        for checkbox in self._dataset_checks.values():
            checkbox.toggled.connect(self._on_filter_changed)

    def _build_header(self) -> None:
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Detaylı Karşılaştırma")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("3 veri seti × 3 boyut × tüm algoritmalar için toplu benchmark.")
        subtitle.setObjectName("subtitle")
        text_box = QtWidgets.QVBoxLayout()
        text_box.addWidget(title)
        text_box.addWidget(subtitle)
        header.addLayout(text_box)
        header.addStretch()
        self.layout().addLayout(header)

    def _build_form_card(self) -> QtWidgets.QFrame:
        card = self._card()
        card.setMaximumWidth(320)
        form = QtWidgets.QFormLayout(card)
        form.setVerticalSpacing(10)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        info = QtWidgets.QLabel(
            "Bu ekran tüm algoritmaları, random/partial/reverse veri setlerinde "
            "1000, 10000 ve 100000 boyutlarında otomatik çalıştırır."
        )
        info.setObjectName("subtitle")
        info.setWordWrap(True)

        algo_names = ", ".join(algo.name for algo in algorithms.available_algorithms())
        algo_label = QtWidgets.QLabel(algo_names)
        algo_label.setObjectName("subtitle")
        algo_label.setWordWrap(True)

        filter_note = QtWidgets.QLabel(
            "Not: Grafikler seçilen veri setleri için üç boyutu birlikte gösterir."
        )
        filter_note.setObjectName("subtitle")
        filter_note.setWordWrap(True)

        dataset_row = QtWidgets.QWidget()
        dataset_layout = QtWidgets.QHBoxLayout(dataset_row)
        dataset_layout.setContentsMargins(0, 0, 0, 0)
        dataset_layout.setSpacing(10)
        self._dataset_checks = {}
        for dataset in self._datasets:
            checkbox = QtWidgets.QCheckBox(dataset)
            checkbox.setChecked(True)
            self._dataset_checks[dataset] = checkbox
            dataset_layout.addWidget(checkbox)
        dataset_layout.addStretch()

        self.runs_spin = QtWidgets.QSpinBox()
        self.runs_spin.setRange(1, 10)
        self.runs_spin.setValue(3)

        self.run_btn = QtWidgets.QPushButton("Toplu Test")
        self.run_btn.clicked.connect(self._on_compare)
        self.stop_btn = QtWidgets.QPushButton("Durdur")
        self.stop_btn.setObjectName("stop-btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)

        self.progress = QtWidgets.QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.hide()

        form.addRow(self._section_header("Toplu Senaryo"))
        form.addRow("", info)
        form.addRow("Algoritmalar:", algo_label)
        form.addRow(self._section_header("Görünüm Filtresi"))
        form.addRow("Veri setleri:", dataset_row)
        form.addRow("", filter_note)
        form.addRow("Tekrar (runs):", self.runs_spin)
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()
        btn_box = QtWidgets.QWidget()
        btn_box.setLayout(btn_row)
        form.addRow("", btn_box)
        form.addRow("", self.progress)
        return card

    def _on_compare(self) -> None:
        if self._thread is not None and self._thread.isRunning():
            return
        algos = [algo.key for algo in algorithms.available_algorithms()]
        runs = self.runs_spin.value()
        total = len(algos) * len(self._datasets) * len(self._sizes)

        self.status_label.setText("Çalıştırılıyor...")
        self.progress.setRange(0, total)
        self.progress.setValue(0)
        self.progress.show()
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        QtWidgets.QApplication.processEvents()

        self._start_worker(DetailCompareWorker(algos, self._datasets, self._sizes, runs))

    def _on_worker_finished(self, df) -> None:
        self._full_df = df
        super()._on_worker_finished(df)
        if self.fullscreen_btn is not None:
            self.fullscreen_btn.setEnabled(self._full_df is not None and not self._full_df.empty)
        self._open_fullscreen_charts()

    def _on_filter_changed(self) -> None:
        if self._full_df is None:
            return
        self._render_chart(self._full_df)
        self._update_summary(self._full_df)

    def _selected_datasets(self) -> list[str]:
        return [dataset for dataset, checkbox in self._dataset_checks.items() if checkbox.isChecked()]

    def _on_metric_changed(self) -> None:
        try:
            if self._full_df is not None:
                self._stop_bulk_animations()
                self._render_chart(self._full_df)
                self._render_fullscreen_charts()
                self._sync_fullscreen_controls()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Uyarı", f"Metrik değiştirilirken hata: {str(e)}")

    def _render_empty_chart(self, message: str) -> None:
        self._stop_bulk_animations()
        for dataset_canvases in self._bulk_canvases.values():
            for canvas in dataset_canvases.values():
                canvas.figure.clear()
                ax = canvas.figure.add_subplot(111)
                self._apply_chart_style(ax)
                ax.text(0.5, 0.5, message, ha="center", va="center", color="#d8e4ff", fontsize=12)
                ax.set_axis_off()
                canvas.draw()

    def _render_chart(self, df) -> None:
        source_df = self._full_df if self._full_df is not None else df
        if source_df is None or source_df.empty:
            self._render_empty_chart("Sonuç yok.")
            return
        selected = self._selected_datasets()
        if not selected:
            self._render_empty_chart("Veri seti seçin.")
            return
        self._stop_bulk_animations()
        for dataset in self._datasets:
            frame = self._dataset_frames.get(dataset)
            if frame is not None:
                frame.setVisible(dataset in selected)
            if dataset not in selected:
                continue
            dataset_df = source_df[source_df["dataset"] == dataset]
            for size in self._sizes:
                size_df = dataset_df[dataset_df["size"] == size]
                canvas = self._bulk_canvases.get(dataset, {}).get(size)
                if canvas is None:
                    continue
                self._render_size_chart(canvas, size_df, dataset, size)
        self._last_df = source_df

    def _update_summary(self, df) -> None:
        source_df = self._full_df if self._full_df is not None else df
        if source_df is None or source_df.empty:
            self.summary_label.setText("Sonuç yok.")
            return
        selected = self._selected_datasets()
        if not selected:
            self.summary_label.setText("Veri seti seçin.")
            return
        lines: list[str] = []
        for dataset in selected:
            dataset_df = source_df[source_df["dataset"] == dataset]
            if dataset_df.empty:
                continue
            chunks: list[str] = []
            for size in self._sizes:
                size_df = dataset_df[dataset_df["size"] == size]
                if size_df.empty:
                    continue
                fastest = size_df.loc[size_df["avg_time_s"].idxmin()]
                chunks.append(f"n={size}: {fastest['algorithm']} ({fastest['avg_time_s']:.4f} s)")
            if chunks:
                lines.append(f"{dataset}: " + " | ".join(chunks))
        self.summary_label.setText("\n".join(lines) if lines else "Sonuç yok.")

    def _reset_chart(self) -> None:
        self._stop_bulk_animations()
        for dataset_canvases in self._bulk_canvases.values():
            for canvas in dataset_canvases.values():
                canvas.figure.clear()
                ax = canvas.figure.add_subplot(111)
                self._apply_chart_style(ax)
                ax.set_axis_off()
                canvas.draw()
        if self._full_df is not None:
            self.summary_label.setText("Grafik sıfırlandı (sonuçlar tabloda duruyor).")

    def _on_open_fullscreen(self) -> None:
        if self._full_df is None or self._full_df.empty:
            QtWidgets.QMessageBox.information(self, "Bilgi", "Önce toplu testi çalıştırın.")
            return
        self._open_fullscreen_charts()

    def _open_fullscreen_charts(self) -> None:
        if self._full_df is None or self._full_df.empty:
            return
        if self._fullscreen_window is not None:
            self._render_fullscreen_charts()
            self._fullscreen_window.raise_()
            self._fullscreen_window.activateWindow()
            return

        window = QtWidgets.QMainWindow()
        window.setWindowTitle("Detaylı Karşılaştırma - Tam Ekran")
        window.resize(1400, 900)
        window.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        window.destroyed.connect(self._clear_fullscreen_window)
        window.setStyleSheet(self.styleSheet())

        central = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Toplu Grafikler (3 × 3)")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("random / partial / reverse × 1000 / 10000 / 100000")
        subtitle.setObjectName("subtitle")
        title_box = QtWidgets.QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        root.addLayout(header)

        controls_card = QtWidgets.QFrame()
        controls_card.setObjectName("card")
        controls = QtWidgets.QHBoxLayout(controls_card)
        controls.setContentsMargins(12, 8, 12, 8)
        controls.setSpacing(12)

        type_label = QtWidgets.QLabel("Grafik Türü:")
        type_label.setObjectName("section-title")
        controls.addWidget(type_label)

        self._fullscreen_bar_btn = QtWidgets.QPushButton("📊 Bar")
        self._fullscreen_bar_btn.setObjectName("chart-toggle")
        self._fullscreen_bar_btn.setCheckable(True)
        self._fullscreen_bar_btn.clicked.connect(lambda: self._set_chart_type("bar"))
        self._fullscreen_line_btn = QtWidgets.QPushButton("📈 Line")
        self._fullscreen_line_btn.setObjectName("chart-toggle")
        self._fullscreen_line_btn.setCheckable(True)
        self._fullscreen_line_btn.clicked.connect(lambda: self._set_chart_type("line"))
        controls.addWidget(self._fullscreen_bar_btn)
        controls.addWidget(self._fullscreen_line_btn)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("color: #223156;")
        controls.addWidget(separator)

        metric_label = QtWidgets.QLabel("Metrik:")
        metric_label.setObjectName("section-title")
        controls.addWidget(metric_label)

        self._fullscreen_metric_combo = QtWidgets.QComboBox()
        self._fullscreen_metric_combo.addItems(
            ["Zaman (Ortalama)", "Bellek (Ek)", "Bellek (Toplam Peak)", "Standart Sapma", "Süre Karşılaştırması"]
        )
        self._fullscreen_metric_combo.currentIndexChanged.connect(self._on_fullscreen_metric_changed)
        self._fullscreen_metric_combo.setMinimumWidth(220)
        controls.addWidget(self._fullscreen_metric_combo)

        controls.addStretch()
        root.addWidget(controls_card)

        charts_widget = QtWidgets.QWidget()
        charts_layout = QtWidgets.QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(14)

        self._fullscreen_canvases = {}
        for dataset in self._datasets:
            dataset_frame = QtWidgets.QFrame()
            dataset_frame.setObjectName("card")
            dataset_layout = QtWidgets.QVBoxLayout(dataset_frame)
            dataset_layout.setContentsMargins(12, 10, 12, 12)
            dataset_layout.setSpacing(10)

            dataset_label = QtWidgets.QLabel(dataset)
            dataset_label.setObjectName("section-title")
            dataset_layout.addWidget(dataset_label)

            grid = QtWidgets.QGridLayout()
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(12)

            for idx, size in enumerate(self._sizes):
                size_frame = QtWidgets.QFrame()
                size_frame.setObjectName("card")
                size_layout = QtWidgets.QVBoxLayout(size_frame)
                size_layout.setContentsMargins(10, 8, 10, 10)
                size_layout.setSpacing(6)

                label = QtWidgets.QLabel(f"n={size}")
                label.setObjectName("subtitle")
                size_layout.addWidget(label)

                canvas = FigureCanvasQTAgg(plt.Figure(figsize=(8, 4.5)))
                canvas.setMinimumHeight(280)
                canvas.setStyleSheet("background-color: #0c1324;")
                self._prime_canvas(canvas)
                size_layout.addWidget(canvas)

                self._fullscreen_canvases[(dataset, size)] = canvas
                grid.addWidget(size_frame, 0, idx)

            dataset_layout.addLayout(grid)
            charts_layout.addWidget(dataset_frame)

        charts_layout.addStretch()

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setWidget(charts_widget)
        root.addWidget(scroll)

        window.setCentralWidget(central)
        self._fullscreen_window = window
        self._render_fullscreen_charts()
        self._sync_fullscreen_controls()
        window.showMaximized()

    def _clear_fullscreen_window(self, *_args: object) -> None:
        self._stop_fullscreen_animations()
        self._fullscreen_window = None
        self._fullscreen_canvases = {}
        self._fullscreen_animations = {}
        self._fullscreen_metric_combo = None
        self._fullscreen_bar_btn = None
        self._fullscreen_line_btn = None

    def _sync_fullscreen_controls(self) -> None:
        if self._fullscreen_metric_combo is not None:
            self._fullscreen_metric_combo.blockSignals(True)
            self._fullscreen_metric_combo.setCurrentIndex(self.chart_metric_combo.currentIndex())
            self._fullscreen_metric_combo.blockSignals(False)
        if self._fullscreen_bar_btn is not None and self._fullscreen_line_btn is not None:
            self._fullscreen_bar_btn.setChecked(self.chart_type == "bar")
            self._fullscreen_line_btn.setChecked(self.chart_type == "line")

    def _on_fullscreen_metric_changed(self, index: int) -> None:
        if self.chart_metric_combo.currentIndex() != index:
            self.chart_metric_combo.setCurrentIndex(index)

    def _render_fullscreen_charts(self) -> None:
        if self._fullscreen_window is None or not self._fullscreen_canvases:
            return
        self._stop_fullscreen_animations()
        if self._full_df is None or self._full_df.empty:
            for canvas in self._fullscreen_canvases.values():
                self._render_fullscreen_empty(canvas, "Sonuç yok.")
            return
        for dataset in self._datasets:
            dataset_df = self._full_df[self._full_df["dataset"] == dataset]
            for size in self._sizes:
                canvas = self._fullscreen_canvases.get((dataset, size))
                if canvas is None:
                    continue
                size_df = dataset_df[dataset_df["size"] == size]
                anim = self._render_fullscreen_chart(canvas, size_df, dataset, size)
                if anim is not None:
                    self._fullscreen_animations[(dataset, size)] = anim

    def _render_fullscreen_empty(self, canvas: FigureCanvasQTAgg, message: str) -> None:
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        self._apply_chart_style(ax)
        ax.text(0.5, 0.5, message, ha="center", va="center", color="#d8e4ff", fontsize=13)
        ax.set_axis_off()
        canvas.draw()

    def _render_fullscreen_chart(
        self, canvas: FigureCanvasQTAgg, df, dataset: str, size: int
    ) -> FuncAnimation | None:
        if df.empty:
            self._render_fullscreen_empty(canvas, "Sonuç yok.")
            return None

        labels = list(df["algorithm"])
        colors = self._chart_colors(len(labels))
        y, ylabel, title_suffix = self._metric_payload(df)
        title = f"{dataset} / n={size} - {title_suffix}"
        return self._animate_fullscreen_chart(canvas, labels, y, colors, ylabel, title)

    def _set_chart_type(self, chart_type: str) -> None:
        try:
            self.chart_type = chart_type
            self.bar_btn.setChecked(chart_type == "bar")
            self.line_btn.setChecked(chart_type == "line")
            self._stop_bulk_animations()
            if self._full_df is not None:
                self._render_chart(self._full_df)
                self._render_fullscreen_charts()
            self._sync_fullscreen_controls()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Uyarı", f"Grafik türü değiştirilirken hata: {str(e)}")

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

        controls_card = QtWidgets.QFrame()
        controls_card.setObjectName("card")
        controls_card.setMaximumHeight(80)
        controls = QtWidgets.QHBoxLayout(controls_card)
        controls.setContentsMargins(15, 10, 15, 10)
        controls.setSpacing(15)

        type_label = QtWidgets.QLabel("Grafik Türü:")
        type_label.setObjectName("section-title")
        controls.addWidget(type_label)

        self.bar_btn = QtWidgets.QPushButton("📊 Bar")
        self.bar_btn.setObjectName("chart-toggle")
        self.bar_btn.setCheckable(True)
        self.line_btn = QtWidgets.QPushButton("📈 Line")
        self.line_btn.setObjectName("chart-toggle")
        self.line_btn.setCheckable(True)
        self.bar_btn.setChecked(True)
        self.chart_type = "bar"
        self.bar_btn.clicked.connect(lambda: self._set_chart_type("bar"))
        self.line_btn.clicked.connect(lambda: self._set_chart_type("line"))
        controls.addWidget(self.bar_btn)
        controls.addWidget(self.line_btn)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("color: #223156;")
        controls.addWidget(separator)

        metric_label = QtWidgets.QLabel("Metrik:")
        metric_label.setObjectName("section-title")
        controls.addWidget(metric_label)

        self.chart_metric_combo = QtWidgets.QComboBox()
        self.chart_metric_combo.addItems(
            ["Zaman (Ortalama)", "Bellek (Ek)", "Bellek (Toplam Peak)", "Standart Sapma", "Süre Karşılaştırması"]
        )
        self.chart_metric_combo.currentIndexChanged.connect(self._on_metric_changed)
        self.chart_metric_combo.setMinimumWidth(200)
        controls.addWidget(self.chart_metric_combo)

        controls.addStretch()

        self.fullscreen_btn = QtWidgets.QPushButton("Tam Ekran")
        self.fullscreen_btn.setEnabled(False)
        self.fullscreen_btn.clicked.connect(self._on_open_fullscreen)
        controls.addWidget(self.fullscreen_btn)

        self.reset_chart_btn = QtWidgets.QPushButton("🔄 Sıfırla")
        self.reset_chart_btn.clicked.connect(self._reset_chart)
        controls.addWidget(self.reset_chart_btn)

        self.reset_hint = QtWidgets.QLabel("")
        self.reset_hint.setObjectName("subtitle")
        self.reset_hint.setMinimumWidth(140)
        controls.addWidget(self.reset_hint)

        v.addWidget(controls_card)

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

        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Algoritma", "Dataset", "N", "Ortalama (s)", "Std (s)", "Bellek Δ (MB)", "Bellek Peak (MB)"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setMinimumHeight(220)
        self.table.setStyleSheet("QTableWidget { background-color: #0c1324; }")

        self.table_container = QtWidgets.QWidget()
        table_layout = QtWidgets.QVBoxLayout(self.table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(6)
        table_layout.addWidget(toggle_bar)
        table_layout.addWidget(self.table)

        charts_widget = QtWidgets.QWidget()
        charts_layout = QtWidgets.QVBoxLayout(charts_widget)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        charts_layout.setSpacing(14)

        self._bulk_canvases = {}
        self._dataset_frames = {}
        for dataset in self._datasets:
            dataset_frame = QtWidgets.QFrame()
            dataset_frame.setObjectName("card")
            dataset_layout = QtWidgets.QVBoxLayout(dataset_frame)
            dataset_layout.setContentsMargins(12, 10, 12, 12)
            dataset_layout.setSpacing(10)

            dataset_label = QtWidgets.QLabel(dataset)
            dataset_label.setObjectName("section-title")
            dataset_layout.addWidget(dataset_label)

            grid = QtWidgets.QGridLayout()
            grid.setHorizontalSpacing(12)
            grid.setVerticalSpacing(12)
            self._bulk_canvases[dataset] = {}

            for idx, size in enumerate(self._sizes):
                size_frame = QtWidgets.QFrame()
                size_frame.setObjectName("card")
                size_layout = QtWidgets.QVBoxLayout(size_frame)
                size_layout.setContentsMargins(10, 8, 10, 10)
                size_layout.setSpacing(6)

                label = QtWidgets.QLabel(f"n={size}")
                label.setObjectName("subtitle")
                size_layout.addWidget(label)

                canvas = FigureCanvasQTAgg(plt.Figure(figsize=(7, 3.2)))
                canvas.setMinimumHeight(210)
                canvas.setStyleSheet("background-color: #0c1324;")
                self._prime_canvas(canvas)
                size_layout.addWidget(canvas)

                self._bulk_canvases[dataset][size] = canvas
                grid.addWidget(size_frame, 0, idx)

            dataset_layout.addLayout(grid)
            charts_layout.addWidget(dataset_frame)
            self._dataset_frames[dataset] = dataset_frame

        charts_layout.addStretch()

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setWidget(charts_widget)

        container = QtWidgets.QHBoxLayout()
        container.setSpacing(12)
        container.addWidget(self.table_container, 2)
        container.addWidget(scroll, 3)
        container.setStretch(0, 2)
        container.setStretch(1, 3)
        v.addLayout(container)

        self.summary_bar = QtWidgets.QFrame()
        self.summary_bar.setObjectName("info-bar")
        bar_layout = QtWidgets.QHBoxLayout(self.summary_bar)
        bar_layout.setContentsMargins(10, 8, 10, 8)
        self.summary_label = QtWidgets.QLabel("Seçim yapıp karşılaştırmayı başlatın.")
        self.summary_label.setObjectName("subtitle")
        self.summary_label.setWordWrap(True)
        bar_layout.addWidget(self.summary_label)
        v.addWidget(self.summary_bar)

        self._result_card = card
        return card

    def _metric_payload(self, df) -> tuple[list[float], str, str]:
        metric = self.chart_metric_combo.currentText()
        if metric == "Zaman (Ortalama)":
            return list(df["avg_time_s"]), "Süre (s)", "Ortalama Süre"
        if metric == "Bellek (Ek)":
            return self._memory_values(df, "memory_mb"), "Bellek Δ (MB)", "Ek Bellek (Peak Δ)"
        if metric == "Bellek (Toplam Peak)":
            return self._memory_values(df, "memory_peak_mb"), "Bellek Peak (MB)", "Toplam Bellek (Peak)"
        if metric == "Standart Sapma":
            return list(df["std_time_s"]), "Std Sapma (s)", "Zaman Standart Sapması"
        return list(df["avg_time_s"]), "Süre (s)", "Süre Karşılaştırması"

    def _render_size_chart(self, canvas: FigureCanvasQTAgg, df, dataset: str, size: int) -> None:
        labels = list(df["algorithm"])
        colors = self._chart_colors(len(labels))
        y, ylabel, title_suffix = self._metric_payload(df)
        title = f"{dataset} / n={size} - {title_suffix}"
        self._bulk_animations[(dataset, size)] = self._animate_size_chart(canvas, labels, y, colors, ylabel, title)

    def _stop_bulk_animations(self) -> None:
        for anim in self._bulk_animations.values():
            if hasattr(anim, "event_source") and anim.event_source is not None:
                anim.event_source.stop()
        self._bulk_animations.clear()

    def _stop_fullscreen_animations(self) -> None:
        for anim in self._fullscreen_animations.values():
            if hasattr(anim, "event_source") and anim.event_source is not None:
                anim.event_source.stop()
        self._fullscreen_animations.clear()

    def _animate_size_chart(
        self,
        canvas: FigureCanvasQTAgg,
        labels: list[str],
        y: list[float],
        colors: list[str],
        ylabel: str,
        title: str,
    ) -> FuncAnimation:
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        self._apply_chart_style(ax)
        if not y:
            ax.text(0.5, 0.5, "Sonuç yok.", ha="center", va="center", color="#d8e4ff", fontsize=12)
            ax.set_axis_off()
            canvas.draw()
            return FuncAnimation(canvas.figure, lambda _f: (), frames=1, interval=1)

        if self.chart_type == "line":
            x = list(range(len(y)))
            line, = ax.plot(
                [],
                [],
                color="#3ac7ff",
                linewidth=2.5,
                marker="o",
                markersize=6,
                alpha=0.9,
                markerfacecolor="white",
                markeredgecolor="#3ac7ff",
                markeredgewidth=1.5,
            )
            scatter = ax.scatter([], [], c=[], s=60, zorder=4, edgecolors="white", linewidths=1.5, alpha=0.85)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
            y_max = max(y) if y else 0
            ax.set_ylim(0, y_max * 1.2 if y_max > 0 else 1)
            ax.set_xlim(-0.5, len(x) - 0.5)
            offset = y_max * 0.04 if y_max > 0 else 0.05
            duration_s = getattr(self, "_bulk_animation_duration_s", self._animation_duration_s)
            total_frames = max(1, int(self._animation_fps * duration_s))
            value_labels = []
            for xi, yi in zip(x, y):
                label = ax.text(
                    xi,
                    yi + offset,
                    "",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    color="#f4f7ff",
                    weight="bold",
                )
                label.set_visible(False)
                value_labels.append(label)

            def animate_line(frame: int):
                progress = min(1.0, (frame + 1) / total_frames)
                idx = max(1, int(progress * len(x)))
                x_data = x[:idx]
                y_data = y[:idx]
                line.set_data(x_data, y_data)
                scatter.set_offsets(list(zip(x_data, y_data)))
                if len(x_data) > 0:
                    scatter.set_color(colors[:idx])
                for i, label in enumerate(value_labels):
                    if i < idx:
                        val = y[i]
                        label.set_text(f"{val:.4f}" if val < 1 else f"{val:.2f}")
                        label.set_x(x[i])
                        label.set_y(val + offset)
                        label.set_visible(True)
                    else:
                        label.set_visible(False)
                return [line, scatter, *value_labels]

            anim = FuncAnimation(
                canvas.figure,
                animate_line,
                frames=total_frames,
                interval=self._animation_interval_ms,
                blit=True,
                repeat=False,
            )
        else:
            x = list(range(len(labels)))
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=9)
            y_max = max(y) if y else 0
            ax.set_ylim(0, y_max * 1.2 if y_max > 0 else 1)
            ax.set_xlim(-0.5, len(x) - 0.5)
            bars = ax.bar(x, [0.0] * len(y), color=colors, alpha=0.9, edgecolor="white", linewidth=1.6)
            value_labels = []
            for bar in bars:
                label = ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    0,
                    "",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                    color="#f4f7ff",
                    weight="bold",
                )
                label.set_visible(False)
                value_labels.append(label)

            duration_s = getattr(self, "_bulk_animation_duration_s", self._animation_duration_s)
            total_frames = max(1, int(self._animation_fps * duration_s))

            def animate_bar(frame: int):
                progress = min(1.0, (frame + 1) / total_frames)
                for bar, val, label in zip(bars, y, value_labels):
                    height = val * progress
                    bar.set_height(height)
                    if progress >= 0.9:
                        label.set_text(f"{val:.4f}" if val < 1 else f"{val:.2f}")
                        label.set_x(bar.get_x() + bar.get_width() / 2.0)
                        label.set_y(height)
                        label.set_visible(True)
                    else:
                        label.set_visible(False)
                return [*bars, *value_labels]

            anim = FuncAnimation(
                canvas.figure,
                animate_bar,
                frames=total_frames,
                interval=self._animation_interval_ms,
                blit=True,
                repeat=False,
            )

        ax.set_ylabel(ylabel, fontsize=10, color="#d8e4ff", fontweight="bold")
        ax.set_title(title, fontsize=11, color="#f4f7ff", pad=12, fontweight="bold")
        ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
        ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
        canvas.figure.set_facecolor("#0c1324")
        canvas.figure.tight_layout(pad=1.6)
        canvas.draw_idle()
        return anim

    def _animate_fullscreen_chart(
        self,
        canvas: FigureCanvasQTAgg,
        labels: list[str],
        y: list[float],
        colors: list[str],
        ylabel: str,
        title: str,
    ) -> FuncAnimation:
        canvas.figure.clear()
        ax = canvas.figure.add_subplot(111)
        self._apply_chart_style(ax)
        if not y:
            ax.text(0.5, 0.5, "Sonuç yok.", ha="center", va="center", color="#d8e4ff", fontsize=13)
            ax.set_axis_off()
            canvas.draw()
            return FuncAnimation(canvas.figure, lambda _f: (), frames=1, interval=1)

        if self.chart_type == "line":
            x = list(range(len(y)))
            line, = ax.plot(
                [],
                [],
                color="#3ac7ff",
                linewidth=3.0,
                marker="o",
                markersize=7,
                alpha=0.9,
                markerfacecolor="white",
                markeredgecolor="#3ac7ff",
                markeredgewidth=1.7,
            )
            scatter = ax.scatter([], [], c=[], s=90, zorder=4, edgecolors="white", linewidths=1.7, alpha=0.85)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=10)
            y_max = max(y) if y else 0
            ax.set_ylim(0, y_max * 1.2 if y_max > 0 else 1)
            ax.set_xlim(-0.5, len(x) - 0.5)
            offset = y_max * 0.04 if y_max > 0 else 0.05
            duration_s = getattr(self, "_fullscreen_animation_duration_s", self._animation_duration_s)
            total_frames = max(1, int(self._animation_fps * duration_s))
            value_labels = []
            for xi, yi in zip(x, y):
                label = ax.text(
                    xi,
                    yi + offset,
                    "",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color="#f4f7ff",
                    weight="bold",
                )
                label.set_visible(False)
                value_labels.append(label)

            def animate_line(frame: int):
                progress = min(1.0, (frame + 1) / total_frames)
                idx = max(1, int(progress * len(x)))
                x_data = x[:idx]
                y_data = y[:idx]
                line.set_data(x_data, y_data)
                scatter.set_offsets(list(zip(x_data, y_data)))
                if len(x_data) > 0:
                    scatter.set_color(colors[:idx])
                for i, label in enumerate(value_labels):
                    if i < idx:
                        val = y[i]
                        label.set_text(f"{val:.4f}" if val < 1 else f"{val:.2f}")
                        label.set_x(x[i])
                        label.set_y(val + offset)
                        label.set_visible(True)
                    else:
                        label.set_visible(False)
                return [line, scatter, *value_labels]

            anim = FuncAnimation(
                canvas.figure,
                animate_line,
                frames=total_frames,
                interval=self._animation_interval_ms,
                blit=True,
                repeat=False,
            )
        else:
            x = list(range(len(labels)))
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=10)
            y_max = max(y) if y else 0
            ax.set_ylim(0, y_max * 1.2 if y_max > 0 else 1)
            ax.set_xlim(-0.5, len(x) - 0.5)
            bars = ax.bar(x, [0.0] * len(y), color=colors, alpha=0.9, edgecolor="white", linewidth=1.8)
            value_labels = []
            for bar in bars:
                label = ax.text(
                    bar.get_x() + bar.get_width() / 2.0,
                    0,
                    "",
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    color="#f4f7ff",
                    weight="bold",
                )
                label.set_visible(False)
                value_labels.append(label)

            duration_s = getattr(self, "_fullscreen_animation_duration_s", self._animation_duration_s)
            total_frames = max(1, int(self._animation_fps * duration_s))

            def animate_bar(frame: int):
                progress = min(1.0, (frame + 1) / total_frames)
                for bar, val, label in zip(bars, y, value_labels):
                    height = val * progress
                    bar.set_height(height)
                    if progress >= 0.9:
                        label.set_text(f"{val:.4f}" if val < 1 else f"{val:.2f}")
                        label.set_x(bar.get_x() + bar.get_width() / 2.0)
                        label.set_y(height)
                        label.set_visible(True)
                    else:
                        label.set_visible(False)
                return [*bars, *value_labels]

            anim = FuncAnimation(
                canvas.figure,
                animate_bar,
                frames=total_frames,
                interval=self._animation_interval_ms,
                blit=True,
                repeat=False,
            )

        ax.set_ylabel(ylabel, fontsize=12, color="#d8e4ff", fontweight="bold")
        ax.set_title(title, fontsize=13, color="#f4f7ff", pad=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
        ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
        canvas.figure.set_facecolor("#0c1324")
        canvas.figure.tight_layout(pad=2.0)
        canvas.draw_idle()
        return anim
