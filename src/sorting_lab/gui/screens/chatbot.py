"""README-aware chatbot screen using OpenAI API."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from urllib import error, request

from PySide6 import QtCore, QtGui, QtWidgets


class ChatWorker(QtCore.QObject):
    finished = QtCore.Signal(str)
    error = QtCore.Signal(str)

    def __init__(self, api_key: str, model: str, messages: list[dict[str, str]], timeout_s: int = 60) -> None:
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.messages = messages
        self.timeout_s = timeout_s

    @QtCore.Slot()
    def run(self) -> None:
        try:
            payload = {
                "model": self.model,
                "messages": self.messages,
                "temperature": 0.2,
            }
            data = json.dumps(payload).encode("utf-8")
            req = request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=data,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "sorting-lab-chatbot",
                },
                method="POST",
            )
            with request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
            response = json.loads(body)
            if "error" in response:
                raise RuntimeError(response["error"].get("message", "Bilinmeyen API hatası."))
            message = response["choices"][0]["message"]["content"]
            self.finished.emit(message.strip())
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            self.error.emit(f"HTTP {exc.code}: {detail}")
        except error.URLError as exc:
            self.error.emit(f"Ağ hatası: {exc}")
        except Exception as exc:  # pragma: no cover - UI error handling
            self.error.emit(str(exc))


class ChatbotView(QtWidgets.QWidget):
    def __init__(self) -> None:
        super().__init__()
        self._thread: QtCore.QThread | None = None
        self._worker: ChatWorker | None = None
        self._history: list[dict[str, str]] = []
        self._max_history = 12
        self._readme_text = self._load_readme()
        self._system_message = self._build_system_message(self._readme_text)
        self._apply_theme()
        self._build_ui()
        self._refresh_status()
        self._append_system("README yüklendi. Sorularınızı yazabilirsiniz.")

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
            QFrame#info-bar {
                background-color: #0f1a33;
                border-left: 4px solid #7effa1;
                border-radius: 8px;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #0f1527;
                color: #eef3ff;
                border: 1px solid #30426e;
                border-radius: 10px;
                padding: 8px;
            }
            QTextEdit[chatSize="SMALL"], QPlainTextEdit[chatSize="SMALL"] { font-size: 16px; }
            QTextEdit[chatSize="MEDIUM"], QPlainTextEdit[chatSize="MEDIUM"] { font-size: 18px; }
            QTextEdit[chatSize="LARGE"], QPlainTextEdit[chatSize="LARGE"] { font-size: 20px; }
            QTextEdit[chatSize="X LARGE"], QPlainTextEdit[chatSize="X LARGE"] { font-size: 22px; }
            QComboBox {
                background-color: #0f1527;
                color: #eef3ff;
                border: 1px solid #30426e;
                border-radius: 8px;
                padding: 4px 6px;
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
            QPushButton#secondary {
                background-color: #1a2440;
                color: #c7d6ff;
            }
            QLabel#title { font-size: 18px; font-weight: 700; color: #f4f7ff; }
            QLabel#subtitle { color: #a8b8de; font-size: 12px; }
            QLabel#chip { background: #0f1a33; border-radius: 8px; padding: 4px 8px; }
            """
        )

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Chatbot")
        title.setObjectName("title")
        subtitle = QtWidgets.QLabel("AI tabanlı yardımcı asistan ile uygulama hakkında soru sorun.")
        subtitle.setObjectName("subtitle")
        title_box = QtWidgets.QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        header.addLayout(title_box)
        header.addStretch()
        size_wrap = QtWidgets.QWidget()
        size_layout = QtWidgets.QHBoxLayout(size_wrap)
        size_layout.setContentsMargins(0, 0, 0, 0)
        size_layout.setSpacing(6)
        size_label = QtWidgets.QLabel("Metin Boyutu")
        size_label.setObjectName("subtitle")
        self.size_combo = QtWidgets.QComboBox()
        self.size_combo.addItems(["SMALL", "MEDIUM", "LARGE", "X LARGE"])
        self.size_combo.setCurrentText("LARGE")
        self.size_combo.setMinimumWidth(120)
        self.size_combo.currentTextChanged.connect(self._on_size_changed)
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_combo)
        header.addWidget(size_wrap)
        layout.addLayout(header)

        self.info_bar = QtWidgets.QFrame()
        self.info_bar.setObjectName("info-bar")
        info_layout = QtWidgets.QHBoxLayout(self.info_bar)
        info_layout.setContentsMargins(10, 8, 10, 8)
        self.api_status = QtWidgets.QLabel("")
        self.api_status.setObjectName("subtitle")
        self.model_status = QtWidgets.QLabel("")
        self.model_status.setObjectName("subtitle")
        self.readme_status = QtWidgets.QLabel("")
        self.readme_status.setObjectName("subtitle")
        info_layout.addWidget(self.api_status)
        info_layout.addStretch()
        info_layout.addWidget(self.model_status)
        info_layout.addStretch()
        info_layout.addWidget(self.readme_status)
        layout.addWidget(self.info_bar)

        chat_card = QtWidgets.QFrame()
        chat_card.setObjectName("card")
        chat_layout = QtWidgets.QVBoxLayout(chat_card)
        chat_layout.setContentsMargins(12, 12, 12, 12)
        chat_layout.setSpacing(10)

        self.chat_log = QtWidgets.QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setMinimumHeight(320)
        chat_layout.addWidget(self.chat_log, 1)

        input_row = QtWidgets.QHBoxLayout()
        self.input_box = QtWidgets.QPlainTextEdit()
        self.input_box.setPlaceholderText("Sorunuzu yazın... (örn: Quick Sort'un worst case'i nedir?)")
        self.input_box.setFixedHeight(90)
        self.input_box.installEventFilter(self)
        input_row.addWidget(self.input_box, 1)

        button_col = QtWidgets.QVBoxLayout()
        self.send_btn = QtWidgets.QPushButton("Gönder")
        self.send_btn.clicked.connect(self._on_send)
        self.clear_btn = QtWidgets.QPushButton("Temizle")
        self.clear_btn.setObjectName("secondary")
        self.clear_btn.clicked.connect(self._clear_chat)
        self.reload_btn = QtWidgets.QPushButton("README Yenile")
        self.reload_btn.setObjectName("secondary")
        self.reload_btn.clicked.connect(self._reload_readme)
        button_col.addWidget(self.send_btn)
        button_col.addWidget(self.clear_btn)
        button_col.addWidget(self.reload_btn)
        button_col.addStretch()
        input_row.addLayout(button_col)
        chat_layout.addLayout(input_row)

        layout.addWidget(chat_card, 1)

        self.footer_status = QtWidgets.QLabel("Hazır.")
        self.footer_status.setObjectName("subtitle")
        layout.addWidget(self.footer_status)
        self._apply_chat_size("MEDIUM")

    def _load_readme(self) -> str:
        try:
            root = Path(__file__).resolve().parents[4]
            readme_path = root / "README.md"
            text = readme_path.read_text(encoding="utf-8")
            max_chars = 14000
            if len(text) > max_chars:
                return text[:max_chars] + "\n\n[README kısaltıldı: içerik sınırı aşıldı]"
            return text
        except Exception:
            return "README yüklenemedi."

    def _build_system_message(self, readme_text: str) -> dict[str, str]:
        content = (
            "Sen Sorting Lab uygulamasının yardım asistanısın. "
            "Sadece README içeriğine dayanarak yanıt ver; bilmediğin konularda dürüstçe belirt. "
            "Kullanıcıya kısa ve net, adım adım yönergeler ver.\n\n"
            "README:\n"
            f"{readme_text}"
        )
        return {"role": "system", "content": content}

    def _refresh_status(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        readme_state = "README: yüklü" if self._readme_text else "README: bulunamadı"
        self.api_status.setText("API: hazır" if api_key else "API: anahtar yok")
        self.model_status.setText(f"Model: {model}")
        self.readme_status.setText(readme_state)

    def _append_html(self, html_text: str) -> None:
        self.chat_log.append(html_text)
        self.chat_log.moveCursor(QtGui.QTextCursor.End)

    def _append_user(self, message: str) -> None:
        safe = html.escape(message)
        self._append_html(
            f"<div style='margin-bottom:8px;'><span style='color:#7effa1; font-weight:600;'>Sen:</span> {safe}</div>"
        )

    def _append_assistant(self, message: str) -> None:
        safe = html.escape(message).replace("\n", "<br>")
        self._append_html(
            f"<div style='margin-bottom:10px;'><span style='color:#3ac7ff; font-weight:600;'>Asistan:</span> {safe}</div>"
        )

    def _append_system(self, message: str) -> None:
        safe = html.escape(message)
        self._append_html(
            f"<div style='margin-bottom:8px; color:#a8b8de;'><em>{safe}</em></div>"
        )

    def _on_send(self) -> None:
        text = self.input_box.toPlainText().strip()
        if not text:
            return
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            self._append_system("OpenAI API anahtarı bulunamadı. README'deki kurulum adımlarını takip edin.")
            self._refresh_status()
            return

        self._append_user(text)
        self.input_box.clear()
        self._history.append({"role": "user", "content": text})
        self._trim_history()
        self._start_request(api_key)

    def _trim_history(self) -> None:
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history :]

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:  # type: ignore[override]
        if obj is self.input_box and event.type() == QtCore.QEvent.KeyPress:
            key_event = QtGui.QKeyEvent(event)
            if key_event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                if key_event.modifiers() & QtCore.Qt.ShiftModifier:
                    return False
                if self.send_btn.isEnabled():
                    self._on_send()
                return True
        return super().eventFilter(obj, event)

    def _apply_chat_size(self, size: str) -> None:
        for widget in (self.chat_log, self.input_box):
            widget.setProperty("chatSize", size)
            widget.style().unpolish(widget)
            widget.style().polish(widget)
            widget.update()

    def _on_size_changed(self, size: str) -> None:
        self._apply_chat_size(size)

    def _start_request(self, api_key: str) -> None:
        if self._thread is not None and self._thread.isRunning():
            return
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
        messages = [self._system_message] + self._history
        self.send_btn.setEnabled(False)
        self.input_box.setEnabled(False)
        self.footer_status.setText("Yanıt hazırlanıyor...")
        QtWidgets.QApplication.processEvents()

        self._worker = ChatWorker(api_key, model, messages)
        self._thread = QtCore.QThread(self)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_response)
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)
        self._thread.finished.connect(self._cleanup_worker)
        self._thread.start()

    def _on_response(self, message: str) -> None:
        self._append_assistant(message)
        self._history.append({"role": "assistant", "content": message})
        self._trim_history()
        self.footer_status.setText("Hazır.")

    def _on_error(self, message: str) -> None:
        self._append_system(f"Hata: {message}")
        self.footer_status.setText("Hata oluştu.")

    def _cleanup_worker(self) -> None:
        if self._worker is not None:
            self._worker.deleteLater()
        if self._thread is not None:
            self._thread.deleteLater()
        self._worker = None
        self._thread = None
        self.send_btn.setEnabled(True)
        self.input_box.setEnabled(True)

    def _clear_chat(self) -> None:
        self._history = []
        self.chat_log.clear()
        self._append_system("Sohbet temizlendi.")

    def _reload_readme(self) -> None:
        self._readme_text = self._load_readme()
        self._system_message = self._build_system_message(self._readme_text)
        self._refresh_status()
        self._append_system("README güncellendi.")
