"""LLM Settings dialog for Automatr.

Simple GUI for live-tuning llama.cpp generation parameters.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from automatr.core.config import get_config_manager, LLMConfig


# Default values (must match LLMConfig dataclass defaults)
DEFAULTS = {
    "temperature": 0.7,
    "max_tokens": 512,
    "top_p": 1.0,
    "top_k": 40,
    "repeat_penalty": 1.1,
}


class LLMSettingsDialog(QDialog):
    """Dialog for editing LLM generation settings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LLM Settings")
        self.setMinimumWidth(400)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Generation Parameters")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        hint = QLabel("Changes apply to new requests immediately.")
        hint.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(hint)

        layout.addSpacing(10)

        # Form with settings
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # Temperature (0.0 - 2.0)
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(0.0, 2.0)
        self.temperature_spin.setSingleStep(0.1)
        self.temperature_spin.setDecimals(2)
        self.temperature_spin.setToolTip(
            "Controls randomness. Lower = more focused, higher = more creative."
        )
        form.addRow("Temperature:", self.temperature_spin)

        # Max tokens (1 - 8192)
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(1, 8192)
        self.max_tokens_spin.setSingleStep(64)
        self.max_tokens_spin.setToolTip("Maximum number of tokens to generate.")
        form.addRow("Max Tokens:", self.max_tokens_spin)

        # Top-p (0.0 - 1.0)
        self.top_p_spin = QDoubleSpinBox()
        self.top_p_spin.setRange(0.0, 1.0)
        self.top_p_spin.setSingleStep(0.05)
        self.top_p_spin.setDecimals(2)
        self.top_p_spin.setToolTip(
            "Nucleus sampling. 1.0 = disabled. Lower = more focused."
        )
        form.addRow("Top-p:", self.top_p_spin)

        # Top-k (0 - 100)
        self.top_k_spin = QSpinBox()
        self.top_k_spin.setRange(0, 100)
        self.top_k_spin.setSingleStep(5)
        self.top_k_spin.setToolTip(
            "Limits token choices. 0 = disabled. Lower = more focused."
        )
        form.addRow("Top-k:", self.top_k_spin)

        # Repeat penalty (1.0 - 2.0)
        self.repeat_penalty_spin = QDoubleSpinBox()
        self.repeat_penalty_spin.setRange(1.0, 2.0)
        self.repeat_penalty_spin.setSingleStep(0.05)
        self.repeat_penalty_spin.setDecimals(2)
        self.repeat_penalty_spin.setToolTip(
            "Penalizes repetition. 1.0 = no penalty."
        )
        form.addRow("Repeat Penalty:", self.repeat_penalty_spin)

        layout.addLayout(form)
        layout.addSpacing(10)

        # Reset button
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.clicked.connect(self._reset_to_defaults)
        layout.addWidget(reset_btn)

        layout.addStretch()

        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_settings)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_settings(self):
        """Load current settings from config."""
        config = get_config_manager().config.llm
        self.temperature_spin.setValue(config.temperature)
        self.max_tokens_spin.setValue(config.max_tokens)
        self.top_p_spin.setValue(config.top_p)
        self.top_k_spin.setValue(config.top_k)
        self.repeat_penalty_spin.setValue(config.repeat_penalty)

    def _reset_to_defaults(self):
        """Reset all fields to default values."""
        self.temperature_spin.setValue(DEFAULTS["temperature"])
        self.max_tokens_spin.setValue(DEFAULTS["max_tokens"])
        self.top_p_spin.setValue(DEFAULTS["top_p"])
        self.top_k_spin.setValue(DEFAULTS["top_k"])
        self.repeat_penalty_spin.setValue(DEFAULTS["repeat_penalty"])

    def _save_settings(self):
        """Save settings to config and close."""
        config_manager = get_config_manager()
        config_manager.update(
            **{
                "llm.temperature": self.temperature_spin.value(),
                "llm.max_tokens": self.max_tokens_spin.value(),
                "llm.top_p": self.top_p_spin.value(),
                "llm.top_k": self.top_k_spin.value(),
                "llm.repeat_penalty": self.repeat_penalty_spin.value(),
            }
        )
        self.accept()
