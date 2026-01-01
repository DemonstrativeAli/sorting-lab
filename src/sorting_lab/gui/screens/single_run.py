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
        self.layout().setContentsMargins(10, 10, 10, 10)
        self.layout().setSpacing(12)
        self._build_header()
        self._build_body()
        self._build_footer()
        self.layout().addStretch(1)
        QtCore.QTimer.singleShot(0, self._sync_card_heights)

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
            QFrame#chip {
                background-color: #0c1324;
                border: 1px solid #2a3c63;
                border-radius: 10px;
            }
            QFrame#info-bar {
                background-color: #0f1a33;
                border-left: 4px solid #37c6f4;
                border-radius: 8px;
            }
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2f70ff, stop:1 #3ac7ff);
                border: none;
                color: white;
                padding: 10px 14px;
                border-radius: 8px;
                font-weight: 600;
                transition: all 120ms ease-in-out;
            }
            QPushButton:hover { background-color: #4a86ff; transform: translateY(-1px); }
            QPushButton:pressed { background-color: #2f70ff; }
            QPushButton:disabled { background-color: #3a4a71; color: #cfd9ff; }
            QComboBox, QSpinBox, QTextEdit, QListView {
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
            QProgressBar::chunk { background-color: #3ac7ff; border-radius: 6px; }
            QLabel#title { font-size: 18px; font-weight: 700; color: #f4f7ff; }
            QLabel#subtitle { color: #a8b8de; font-size: 12px; }
            QLabel#section-title { font-size: 13px; font-weight: 700; color: #d7e3ff; }
            QLabel#chip-value { font-size: 12px; font-weight: 700; color: #f5f8ff; }
            QLabel#chip-label { font-size: 9px; color: #9fb2d9; }
            QLabel#status-pill {
                background-color: #1a2440;
                color: #d7e3ff;
                padding: 2px 8px;
                border-radius: 10px;
                font-size: 10px;
                min-width: 78px;
                text-align: center;
            }
            QLabel#status-pill[state="running"] { background-color: #ffb347; color: #1a1a1a; }
            QLabel#status-pill[state="done"] { background-color: #7effa1; color: #0b1a0f; }
            QLabel#status-pill[state="ready"] { background-color: #2a3c63; color: #d7e3ff; }
            QLabel#status-pill[state="error"] { background-color: #ff5b5b; color: #ffffff; }
            QHeaderView::section { background-color: #0f1629; color: #d8e4ff; border: none; padding: 4px; }
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
        body_container = QtWidgets.QWidget()
        body_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        body = QtWidgets.QHBoxLayout(body_container)
        body.setSpacing(12)
        self._form_card = self._build_form_card()
        self._result_card = self._build_result_card()
        body.addWidget(self._form_card, 1, QtCore.Qt.AlignTop)
        body.addWidget(self._result_card, 2, QtCore.Qt.AlignTop)
        self.layout().addWidget(body_container)

    def _build_form_card(self) -> QtWidgets.QFrame:
        card = self._card()
        form = QtWidgets.QFormLayout(card)
        form.setVerticalSpacing(10)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self.algo_combo = QtWidgets.QComboBox()
        for algo in algorithms.available_algorithms():
            self.algo_combo.addItem(algo.name, algo.key)
        self.algo_combo.setMinimumWidth(220)
        self.algo_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        view = QtWidgets.QListView()
        view.setMinimumWidth(260)
        self.algo_combo.setView(view)
        self.algo_combo.setMinimumContentsLength(16)
        self.algo_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
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
        self.algo_info_time = QtWidgets.QLabel("")
        self.algo_info_time.setWordWrap(True)
        self.algo_info_time.setObjectName("subtitle")
        self.algo_info_space = QtWidgets.QLabel("")
        self.algo_info_space.setWordWrap(True)
        self.algo_info_space.setObjectName("subtitle")
        self.algo_info_use = QtWidgets.QLabel("")
        self.algo_info_use.setWordWrap(True)
        self.algo_info_use.setObjectName("subtitle")
        self.algo_info_note = QtWidgets.QLabel("")
        self.algo_info_note.setWordWrap(True)
        self.algo_info_note.setObjectName("subtitle")
        info_layout.addWidget(self.algo_info_title)
        info_layout.addWidget(self.algo_info_desc)
        info_layout.addWidget(self.algo_info_time)
        info_layout.addWidget(self.algo_info_space)
        info_layout.addWidget(self.algo_info_use)
        info_layout.addWidget(self.algo_info_note)
        self._update_algo_info()

        form.addRow(self._section_header("Ayarlar"))
        form.addRow("Algoritma:", self.algo_combo)
        form.addRow("", self.algo_info_card)
        form.addRow("Veri seti:", self.dataset_combo)
        form.addRow("Boyut:", self.size_spin)
        form.addRow("", self.run_btn)
        form.addRow("", self.progress)
        return card

    def _build_result_card(self) -> QtWidgets.QFrame:
        card = self._card()
        v = QtWidgets.QVBoxLayout(card)
        v.setContentsMargins(10, 8, 10, 10)
        v.setSpacing(6)
        header = QtWidgets.QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(10)
        title = QtWidgets.QLabel("Sonuçlar")
        title.setObjectName("title")
        self.status_label = QtWidgets.QLabel("Hazır")
        self.status_label.setObjectName("status-pill")
        self.status_label.setProperty("state", "ready")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.status_label)
        v.addLayout(header)

        chip_row = QtWidgets.QHBoxLayout()
        chip_row.setSpacing(8)
        self.dataset_value = self._stat_chip("Dataset", "-")
        self.size_value = self._stat_chip("Boyut", "-")
        self.runtime_value = self._stat_chip("Süre", "-")
        self.memory_value = self._stat_chip("Bellek Δ", "-")
        chip_row.addWidget(self.dataset_value["frame"])
        chip_row.addWidget(self.size_value["frame"])
        chip_row.addWidget(self.runtime_value["frame"])
        chip_row.addWidget(self.memory_value["frame"])
        chip_row.setStretch(0, 1)
        chip_row.setStretch(1, 1)
        chip_row.setStretch(2, 1)
        chip_row.setStretch(3, 1)

        chips_container = QtWidgets.QWidget()
        chips_container.setLayout(chip_row)
        chips_container.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        chips_container.setMaximumHeight(64)
        v.addWidget(chips_container)
        self._chip_value_labels = [
            self.dataset_value["value"],
            self.size_value["value"],
            self.runtime_value["value"],
            self.memory_value["value"],
        ]
        self._chip_text_labels = [
            self.dataset_value["label"],
            self.size_value["label"],
            self.runtime_value["label"],
            self.memory_value["label"],
        ]
        self._apply_responsive_fonts()

        self.preview_table = QtWidgets.QTableWidget(20, 2)
        self.preview_table.setHorizontalHeaderLabels(["Giriş (rastgele/partial/reverse)", "Sıralı (algoritma çıktısı)"])
        self.preview_table.verticalHeader().setVisible(True)
        self.preview_table.verticalHeader().setDefaultSectionSize(20)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.preview_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.preview_table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.preview_table.setMaximumHeight(220)
        v.addWidget(self.preview_table)
        self.preview_help = QtWidgets.QLabel(
            "Giriş sütunu üretilen veri setinin ilk 20 elemanını gösterir. Sıralı sütunu, seçilen algoritmanın çıktısıdır."
        )
        self.preview_help.setWordWrap(True)
        self.preview_help.setObjectName("subtitle")
        v.addWidget(self.preview_help)

        self._result_card = card
        return card

    def _card(self) -> QtWidgets.QFrame:
        card = QtWidgets.QFrame()
        card.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
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
        self._set_status("Çalıştırılıyor", "running")
        QtWidgets.QApplication.processEvents()

        base_data = data_gen.generate(dataset, size)

        result = metrics.measure(lambda: algorithms.run_algorithm(algo_key, base_data)[0])

        sorted_arr = result.output
        self._render_preview(base_data, sorted_arr)
        self.dataset_value["value"].setText(dataset)
        self.size_value["value"].setText(f"{size:,}")
        self.runtime_value["value"].setText(f"{result.duration:.4f} s")
        if result.memory_mb is not None:
            self.memory_value["value"].setText(f"{result.memory_mb:.3f} MB")
        else:
            self.memory_value["value"].setText("ölçülmedi")
        self._set_status("Tamamlandı", "done")
        self.progress.setRange(0, 1)
        self.progress.setValue(1)
        self.progress.hide()
        self.run_btn.setEnabled(True)
        self._fade_in(self._result_card)
        self._pulse_status()
        self._animate_chips()

    def _render_preview(self, before: list[int], after: list[int]) -> None:
        max_rows = self.preview_table.rowCount()
        for row in range(max_rows):
            b_val = str(before[row]) if row < len(before) else ""
            a_val = str(after[row]) if row < len(after) else ""
            self.preview_table.setItem(row, 0, QtWidgets.QTableWidgetItem(b_val))
            self.preview_table.setItem(row, 1, QtWidgets.QTableWidgetItem(a_val))
        self.preview_table.resizeColumnsToContents()

    def _build_footer(self) -> None:
        info_bar = QtWidgets.QFrame()
        info_bar.setObjectName("info-bar")
        layout = QtWidgets.QHBoxLayout(info_bar)
        layout.setContentsMargins(10, 8, 10, 8)
        label = QtWidgets.QLabel(
            "Önizleme: Bu tablo, girişteki üretilen sayıları ve sıralama sonrası çıkan sonuçları hızlı doğrulama için gösterir."
        )
        label.setWordWrap(True)
        label.setObjectName("subtitle")
        layout.addWidget(label)
        self.layout().addWidget(info_bar)

    def _update_algo_info(self) -> None:
        data = {
            "quick": {
                "title": "Quick Sort",
                "desc": "Böl ve fethet yaklaşımı; pivot etrafında bölme yapar, pratikte çok hızlıdır.",
                "time": "Zaman: Best/Avg O(n log n), Worst O(n^2).",
                "space": "Bellek: O(log n) özyineleme, in-place, stabil değil.",
                "use": "Kullanım: Ortalama performansı güçlü; rastgele veri setlerinde iyi sonuç verir.",
                "note": "Not: Kötü pivot seçimi worst-case süresini artırır.",
            },
            "heap": {
                "title": "Heap Sort",
                "desc": "Max-heap kurar ve kökü sona atarak sıralar.",
                "time": "Zaman: Best/Avg/Worst O(n log n).",
                "space": "Bellek: O(1), in-place, stabil değil.",
                "use": "Kullanım: Kötü senaryo garantisi isterken tercih edilir.",
                "note": "Not: Cache performansı Quick/Merge'e göre zayıf olabilir.",
            },
            "shell": {
                "title": "Shell Sort",
                "desc": "Aralıklı insertion ile kademeli sıralama yapar.",
                "time": "Zaman: Aralık dizisine bağlı; pratikte hızlı.",
                "space": "Bellek: O(1), in-place, stabil değil.",
                "use": "Kullanım: Orta boyutlu dizilerde düşük ek bellekle hızlı.",
                "note": "Not: Teorik üst sınırlar gap seçimine bağlıdır.",
            },
            "merge": {
                "title": "Merge Sort",
                "desc": "Diziyi bölüp birleştirerek sıralar (divide & conquer).",
                "time": "Zaman: Best/Avg/Worst O(n log n).",
                "space": "Bellek: O(n), stabil, in-place değil.",
                "use": "Kullanım: Stabil sıralama isteyenlerde veya büyük n için güvenli.",
                "note": "Not: Ek bellek gereksinimi vardır.",
            },
            "radix": {
                "title": "Radix Sort",
                "desc": "Basamaklara göre sıralar; sayısal veride çok hızlıdır.",
                "time": "Zaman: O(d * (n + k)).",
                "space": "Bellek: O(n + k), stabil, in-place değil.",
                "use": "Kullanım: Büyük sayısal veri setlerinde çok etkilidir.",
                "note": "Not: Negatif sayı desteği yoktur.",
            },
        }
        key = self.algo_combo.currentData()
        info = data.get(key, {})
        self.algo_info_title.setText(info.get("title", ""))
        self.algo_info_desc.setText(info.get("desc", ""))
        self.algo_info_time.setText(info.get("time", ""))
        self.algo_info_space.setText(info.get("space", ""))
        self.algo_info_use.setText(info.get("use", ""))
        self.algo_info_note.setText(info.get("note", ""))
        self._sync_card_heights()

    def _stat_chip(self, label: str, value: str) -> dict[str, QtWidgets.QWidget]:
        frame = QtWidgets.QFrame()
        frame.setObjectName("chip")
        layout = QtWidgets.QVBoxLayout(frame)
        layout.setContentsMargins(6, 4, 6, 4)
        value_label = QtWidgets.QLabel(value)
        value_label.setObjectName("chip-value")
        label_label = QtWidgets.QLabel(label)
        label_label.setObjectName("chip-label")
        layout.addWidget(value_label)
        layout.addWidget(label_label)
        frame.setMinimumWidth(120)
        frame.setMaximumHeight(60)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        return {"frame": frame, "value": value_label, "label": label_label}

    def _section_header(self, title: str) -> QtWidgets.QWidget:
        wrapper = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        label = QtWidgets.QLabel(title)
        label.setObjectName("section-title")
        line = QtWidgets.QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet(
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #37c6f4, stop:1 #2f70ff);"
        )
        layout.addWidget(label)
        layout.addWidget(line, 1)
        return wrapper

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

    def _set_status(self, text: str, state: str) -> None:
        self.status_label.setText(text)
        self.status_label.setProperty("state", state)
        self.status_label.style().polish(self.status_label)

    def _sync_card_heights(self) -> None:
        if not hasattr(self, "_form_card") or not hasattr(self, "_result_card"):
            return
        max_h = max(self._form_card.sizeHint().height(), self._result_card.sizeHint().height())
        if max_h > 0:
            self._form_card.setFixedHeight(max_h)
            self._result_card.setFixedHeight(max_h)

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        self._apply_responsive_fonts()

    def _apply_responsive_fonts(self) -> None:
        if not hasattr(self, "_chip_value_labels"):
            return
        scale = max(0.75, min(1.0, self.width() / 1400))
        value_size = int(12 * scale)
        label_size = int(9 * scale)
        for label in self._chip_value_labels:
            font = label.font()
            font.setPointSize(value_size)
            label.setFont(font)
        for label in self._chip_text_labels:
            font = label.font()
            font.setPointSize(label_size)
            label.setFont(font)
    
    def _animate_chips(self) -> None:
        """Chip'leri sırayla animasyonlu göster"""
        chips = [
            self.dataset_value["frame"],
            self.size_value["frame"],
            self.runtime_value["frame"],
            self.memory_value["frame"]
        ]
        for i, chip in enumerate(chips):
            effect = QtWidgets.QGraphicsOpacityEffect()
            chip.setGraphicsEffect(effect)
            anim = QtCore.QPropertyAnimation(effect, b"opacity", chip)
            anim.setDuration(300)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QtCore.QEasingCurve.OutCubic)
            QtCore.QTimer.singleShot(i * 100, lambda a=anim: a.start(QtCore.QAbstractAnimation.DeleteWhenStopped))
