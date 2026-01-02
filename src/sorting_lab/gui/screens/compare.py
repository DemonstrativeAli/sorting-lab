"""Algorithm comparison screen with styled cards and animated feedback."""

from __future__ import annotations

from typing import List

from PySide6 import QtWidgets, QtCore, QtGui
import pandas as pd
from statistics import mean, stdev
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import numpy as np

from sorting_lab import algorithms
from sorting_lab.utils import data_gen, metrics


class CompareWorker(QtCore.QObject):
    finished = QtCore.Signal(object)
    canceled = QtCore.Signal()
    progress = QtCore.Signal(int, int, str)
    error = QtCore.Signal(str)

    def __init__(self, algos: list[str], size: int, dataset: str, runs: int) -> None:
        super().__init__()
        self.algos = list(algos)
        self.size = size
        self.dataset = dataset
        self.runs = runs
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def run(self) -> None:
        try:
            records: list[dict[str, object]] = []
            total = len(self.algos)
            for idx, algo_key in enumerate(self.algos, start=1):
                if self._stop:
                    self.canceled.emit()
                    return
                base_data = data_gen.generate(self.dataset, self.size)
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
                        "dataset": self.dataset,
                        "size": self.size,
                        "runs": self.runs,
                        "avg_time_s": avg,
                        "std_time_s": std,
                        "memory_mb": memory,
                        "memory_peak_mb": memory_peak,
                    }
                )
                self.progress.emit(idx, total, algo_key)
            df = pd.DataFrame.from_records(records)
            self.finished.emit(df)
        except Exception as exc:  # pragma: no cover - UI error reporting
            self.error.emit(str(exc))


class CompareView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._last_df = None
        self._worker = None
        self._thread = None
        self._animation = None
        self._chart_data = None
        self._current_chart_index = 0
        self._animation_interval_ms = 16
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
            QPushButton#stop-btn { background-color: #ff5b5b; color: #ffffff; }
            QPushButton#stop-btn:hover { background-color: #ff7373; }
            QPushButton#stop-btn:disabled { background-color: #663333; color: #f0bcbc; }
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
        self.stop_btn = QtWidgets.QPushButton("Durdur")
        self.stop_btn.setObjectName("stop-btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)

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

        self.case_info_card = QtWidgets.QFrame()
        self.case_info_card.setObjectName("info-card")
        case_layout = QtWidgets.QVBoxLayout(self.case_info_card)
        case_layout.setContentsMargins(8, 8, 8, 8)
        case_layout.setSpacing(6)
        self.case_info_title = QtWidgets.QLabel("Best/Worst Senaryo")
        self.case_info_title.setObjectName("section-title")
        self.case_info_body = QtWidgets.QLabel("")
        self.case_info_body.setWordWrap(True)
        self.case_info_body.setObjectName("subtitle")
        case_layout.addWidget(self.case_info_title)
        case_layout.addWidget(self.case_info_body)

        hint = QtWidgets.QLabel("İpucu: Çoklu karşılaştırma için kutuları işaretleyin.")
        hint.setObjectName("subtitle")
        hint.setWordWrap(True)

        form.addRow(self._section_header("Seçimler"))
        form.addRow("Algoritmalar:", self.algo_list)
        form.addRow("", self.algo_info_card)
        form.addRow("", self.case_info_card)
        form.addRow("", hint)
        form.addRow("Veri seti:", self.dataset_combo)
        form.addRow("Boyut:", self.size_spin)
        form.addRow("Tekrar (runs):", self.runs_spin)
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()
        btn_box = QtWidgets.QWidget()
        btn_box.setLayout(btn_row)
        form.addRow("", btn_box)
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

        # Kontrol paneli - daha güzel görünüm için card içinde
        controls_card = QtWidgets.QFrame()
        controls_card.setObjectName("card")
        controls_card.setMaximumHeight(80)
        controls = QtWidgets.QHBoxLayout(controls_card)
        controls.setContentsMargins(15, 10, 15, 10)
        controls.setSpacing(15)
        
        # Grafik türü seçimi
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
        
        # Ayırıcı
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator.setStyleSheet("color: #223156;")
        controls.addWidget(separator)
        
        # Metrik seçimi
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
        
        # Sıfırla butonu
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

        # Ana grafik canvas - tek grafik, daha büyük
        self.canvas = FigureCanvasQTAgg(plt.Figure(figsize=(8, 4.5)))
        self.canvas.setMinimumWidth(600)
        self.canvas.setMinimumHeight(350)
        self._prime_canvas(self.canvas)
        
        # İkinci grafik canvas (detaylı karşılaştırma için) - alt kısımda
        self.canvas2 = FigureCanvasQTAgg(plt.Figure(figsize=(8, 3.5)))
        self.canvas2.setMinimumWidth(600)
        self.canvas2.setMinimumHeight(280)
        self._prime_canvas(self.canvas2)
        
        # Grafik toggle butonu - başlangıçta açık
        self.detail_chart_toggle = QtWidgets.QPushButton("▲ Detaylı Karşılaştırma Gizle")
        self.detail_chart_toggle.setObjectName("chart-toggle")
        self.detail_chart_toggle.setCheckable(True)
        self.detail_chart_toggle.setChecked(True)  # Başlangıçta açık
        self.detail_chart_toggle.toggled.connect(self._toggle_detail_chart)
        
        chart_container = QtWidgets.QVBoxLayout()
        chart_container.setSpacing(10)
        chart_container.addWidget(self.canvas, 1)
        chart_container.addWidget(self.detail_chart_toggle)
        chart_container.addWidget(self.canvas2, 1)
        
        container = QtWidgets.QHBoxLayout()
        container.setSpacing(12)
        container.addWidget(self.table_container, 2)
        container.addLayout(chart_container, 3)
        container.setStretch(0, 2)
        container.setStretch(1, 3)
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
        if self._thread is not None and self._thread.isRunning():
            return
        algos = self._selected_algorithms()
        if not algos:
            QtWidgets.QMessageBox.warning(self, "Uyarı", "En az bir algoritma seçin.")
            return
        dataset = self.dataset_combo.currentText()
        size = self.size_spin.value()
        runs = self.runs_spin.value()

        self.status_label.setText("Çalıştırılıyor...")
        self.progress.setRange(0, len(algos))
        self.progress.setValue(0)
        self.progress.show()
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        QtWidgets.QApplication.processEvents()

        self._worker = CompareWorker(algos, size, dataset, runs)
        self._thread = QtCore.QThread(self)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_worker_finished)
        self._worker.canceled.connect(self._on_worker_canceled)
        self._worker.error.connect(self._on_worker_error)

        for sig in (self._worker.finished, self._worker.canceled, self._worker.error):
            sig.connect(self._thread.quit)
            sig.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

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
            mem_peak = "-" if r.get("memory_peak_mb") is None else f"{r['memory_peak_mb']:.3f}"
            self.table.setItem(row, 6, QtWidgets.QTableWidgetItem(mem_peak))
        self.table.resizeColumnsToContents()

    def _render_chart(self, df) -> None:
        try:
            self._last_df = df
            self._stop_animation()
            
            # Önceki axes'leri tamamen temizle
            self.canvas.figure.clear()
            self.canvas2.figure.clear()
            
            # Ana grafik - yeni axes oluştur
            ax = self.canvas.figure.add_subplot(111)
            self._apply_chart_style(ax)
            
            # İkinci grafik (detaylı karşılaştırma) - her zaman göster
            ax2 = self.canvas2.figure.add_subplot(111)
            self._apply_chart_style(ax2)
            
            colors = self._chart_colors(len(df))
            labels = list(df["algorithm"])
            title_prefix = f"{self.dataset_combo.currentText()} / n={self.size_spin.value()}"
            
            # Metrik seçimine göre veri hazırla
            metric = self.chart_metric_combo.currentText()
            if metric == "Zaman (Ortalama)":
                y = list(df["avg_time_s"])
                ylabel = "Süre (s)"
                title_suffix = "Ortalama Süre"
                secondary_info = None
            elif (memory_config := self._memory_metric_config(metric)) is not None:
                primary_key, primary_title, primary_ylabel, secondary_key, secondary_title, secondary_ylabel = memory_config
                y = self._memory_values(df, primary_key)
                ylabel = primary_ylabel
                title_suffix = primary_title
                secondary_info = (secondary_key, secondary_title, secondary_ylabel)
            elif metric == "Standart Sapma":
                y = list(df["std_time_s"])
                ylabel = "Std Sapma (s)"
                title_suffix = "Zaman Standart Sapması"
                secondary_info = None
            else:  # Süre Karşılaştırması
                # Saniye cinsinden göster
                y = list(df["avg_time_s"])
                ylabel = "Süre (s)"
                title_suffix = "Süre Karşılaştırması"
                secondary_info = None
            
            # Ana grafik - animasyonlu
            self._chart_data = {
                "y": y,
                "labels": labels,
                "colors": colors,
                "ylabel": ylabel,
                "title": f"{title_prefix} - {title_suffix}"
            }
            
            # İkinci grafik - detaylı karşılaştırma (her zaman göster)
            try:
                if secondary_info:
                    sec_key, sec_title, sec_ylabel = secondary_info
                    self._render_memory_chart(ax2, df, sec_key, f"{title_prefix} - {sec_title}", sec_ylabel)
                else:
                    self._render_comparison_chart(ax2, df)
                self.canvas2.figure.set_facecolor("#0c1324")
                self.canvas2.figure.tight_layout(pad=2.0)
                self.canvas2.draw()
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Uyarı", f"Detaylı grafik çizilirken hata: {str(e)}")
            
            self.canvas.figure.set_facecolor("#0c1324")
            self.canvas.figure.tight_layout(pad=2.0)
            self.canvas.draw()
            
            # Canvas2'yi her zaman göster ve layout'u güncelle
            self.canvas2.setVisible(True)
            self.canvas2.show()
            self.detail_chart_toggle.setChecked(True)
            self.detail_chart_toggle.setText(
                "▲ İkinci Bellek Grafiğini Gizle" if secondary_info else "▲ Detaylı Karşılaştırma Gizle"
            )
            
            # Animasyonu otomatik başlat
            self._start_animation()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Hata", f"Grafik çizilirken hata oluştu: {str(e)}")
            self.status_label.setText(f"Hata: {str(e)}")

    def _render_comparison_chart(self, ax, df) -> None:
        """İkinci grafikte detaylı karşılaştırma göster"""
        labels = list(df["algorithm"])
        x = np.arange(len(labels))
        width = 0.25
        
        # Normalize edilmiş değerler (0-1 arası)
        times = np.array(df["avg_time_s"])
        times_norm = times / times.max() if times.max() > 0 else times
        
        memories = np.array(self._memory_values(df, "memory_mb"))
        memories_norm = memories / memories.max() if memories.max() > 0 else memories
        
        stds = np.array(df["std_time_s"])
        stds_norm = stds / stds.max() if stds.max() > 0 else stds
        
        colors = self._chart_colors(3)
        ax.bar(x - width, times_norm, width, label="Zaman (norm)", color=colors[0], alpha=0.8)
        ax.bar(x, memories_norm, width, label="Bellek Δ (norm)", color=colors[1], alpha=0.8)
        ax.bar(x + width, stds_norm, width, label="Std Sapma (norm)", color=colors[2], alpha=0.8)
        
        ax.set_ylabel("Normalize Değer", fontsize=11, color="#d8e4ff", fontweight='bold')
        ax.set_title("Detaylı Performans Karşılaştırması", fontsize=12, color="#f4f7ff", pad=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=10)
        ax.legend(loc='upper left', fontsize=9, framealpha=0.4, facecolor='#0c1324', edgecolor='#223156')
        ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
        ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
        ax.set_ylim(0, 1.1)
        # Arka plan rengini ayarla
        ax.set_facecolor("#0c1324")

    def _start_animation(self) -> None:
        """Grafik animasyonunu başlat"""
        try:
            if self._chart_data is None:
                return
            
            self._stop_animation()
            
            # Figure'ı temizle ve yeni axes oluştur
            self.canvas.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            self._apply_chart_style(ax)
            self.canvas.figure.set_facecolor("#0c1324")
            
            y = self._chart_data["y"]
            labels = self._chart_data["labels"]
            colors = self._chart_data["colors"]
            ylabel = self._chart_data["ylabel"]
            title = self._chart_data["title"]
            
            self._current_chart_index = 0
            
            if self.chart_type == "line":
                x = list(range(len(y)))
                self._line_data = {"x": x, "y": y, "colors": colors}
                self._line_plot, = ax.plot([], [], color="#3ac7ff", linewidth=3, alpha=0.9, marker='o', markersize=8,
                                          markerfacecolor='white', markeredgecolor="#3ac7ff", markeredgewidth=2)
                self._line_scatter = ax.scatter([], [], c=[], s=120, zorder=4, edgecolors='white', linewidths=2.5, alpha=0.8)
                self._line_fill_poly = None
                ax.set_xticks(x)
                ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=10)
                y_max = max(y) if y else 0
                y_max = y_max * 1.2 if y_max > 0 else 1
                ax.set_ylim(0, y_max)
                ax.set_xlim(-0.5, len(x) - 0.5)
                ax.set_ylabel(ylabel, fontsize=12, color="#d8e4ff", fontweight='bold')
                ax.set_title(title, fontsize=13, color="#f4f7ff", pad=15, fontweight='bold')
                ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
                ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
                
                def animate_line(frame):
                    try:
                        total_frames = len(x) * 3
                        if frame >= total_frames:
                            return self._line_plot, self._line_scatter
                        progress = min(1.0, (frame + 1) / total_frames)
                        idx = max(1, int(progress * len(x)))
                        if idx > 0:
                            x_data = x[:idx]
                            y_data = y[:idx]
                            self._line_plot.set_data(x_data, y_data)
                            if len(x_data) > 0:
                                scatter_data = np.array(list(zip(x_data, y_data)))
                                self._line_scatter.set_offsets(scatter_data)
                                if len(colors[:idx]) > 0:
                                    # Renkleri normalize et
                                    try:
                                        color_array = np.linspace(0, 1, len(colors[:idx]))
                                        self._line_scatter.set_array(color_array)
                                        self._line_scatter.set_cmap(plt.cm.viridis)
                                    except:
                                        pass
                                # Fill area - önceki fill'i kaldır
                                if self._line_fill_poly is not None:
                                    try:
                                        for poly in self._line_fill_poly:
                                            poly.remove()
                                    except:
                                        pass
                                if len(x_data) > 1:
                                    self._line_fill_poly = ax.fill_between(x_data, 0, y_data, color="#3ac7ff", alpha=0.2)
                            # Eksenleri güncelle
                            ax.set_ylabel(ylabel, fontsize=12, color="#d8e4ff", fontweight='bold')
                            ax.set_title(title, fontsize=13, color="#f4f7ff", pad=15, fontweight='bold')
                            ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
                            ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
                        self.canvas.draw_idle()
                        return self._line_plot, self._line_scatter
                    except Exception as e:
                        # Hata olsa bile devam et
                        return self._line_plot, self._line_scatter
                
                self._animation = FuncAnimation(
                    self.canvas.figure, animate_line, frames=len(x) * 3, 
                    interval=self._animation_interval_ms, blit=False, repeat=False
                )
                # Figure arka plan rengini ayarla
                self.canvas.figure.set_facecolor("#0c1324")
            else:
                self._bar_data = {"y": y, "labels": labels, "colors": colors}
                self._bars = []
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, rotation=15, ha='right')
                y_max = max(y) if y else 0
                y_max = y_max * 1.15 if y_max > 0 else 1
                ax.set_ylim(0, y_max)
                ax.set_xlim(-0.5, len(labels) - 0.5)
                
                def animate_bar(frame):
                    try:
                        total_frames = len(labels) * 15
                        if frame >= total_frames:
                            return self._bars
                        
                        # Her çubuk için ayrı animasyon
                        ax.clear()
                        self._apply_chart_style(ax)
                        
                        bars = []
                        for i in range(len(labels)):
                            # Her çubuk için animasyon ilerlemesi
                            bar_start_frame = i * 12
                            bar_anim_frames = 20
                            if frame >= bar_start_frame:
                                anim_progress = min(1.0, (frame - bar_start_frame) / bar_anim_frames)
                                # Daha yumuşak easing function (ease-out cubic)
                                anim_progress = 1 - (1 - anim_progress) ** 2.5
                                target_height = y[i] * anim_progress
                                bar = ax.bar(i, target_height, color=colors[i], alpha=0.85 + 0.1 * anim_progress, 
                                            edgecolor='white', linewidth=2)
                                bars.extend(bar)
                                # Değer etiketi
                                if anim_progress > 0.8:
                                    ax.text(i, target_height, f'{y[i]:.4f}' if y[i] < 1 else f'{y[i]:.2f}',
                                           ha='center', va='bottom', fontsize=10, color='#f4f7ff', weight='bold')
                            else:
                                bar = ax.bar(i, 0, color=colors[i], alpha=0.0)
                                bars.extend(bar)
                        
                        ax.set_xticks(range(len(labels)))
                        ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=10)
                        y_max = max(y) if y else 0
                        y_max = y_max * 1.2 if y_max > 0 else 1
                        ax.set_ylim(0, y_max)
                        ax.set_xlim(-0.5, len(labels) - 0.5)
                        ax.set_ylabel(ylabel, fontsize=12, color="#d8e4ff", fontweight='bold')
                        ax.set_title(title, fontsize=13, color="#f4f7ff", pad=15, fontweight='bold')
                        ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
                        ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
                        self._bars = bars
                        self.canvas.draw_idle()
                        return self._bars
                    except Exception as e:
                        # Hata olsa bile devam et
                        return self._bars if hasattr(self, '_bars') else []
                
                self._animation = FuncAnimation(
                    self.canvas.figure, animate_bar, frames=len(labels) * 15, 
                    interval=self._animation_interval_ms, blit=False, repeat=False
                )
                # Figure arka plan rengini ayarla
                self.canvas.figure.set_facecolor("#0c1324")
            self.canvas.draw_idle()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Uyarı", f"Animasyon başlatılırken hata: {str(e)}")
            # Hata olsa bile statik grafiği göster
            try:
                if self._chart_data is not None:
                    self._render_static_chart()
            except:
                pass

    def _stop_animation(self) -> None:
        """Animasyonu durdur"""
        try:
            if self._animation is not None:
                if hasattr(self._animation, 'event_source') and self._animation.event_source is not None:
                    self._animation.event_source.stop()
                self._animation = None
        except Exception as e:
            # Hata olsa bile devam et
            self._animation = None


    def _render_static_chart(self) -> None:
        """Animasyon olmadan statik grafik göster"""
        if self._last_df is None or self._chart_data is None:
            return
        
        # Figure'ı temizle ve yeni axes oluştur
        self.canvas.figure.clear()
        ax = self.canvas.figure.add_subplot(111)
        self._apply_chart_style(ax)
        self.canvas.figure.set_facecolor("#0c1324")
        
        y = self._chart_data["y"]
        labels = self._chart_data["labels"]
        colors = self._chart_data["colors"]
        ylabel = self._chart_data["ylabel"]
        title = self._chart_data["title"]
        
        if self.chart_type == "line":
            x = list(range(len(y)))
            ax.plot(x, y, color="#3ac7ff", linewidth=3, marker='o', markersize=10, alpha=0.9, 
                   markerfacecolor='white', markeredgecolor="#3ac7ff", markeredgewidth=2)
            ax.scatter(x, y, c=colors, s=120, zorder=4, edgecolors='white', linewidths=2.5, alpha=0.8)
            ax.fill_between(x, 0, y, color="#3ac7ff", alpha=0.2)
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=10)
            # Y ekseni limiti
            y_max = max(y) if y else 0
            y_max = y_max * 1.2 if y_max > 0 else 1
            ax.set_ylim(0, y_max)
        else:
            bars = ax.bar(labels, y, color=colors, alpha=0.9, edgecolor='white', linewidth=2)
            # Değerleri çubukların üzerine yaz
            for i, (bar, val) in enumerate(zip(bars, y)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.4f}' if val < 1 else f'{val:.2f}',
                       ha='center', va='bottom', fontsize=10, color='#f4f7ff', weight='bold')
            ax.set_xticklabels(labels, rotation=20, ha='right', fontsize=10)
            # Y ekseni limiti
            y_max = max(y) if y else 0
            y_max = y_max * 1.2 if y_max > 0 else 1
            ax.set_ylim(0, y_max)
        
        ax.set_ylabel(ylabel, fontsize=12, color="#d8e4ff", fontweight='bold')
        ax.set_title(title, fontsize=13, color="#f4f7ff", pad=15, fontweight='bold')
        ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
        ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
        self.canvas.figure.set_facecolor("#0c1324")
        self.canvas.figure.tight_layout(pad=2.0)
        self.canvas.draw()

    def _on_metric_changed(self) -> None:
        """Metrik değiştiğinde grafiği yeniden çiz"""
        try:
            if self._last_df is not None:
                # Animasyonu durdur
                self._stop_animation()
                # Grafiği yeniden çiz (otomatik animasyon başlayacak)
                self._render_chart(self._last_df)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Uyarı", f"Metrik değiştirilirken hata: {str(e)}")
    
    def _toggle_detail_chart(self, checked: bool) -> None:
        """Detaylı karşılaştırma grafiğini göster/gizle"""
        try:
            metric = self.chart_metric_combo.currentText()
            memory_config = self._memory_metric_config(metric)
            title_prefix = f"{self.dataset_combo.currentText()} / n={self.size_spin.value()}"
            if checked:
                self.canvas2.show()
                self.detail_chart_toggle.setText(
                    "▲ İkinci Bellek Grafiğini Gizle" if memory_config else "▲ Detaylı Karşılaştırma Gizle"
                )
                # Eğer veri varsa grafiği yeniden çiz
                if self._last_df is not None:
                    self.canvas2.figure.clear()
                    ax2 = self.canvas2.figure.add_subplot(111)
                    self._apply_chart_style(ax2)
                    if memory_config:
                        sec_key, sec_title, sec_ylabel = memory_config[3], memory_config[4], memory_config[5]
                        self._render_memory_chart(ax2, self._last_df, sec_key, f"{title_prefix} - {sec_title}", sec_ylabel)
                    else:
                        self._render_comparison_chart(ax2, self._last_df)
                    self.canvas2.figure.set_facecolor("#0c1324")
                    self.canvas2.figure.tight_layout(pad=2.0)
                    self.canvas2.draw()
            else:
                self.canvas2.hide()
                self.detail_chart_toggle.setText(
                    "▼ İkinci Bellek Grafiğini Göster" if memory_config else "▼ Detaylı Karşılaştırma Göster"
                )
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Uyarı", f"Detaylı grafik gösterilirken hata: {str(e)}")

    def _on_progress(self, current: int, total: int, algo_key: str) -> None:
        self.status_label.setText(f"Çalıştırılıyor: {algo_key} ({current}/{total})")
        self.progress.setValue(current)

    def _on_worker_finished(self, df) -> None:
        self._render_table(df)
        self._render_chart(df)
        self._update_summary(df)
        self.status_label.setText("Tamamlandı.")
        self._finish_run_ui()
        self._fade_in(self._result_card)
        self._pulse_status()
        # Animasyon otomatik başlatılacak (_render_chart içinde)

    def _on_worker_canceled(self) -> None:
        self.status_label.setText("Durduruldu.")
        self._finish_run_ui()

    def _on_worker_error(self, message: str) -> None:
        self.status_label.setText("Hata oluştu.")
        QtWidgets.QMessageBox.critical(self, "Hata", message)
        self._finish_run_ui()

    def _finish_run_ui(self) -> None:
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._worker = None
        self._thread = None

    def _on_stop(self) -> None:
        if self._worker is not None:
            self._worker.stop()
            self.status_label.setText("Durduruluyor...")
            self.stop_btn.setEnabled(False)

    def _chart_colors(self, count: int) -> list[str]:
        palette = ["#3ac7ff", "#ffb347", "#7effa1", "#ff7a7a", "#b48bff", "#ffd166"]
        return [palette[i % len(palette)] for i in range(count)]

    def _memory_metric_config(self, metric: str) -> tuple[str, str, str, str, str, str] | None:
        if metric == "Bellek (Ek)":
            return (
                "memory_mb",
                "Ek Bellek (Peak Δ)",
                "Bellek Δ (MB)",
                "memory_peak_mb",
                "Toplam Bellek (Peak)",
                "Bellek Peak (MB)",
            )
        if metric == "Bellek (Toplam Peak)":
            return (
                "memory_peak_mb",
                "Toplam Bellek (Peak)",
                "Bellek Peak (MB)",
                "memory_mb",
                "Ek Bellek (Peak Δ)",
                "Bellek Δ (MB)",
            )
        return None

    def _memory_values(self, df, key: str) -> list[float]:
        if key not in df.columns:
            return [0.0] * len(df)
        values: list[float] = []
        for val in df[key]:
            if val is None:
                values.append(0.0)
            else:
                values.append(max(0.0, float(val)))
        return values

    def _render_memory_chart(self, ax, df, key: str, title: str, ylabel: str) -> None:
        labels = list(df["algorithm"])
        y = self._memory_values(df, key)
        colors = self._chart_colors(len(labels))
        x = np.arange(len(labels))
        ax.bar(x, y, color=colors, alpha=0.9, edgecolor="white", linewidth=1.8)
        y_max = max(y) if y else 0
        y_max = y_max * 1.2 if y_max > 0 else 1
        ax.set_ylim(0, y_max)
        ax.set_ylabel(ylabel, fontsize=12, color="#d8e4ff", fontweight="bold")
        ax.set_title(title, fontsize=13, color="#f4f7ff", pad=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=10)
        ax.grid(axis="y", alpha=0.25, linestyle="--", linewidth=1)
        ax.grid(axis="x", alpha=0.1, linestyle="--", linewidth=0.5)
        ax.set_facecolor("#0c1324")

    def _prime_canvas(self, canvas: FigureCanvasQTAgg) -> None:
        fig = canvas.figure
        fig.set_facecolor("#0c1324")
        fig.patch.set_facecolor("#0c1324")
        fig.clear()
        ax = fig.add_subplot(111)
        self._apply_chart_style(ax)
        ax.set_axis_off()
        fig.tight_layout(pad=2.0)
        canvas.setStyleSheet("background-color: #0c1324;")
        canvas.draw_idle()

    def _apply_chart_style(self, ax) -> None:
        # Figure arka plan rengi - her zaman koyu tema
        if hasattr(ax, 'figure'):
            ax.figure.patch.set_facecolor("#0c1324")
            ax.figure.set_facecolor("#0c1324")
        ax.patch.set_facecolor("#0c1324")
        ax.set_facecolor("#0c1324")
        ax.tick_params(axis="x", colors="#d8e4ff", labelsize=10)
        ax.tick_params(axis="y", colors="#d8e4ff", labelsize=10)
        ax.yaxis.label.set_color("#d8e4ff")
        ax.xaxis.label.set_color("#d8e4ff")
        ax.title.set_color("#f4f7ff")
        for spine in ax.spines.values():
            spine.set_color("#223156")
            spine.set_linewidth(1.5)

    def _toggle_table(self, checked: bool) -> None:
        self.table.setVisible(checked)
        self.table_toggle.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)

    def _set_chart_type(self, chart_type: str) -> None:
        try:
            self.chart_type = chart_type
            self.bar_btn.setChecked(chart_type == "bar")
            self.line_btn.setChecked(chart_type == "line")
            if self._last_df is not None:
                # Animasyonu durdur
                self._stop_animation()
                # Grafiği yeniden çiz (otomatik animasyon başlayacak)
                self._render_chart(self._last_df)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Uyarı", f"Grafik türü değiştirilirken hata: {str(e)}")
    
    def _cleanup_animation(self) -> None:
        """Widget kapatılırken animasyonu temizle"""
        self._stop_animation()

    def _reset_chart(self) -> None:
        try:
            self._stop_animation()
            self._last_df = None
            self._chart_data = None
            self.canvas.figure.clear()
            self.canvas2.figure.clear()
            ax = self.canvas.figure.add_subplot(111)
            self._apply_chart_style(ax)
            if self.canvas2.isVisible():
                ax2 = self.canvas2.figure.add_subplot(111)
                self._apply_chart_style(ax2)
            self.canvas.draw()
            if self.canvas2.isVisible():
                self.canvas2.draw()
            self._show_reset_hint()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Uyarı", f"Grafik sıfırlanırken hata: {str(e)}")

    def _show_reset_hint(self) -> None:
        self.reset_hint.setText("Grafik sıfırlandı")
        QtCore.QTimer.singleShot(5000, lambda: self.reset_hint.setText(""))

    def _update_algo_info(self, item: QtWidgets.QListWidgetItem | None) -> None:
        if item is None:
            self.algo_info_title.setText("")
            self.algo_info_desc.setText("")
            self.case_info_body.setText("")
            return
        data = {
            "quick": {
                "desc": "Böl ve fethet; pivot etrafında bölme. Pratikte hızlı, worst O(n^2).",
                "best": "Best: O(n log n) - random/partial veri seti, dengeli pivot.",
                "worst": "Worst: O(n^2) - reverse veya zaten sıralı veri (kötü pivot).",
            },
            "heap": {
                "desc": "Heap tabanlı; O(n log n) ve in-place.",
                "best": "Best: O(n log n) - veri setinden bağımsız.",
                "worst": "Worst: O(n log n) - veri setinden bağımsız.",
            },
            "shell": {
                "desc": "Aralıklı insertion; pratikte hızlı, teori aralığa bağlı.",
                "best": "Best: kısmen sıralı (partial) veri, pratikte hızlı.",
                "worst": "Worst: reverse veri, gap dizisine bağlı ~O(n^2).",
            },
            "merge": {
                "desc": "Stabil ve O(n log n); ek bellek O(n).",
                "best": "Best: O(n log n) - veri setinden bağımsız.",
                "worst": "Worst: O(n log n) - veri setinden bağımsız.",
            },
            "radix": {
                "desc": "Basamak bazlı; sayısal veride çok hızlı.",
                "best": "Best: O(d*(n+k)) - basamak sayısı küçükse hızlı.",
                "worst": "Worst: O(d*(n+k)) - basamak sayısı büyüdükçe artar.",
            },
        }
        key = item.data(QtCore.Qt.UserRole)
        info = data.get(key, {})
        self.algo_info_title.setText(item.text())
        self.algo_info_desc.setText(info.get("desc", ""))
        best = info.get("best", "")
        worst = info.get("worst", "")
        self.case_info_body.setText(f"{best}\n{worst}".strip())

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
