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
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Gradient background
        gradient = QtGui.QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QtGui.QColor("#0b1021"))
        gradient.setColorAt(1, QtGui.QColor("#050810"))
        painter.fillRect(self.rect(), gradient)
        
        if not self.data:
            painter.setPen(QtGui.QColor("#5b8def"))
            painter.setFont(QtGui.QFont("Arial", 14))
            painter.drawText(self.rect(), QtCore.Qt.AlignCenter, "Veri bekleniyor...")
            painter.end()
            return
        
        w = self.width()
        h = self.height()
        n = len(self.data)
        bar_width = max(2, (w - 20) // max(n, 1))
        spacing = 1
        max_val = max(self.data)
        scale = (h - 20) / max(1, max_val)
        
        # Sıralı olup olmadığını kontrol et (renk değişimi için)
        is_sorted = all(self.data[i] <= self.data[i+1] for i in range(len(self.data)-1))
        
        for idx, val in enumerate(self.data):
            bar_h = int(val * scale)
            x = 10 + idx * (bar_width + spacing)
            y = h - 10 - bar_h
            
            # Renk gradyanı - sıralı ise yeşil, değilse mavi tonları
            if is_sorted:
                color = QtGui.QColor("#7effa1")
            else:
                # Değere göre renk gradyanı
                intensity = val / max_val if max_val > 0 else 0
                r = int(91 + (255 - 91) * intensity)
                g = int(141 + (255 - 141) * intensity)
                b = int(239 + (255 - 239) * intensity)
                color = QtGui.QColor(r, g, b)
            
            # Çubuk çizimi - yuvarlatılmış köşeler için path kullan
            rect = QtCore.QRectF(x, y, bar_width - 1, bar_h)
            painter.setBrush(QtGui.QBrush(color))
            painter.setPen(QtGui.QPen(QtGui.QColor("#ffffff"), 0.5))
            painter.drawRoundedRect(rect, 2, 2)
        
        painter.end()


class LiveView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.steps: list[list[int]] = []
        self.step_idx = 0
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._advance)
        self._apply_theme()
        self._build_ui()

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
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7effa1, stop:1 #5bff8f);
                border: none;
                color: #0b1a0f;
                padding: 10px 14px;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #8effb1; transform: translateY(-1px); }
            QPushButton:pressed { background-color: #6eff9f; }
            QPushButton:disabled { background-color: #3a4a71; color: #cfd9ff; }
            QPushButton#stop-btn { 
                background-color: #ff5b5b; 
                color: #ffffff; 
            }
            QPushButton#stop-btn:hover { background-color: #ff7373; }
            QComboBox, QSpinBox, QSlider {
                background-color: #0f1527;
                color: #eef3ff;
                border: 1px solid #30426e;
                border-radius: 8px;
                padding: 6px;
            }
            QSlider::groove:horizontal {
                background: #0f1527;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #7effa1;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #8effb1;
            }
            QProgressBar {
                background-color: #0f1527;
                border: 1px solid #223156;
                border-radius: 6px;
                text-align: center;
                color: #cdd8f5;
                height: 12px;
            }
            QProgressBar::chunk { background-color: #7effa1; border-radius: 6px; }
            QLabel#title { font-size: 18px; font-weight: 700; color: #f4f7ff; }
            QLabel#subtitle { color: #a8b8de; font-size: 12px; }
            """
        )

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        
        # Header
        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Adım Adım Görselleştirme")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("Algoritmaların çalışma adımlarını canlı olarak izleyin.")
        subtitle.setObjectName("subtitle")
        text_box = QtWidgets.QVBoxLayout()
        text_box.addWidget(title)
        text_box.addWidget(subtitle)
        header.addLayout(text_box)
        header.addStretch()
        layout.addLayout(header)
        
        # Controls card
        controls_card = QtWidgets.QFrame()
        controls_card.setObjectName("card")
        controls = QtWidgets.QFormLayout(controls_card)
        controls.setContentsMargins(15, 15, 15, 15)
        controls.setSpacing(10)

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
        self.speed_slider.setToolTip("Kareler arası ms (düşük = hızlı)")

        btn_row = QtWidgets.QHBoxLayout()
        self.run_btn = QtWidgets.QPushButton("▶ Başlat")
        self.run_btn.clicked.connect(self._on_run)
        self.stop_btn = QtWidgets.QPushButton("⏸ Durdur")
        self.stop_btn.setObjectName("stop-btn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()

        controls.addRow("Algoritma:", self.algo_combo)
        controls.addRow("Veri seti:", self.dataset_combo)
        controls.addRow("Boyut:", self.size_spin)
        controls.addRow("Hız (ms):", self.speed_slider)
        controls.addRow("", QtWidgets.QWidget())
        btn_widget = QtWidgets.QWidget()
        btn_widget.setLayout(btn_row)
        controls.addRow("", btn_widget)

        layout.addWidget(controls_card)

        # Canvas with enhanced styling
        canvas_container = QtWidgets.QFrame()
        canvas_container.setObjectName("card")
        canvas_layout = QtWidgets.QVBoxLayout(canvas_container)
        canvas_layout.setContentsMargins(10, 10, 10, 10)
        self.canvas = ArrayCanvas()
        canvas_layout.addWidget(self.canvas)
        layout.addWidget(canvas_container, 1)

        # Progress and status
        self.progress = QtWidgets.QProgressBar()
        self.progress.setTextVisible(True)
        self.progress.setFormat("%p% - Adım %v / %m")
        layout.addWidget(self.progress)
        
        self.status = QtWidgets.QLabel("Hazır. Başlatmak için ayarları yapın ve 'Başlat' butonuna tıklayın.")
        self.status.setObjectName("subtitle")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

    def _on_run(self) -> None:
        algo_key = self.algo_combo.currentData()
        dataset = self.dataset_combo.currentText()
        size = self.size_spin.value()
        
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status.setText("Veri hazırlanıyor...")
        QtWidgets.QApplication.processEvents()

        data = data_gen.generate(dataset, size)
        self.canvas.set_data(data)
        self.status.setText("Algoritma çalışıyor ve adımlar kaydediliyor...")
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
        self.status.setText(f"▶ Oynatılıyor: {len(self.steps)} adım | Hız: {interval_ms}ms/adım")

    def _on_stop(self) -> None:
        self.timer.stop()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        if self.step_idx >= len(self.steps):
            self.status.setText("✓ Tamamlandı! Tekrar oynatmak için 'Başlat' butonuna tıklayın.")
        else:
            self.status.setText(f"⏸ Duraklatıldı. Adım {self.step_idx + 1}/{len(self.steps)}")

    def _advance(self) -> None:
        if not self.steps:
            self.timer.stop()
            self.status.setText("Gösterilecek adım yok.")
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            return
        if self.step_idx >= len(self.steps):
            self.timer.stop()
            self.status.setText("✓ Tamamlandı! Tüm adımlar gösterildi.")
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            return
        self.canvas.set_data(self.steps[self.step_idx])
        self.progress.setValue(self.step_idx)
        self.step_idx += 1
        # İlerleme durumunu güncelle
        if self.step_idx % max(1, len(self.steps) // 20) == 0:
            percent = int((self.step_idx / len(self.steps)) * 100)
            self.status.setText(f"▶ Oynatılıyor: {self.step_idx}/{len(self.steps)} adım ({percent}%)")
