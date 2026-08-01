from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class SettingsPage(QFrame):
    """
    Phase 6 — Settings (UI skeleton only)
    No backend/config logic here. Pure UI placeholders.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setObjectName("SettingsPage")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("SettingsScroll")
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        content.setObjectName("SettingsContent")

        scroll.setWidget(content)
        root.addWidget(scroll)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        header = QLabel("Settings")
        header.setObjectName("SettingsHeader")

        sub = QLabel("Configure NOVA AI (UI only for now).")
        sub.setObjectName("SettingsSubHeader")

        layout.addWidget(header)
        layout.addWidget(sub)
        layout.addSpacing(6)

        layout.addWidget(self._make_appearance_card())
        layout.addWidget(self._make_ai_card())
        layout.addWidget(self._make_voice_card())
        layout.addWidget(self._make_privacy_card())
        layout.addWidget(self._make_about_card())

        layout.addStretch(1)

    def _card(self, title: str, desc: str) -> tuple[QFrame, QVBoxLayout]:
        frame = QFrame()
        frame.setObjectName("SettingsCard")

        box = QVBoxLayout(frame)
        box.setContentsMargins(16, 14, 16, 14)
        box.setSpacing(10)

        t = QLabel(title)
        t.setObjectName("SettingsCardTitle")

        d = QLabel(desc)
        d.setObjectName("SettingsCardDesc")
        d.setWordWrap(True)

        box.addWidget(t)
        box.addWidget(d)

        return frame, box

    def _make_appearance_card(self) -> QFrame:
        frame, box = self._card(
            "Appearance",
            "Theme and UI preferences.",
        )

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        theme = QComboBox()
        theme.setObjectName("SettingsControl")
        theme.addItems(["Dark", "Light", "System (Planned)"])
        theme.setCurrentText("Dark")

        compact = QCheckBox("Compact spacing (Planned)")
        compact.setObjectName("SettingsCheck")
        compact.setChecked(False)
        compact.setEnabled(False)

        animations = QCheckBox("Enable animations")
        animations.setObjectName("SettingsCheck")
        animations.setChecked(True)

        form.addRow("Theme", theme)
        form.addRow("", compact)
        form.addRow("", animations)

        box.addLayout(form)
        return frame

    def _make_ai_card(self) -> QFrame:
        frame, box = self._card(
            "AI",
            "Model and response behavior (placeholders).",
        )

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        model = QComboBox()
        model.setObjectName("SettingsControl")
        model.addItems(["Gemini (Current)", "Other providers (Planned)"])
        model.setCurrentIndex(0)
        model.setEnabled(False)

        temperature = QSlider(Qt.Horizontal)
        temperature.setObjectName("SettingsSlider")
        temperature.setMinimum(0)
        temperature.setMaximum(100)
        temperature.setValue(40)

        temp_row = QWidget()
        temp_layout = QHBoxLayout(temp_row)
        temp_layout.setContentsMargins(0, 0, 0, 0)
        temp_layout.setSpacing(10)

        temp_value = QLabel("0.4")
        temp_value.setObjectName("SettingsValue")

        def _sync_temp(v: int) -> None:
            temp_value.setText(f"{v/100:.2f}")

        temperature.valueChanged.connect(_sync_temp)

        temp_layout.addWidget(temperature, 1)
        temp_layout.addWidget(temp_value, 0)

        form.addRow("Model", model)
        form.addRow("Temperature", temp_row)

        box.addLayout(form)
        return frame

    def _make_voice_card(self) -> QFrame:
        frame, box = self._card(
            "Voice",
            "Voice system settings (planned).",
        )

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        enable_voice = QCheckBox("Enable voice features (Planned)")
        enable_voice.setObjectName("SettingsCheck")
        enable_voice.setEnabled(False)

        wake_word = QLineEdit()
        wake_word.setObjectName("SettingsControl")
        wake_word.setPlaceholderText("e.g., Nova")
        wake_word.setText("Nova")
        wake_word.setEnabled(False)

        form.addRow("", enable_voice)
        form.addRow("Wake word", wake_word)

        box.addLayout(form)
        return frame

    def _make_privacy_card(self) -> QFrame:
        frame, box = self._card(
            "Privacy & Memory",
            "Control data retention and memory behavior (planned).",
        )

        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)

        persistent_memory = QCheckBox("Enable persistent memory (Planned)")
        persistent_memory.setObjectName("SettingsCheck")
        persistent_memory.setEnabled(False)

        clear_runtime = QPushButton("Clear runtime memory (Planned)")
        clear_runtime.setObjectName("SettingsSecondaryButton")
        clear_runtime.setEnabled(False)
        clear_runtime.setCursor(Qt.PointingHandCursor)

        form.addRow("", persistent_memory)
        form.addRow("", clear_runtime)

        box.addLayout(form)
        return frame

    def _make_about_card(self) -> QFrame:
        frame, box = self._card(
            "About",
            "Build information.",
        )

        info = QLabel("NOVA AI — Desktop (Windows) • UI in active development")
        info.setObjectName("SettingsAboutText")
        info.setWordWrap(True)

        box.addWidget(info)
        return frame