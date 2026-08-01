from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class VoicePage(QFrame):
    """
    Voice Recognition (MVP UI):
    - Start/Stop listening
    - Live partial text + final transcript box
    - Language switch (English/Hindi) (model-based)
    """

    start_listening_requested = Signal()
    stop_listening_requested = Signal()
    use_transcript_requested = Signal(str, bool)  # transcript, auto_send

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("VoicePage")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._listening = False

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("VoiceScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("VoiceContent")
        scroll.setWidget(content)

        root.addWidget(scroll)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header = QLabel("Voice")
        header.setObjectName("VoiceHeader")

        sub = QLabel(
            "Offline dictation (Vosk). Set VOSK_MODEL_PATH_EN / VOSK_MODEL_PATH_HI (recommended) "
            "or VOSK_MODEL_PATH (fallback)."
        )
        sub.setObjectName("VoiceSubHeader")
        sub.setWordWrap(True)

        layout.addWidget(header)
        layout.addWidget(sub)
        layout.addSpacing(6)

        layout.addWidget(self._make_dictation_card())
        layout.addWidget(self._make_activation_card())
        layout.addWidget(self._make_input_card())
        layout.addWidget(self._make_output_card())
        layout.addWidget(self._make_notes_card())

        layout.addStretch(1)

        self.set_listening(False)

    def selected_language_key(self) -> str:
        # "English" -> en, "Hindi" -> hi
        val = (self._lang_combo.currentData() or "en")
        return str(val)

    def _card(self, title: str, desc: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("VoiceCard")

        box = QVBoxLayout(frame)
        box.setContentsMargins(16, 14, 16, 14)
        box.setSpacing(10)

        t = QLabel(title)
        t.setObjectName("VoiceCardTitle")

        d = QLabel(desc)
        d.setObjectName("VoiceCardDesc")
        d.setWordWrap(True)

        box.addWidget(t)
        box.addWidget(d)

        return frame, box

    def _make_dictation_card(self) -> QFrame:
        frame, box = self._card(
            "Dictation",
            "Select language, press Start, speak, then Stop.",
        )

        top_row = QWidget()
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(10)

        self._status_pill = QLabel("Idle")
        self._status_pill.setObjectName("VoiceStatusPill")

        self._lang_combo = QComboBox()
        self._lang_combo.setObjectName("SettingsControl")
        self._lang_combo.addItem("English", "en")
        self._lang_combo.addItem("Hindi", "hi")
        self._lang_combo.setFixedWidth(140)

        self._auto_send = QCheckBox("Auto-send to chat")
        self._auto_send.setObjectName("SettingsCheck")
        self._auto_send.setChecked(False)

        self._start_btn = QPushButton("Start listening")
        self._start_btn.setCursor(Qt.PointingHandCursor)
        self._start_btn.clicked.connect(self.start_listening_requested.emit)

        self._stop_btn = QPushButton("Stop")
        self._stop_btn.setObjectName("VoiceStopButton")
        self._stop_btn.setCursor(Qt.PointingHandCursor)
        self._stop_btn.clicked.connect(self.stop_listening_requested.emit)

        top_row_layout.addWidget(self._status_pill, 0)
        top_row_layout.addWidget(self._lang_combo, 0)
        top_row_layout.addStretch(1)
        top_row_layout.addWidget(self._auto_send, 0)
        top_row_layout.addWidget(self._start_btn, 0)
        top_row_layout.addWidget(self._stop_btn, 0)

        self._partial_label = QLabel("")
        self._partial_label.setObjectName("VoicePartialText")
        self._partial_label.setWordWrap(True)

        self._transcript = QPlainTextEdit()
        self._transcript.setObjectName("VoiceTranscript")
        self._transcript.setReadOnly(True)
        self._transcript.setPlaceholderText("Transcript will appear here...")
        self._transcript.setMinimumHeight(130)

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        self._use_btn = QPushButton("Use in chat")
        self._use_btn.setObjectName("SettingsSecondaryButton")
        self._use_btn.setCursor(Qt.PointingHandCursor)
        self._use_btn.clicked.connect(self._emit_use_transcript)

        self._copy_btn = QPushButton("Copy")
        self._copy_btn.setObjectName("SettingsSecondaryButton")
        self._copy_btn.setCursor(Qt.PointingHandCursor)
        self._copy_btn.clicked.connect(self._copy_transcript)

        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setObjectName("SettingsSecondaryButton")
        self._clear_btn.setCursor(Qt.PointingHandCursor)
        self._clear_btn.clicked.connect(self.clear_transcript)

        actions_layout.addWidget(self._use_btn, 0)
        actions_layout.addWidget(self._copy_btn, 0)
        actions_layout.addWidget(self._clear_btn, 0)
        actions_layout.addStretch(1)

        box.addWidget(top_row)
        box.addWidget(self._partial_label)
        box.addWidget(self._transcript)
        box.addWidget(actions)

        return frame

    def _emit_use_transcript(self) -> None:
        text = self.transcript_text().strip()
        if not text:
            return
        self.use_transcript_requested.emit(text, self._auto_send.isChecked())

    def _copy_transcript(self) -> None:
        cb = QGuiApplication.clipboard()
        if cb is None:
            return
        text = self.transcript_text().strip()
        if text:
            cb.setText(text)

    def clear_transcript(self) -> None:
        self._partial_label.setText("")
        self._transcript.clear()

    def transcript_text(self) -> str:
        return self._transcript.toPlainText()

    # called by MainWindow
    def set_listening(self, listening: bool) -> None:
        self._listening = listening
        self._start_btn.setDisabled(listening)
        self._stop_btn.setDisabled(not listening)
        self._lang_combo.setDisabled(listening)  # avoid switching model mid-stream

        if listening:
            self._status_pill.setText("Listening")
        else:
            self._status_pill.setText("Idle")
            self._partial_label.setText("")

    # called by MainWindow
    def set_partial_text(self, text: str) -> None:
        if not self._listening:
            return
        self._partial_label.setText(text)

    # called by MainWindow
    def add_final_text(self, text: str) -> None:
        text = (text or "").strip()
        if not text:
            return

        current = self._transcript.toPlainText().strip()
        if current:
            self._transcript.setPlainText(current + "\n" + text)
        else:
            self._transcript.setPlainText(text)

        self._partial_label.setText("")

    # called by MainWindow
    def show_error(self, message: str) -> None:
        self.set_listening(False)
        self._status_pill.setText("Error")
        self._partial_label.setText("")
        self._transcript.setPlainText(message)

    # --- planned cards kept as-is ---

    def _make_activation_card(self) -> QFrame:
        frame, box = self._card(
            "Activation (Planned)",
            "Wake word and hotkey controls will be added later.",
        )

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        wake = QLineEdit()
        wake.setObjectName("SettingsControl")
        wake.setPlaceholderText("e.g., Nova")
        wake.setText("Nova")
        wake.setEnabled(False)

        hotkey_row = QWidget()
        hotkey_layout = QHBoxLayout(hotkey_row)
        hotkey_layout.setContentsMargins(0, 0, 0, 0)
        hotkey_layout.setSpacing(10)

        hotkey = QLineEdit()
        hotkey.setObjectName("SettingsControl")
        hotkey.setPlaceholderText("e.g., Ctrl+Shift+Space")
        hotkey.setText("Ctrl+Shift+Space")
        hotkey.setEnabled(False)

        set_hotkey = QPushButton("Set (Planned)")
        set_hotkey.setObjectName("SettingsSecondaryButton")
        set_hotkey.setCursor(Qt.PointingHandCursor)
        set_hotkey.setEnabled(False)

        hotkey_layout.addWidget(hotkey, 1)
        hotkey_layout.addWidget(set_hotkey, 0)

        form.addRow("Wake word", wake)
        form.addRow("Push-to-talk hotkey", hotkey_row)

        box.addLayout(form)
        return frame

    def _make_input_card(self) -> QFrame:
        frame, box = self._card(
            "Input (Planned)",
            "Microphone selection and input sensitivity will be added later.",
        )

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        mic = QComboBox()
        mic.setObjectName("SettingsControl")
        mic.addItems(["Default microphone (Planned)", "Device list (Planned)"])
        mic.setEnabled(False)

        sensitivity = QSlider(Qt.Horizontal)
        sensitivity.setObjectName("SettingsSlider")
        sensitivity.setMinimum(0)
        sensitivity.setMaximum(100)
        sensitivity.setValue(60)
        sensitivity.setEnabled(False)

        sens_row = QWidget()
        sens_layout = QHBoxLayout(sens_row)
        sens_layout.setContentsMargins(0, 0, 0, 0)
        sens_layout.setSpacing(10)

        sens_value = QLabel("0.60")
        sens_value.setObjectName("SettingsValue")

        def _sync(v: int) -> None:
            sens_value.setText(f"{v/100:.2f}")

        sensitivity.valueChanged.connect(_sync)

        sens_layout.addWidget(sensitivity, 1)
        sens_layout.addWidget(sens_value, 0)

        form.addRow("Microphone", mic)
        form.addRow("Sensitivity", sens_row)

        box.addLayout(form)
        return frame

    def _make_output_card(self) -> QFrame:
        frame, box = self._card(
            "Output (Planned)",
            "Text-to-speech controls will be added later.",
        )

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        voice = QComboBox()
        voice.setObjectName("SettingsControl")
        voice.addItems(["Default voice (Planned)", "Voice list (Planned)"])
        voice.setEnabled(False)

        rate = QSlider(Qt.Horizontal)
        rate.setObjectName("SettingsSlider")
        rate.setMinimum(50)
        rate.setMaximum(150)
        rate.setValue(100)
        rate.setEnabled(False)

        rate_row = QWidget()
        rate_layout = QHBoxLayout(rate_row)
        rate_layout.setContentsMargins(0, 0, 0, 0)
        rate_layout.setSpacing(10)

        rate_value = QLabel("1.00x")
        rate_value.setObjectName("SettingsValue")

        def _sync_rate(v: int) -> None:
            rate_value.setText(f"{v/100:.2f}x")

        rate.valueChanged.connect(_sync_rate)

        rate_layout.addWidget(rate, 1)
        rate_layout.addWidget(rate_value, 0)

        test_btn = QPushButton("Test voice (Planned)")
        test_btn.setObjectName("SettingsSecondaryButton")
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setEnabled(False)

        form.addRow("Voice", voice)
        form.addRow("Speech rate", rate_row)
        form.addRow("", test_btn)

        box.addLayout(form)
        return frame

    def _make_notes_card(self) -> QFrame:
        frame, box = self._card(
            "Setup",
            "Install deps + download BOTH models if you want English and Hindi.",
        )

        note = QLabel(
            "1) pip install vosk sounddevice\n\n"
            "2) Download models:\n"
            "   - English: vosk-model-small-en-us-0.15\n"
            "   - Hindi:   vosk-model-small-hi-0.22\n\n"
            "3) Set env vars (recommended):\n"
            "   - VOSK_MODEL_PATH_EN = <english model folder>\n"
            "   - VOSK_MODEL_PATH_HI = <hindi model folder>\n"
            "   (Fallback: VOSK_MODEL_PATH)\n\n"
            "4) Restart app and select language from dropdown."
        )
        note.setObjectName("VoiceNoteText")
        note.setWordWrap(True)
        box.addWidget(note)

        return frame