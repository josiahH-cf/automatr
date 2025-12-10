"""Template improvement dialog for Automatr.

Shows a diff view between original and improved template content,
allowing users to apply, regenerate, or discard changes.
"""

from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QWidget,
    QMessageBox,
    QInputDialog,
)

from automatr.core.templates import Template
from automatr.core.feedback import build_improvement_prompt
from automatr.integrations.llm import get_llm_client


class ImprovementWorker(QThread):
    """Background worker for LLM-based template improvement."""
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt
    
    def run(self):
        try:
            client = get_llm_client()
            result = client.generate(self.prompt)
            # Clean up result - remove any markdown code blocks if present
            result = result.strip()
            if result.startswith("```"):
                lines = result.split("\n")
                # Remove first line (```markdown or similar)
                lines = lines[1:]
                # Remove last line if it's ```
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                result = "\n".join(lines)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class TemplateImproveDialog(QDialog):
    """Dialog for reviewing and applying template improvements."""
    
    # Emitted when user wants to apply changes - carries the new content
    changes_applied = pyqtSignal(str)
    
    def __init__(self, template: Template, parent=None):
        super().__init__(parent)
        self.template = template
        self.original_content = template.content
        self.improved_content: Optional[str] = None
        self.worker: Optional[ImprovementWorker] = None
        
        self.setWindowTitle(f"Improve Template: {template.name}")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        
        # Start improvement generation
        self._generate_improvement()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with refinements info
        if self.template.refinements:
            refinements_label = QLabel(
                f"Improving based on {len(self.template.refinements)} feedback item(s)"
            )
            refinements_label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(refinements_label)
        else:
            no_refinements_label = QLabel(
                "No feedback collected yet. AI will suggest general improvements."
            )
            no_refinements_label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(no_refinements_label)
        
        # Splitter for side-by-side view
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side: Original
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 5, 0)
        
        left_label = QLabel("Original Template")
        left_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(left_label)
        
        self.original_text = QPlainTextEdit()
        self.original_text.setPlainText(self.original_content)
        self.original_text.setReadOnly(True)
        left_layout.addWidget(self.original_text)
        
        splitter.addWidget(left_widget)
        
        # Right side: Improved
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)
        
        right_label = QLabel("Suggested Improvements")
        right_label.setStyleSheet("font-weight: bold;")
        right_layout.addWidget(right_label)
        
        self.improved_text = QPlainTextEdit()
        self.improved_text.setPlaceholderText("Generating improvements...")
        self.improved_text.setReadOnly(True)
        right_layout.addWidget(self.improved_text)
        
        splitter.addWidget(right_widget)
        
        # Set equal sizes
        splitter.setSizes([400, 400])
        
        layout.addWidget(splitter)
        
        # Status label
        self.status_label = QLabel("Generating improvements...")
        self.status_label.setStyleSheet("color: #888;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setObjectName("secondary")
        self.discard_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.discard_btn)
        
        self.regenerate_btn = QPushButton("Regenerate with Notes")
        self.regenerate_btn.setObjectName("secondary")
        self.regenerate_btn.setEnabled(False)
        self.regenerate_btn.clicked.connect(self._regenerate_with_notes)
        button_layout.addWidget(self.regenerate_btn)
        
        self.apply_btn = QPushButton("Apply Changes")
        self.apply_btn.setEnabled(False)
        self.apply_btn.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
    
    def _generate_improvement(self, additional_notes: str = ""):
        """Generate improved template using LLM."""
        self.status_label.setText("Generating improvements...")
        self.improved_text.setPlainText("")
        self.apply_btn.setEnabled(False)
        self.regenerate_btn.setEnabled(False)
        
        prompt = build_improvement_prompt(
            template_content=self.original_content,
            refinements=self.template.refinements,
            additional_notes=additional_notes,
        )
        
        self.worker = ImprovementWorker(prompt)
        self.worker.finished.connect(self._on_improvement_finished)
        self.worker.error.connect(self._on_improvement_error)
        self.worker.start()
    
    def _on_improvement_finished(self, result: str):
        """Handle successful improvement generation."""
        self.improved_content = result
        self.improved_text.setPlainText(result)
        self.status_label.setText("Review the suggested improvements")
        self.apply_btn.setEnabled(True)
        self.regenerate_btn.setEnabled(True)
    
    def _on_improvement_error(self, error: str):
        """Handle improvement generation error."""
        self.status_label.setText(f"Error: {error}")
        self.regenerate_btn.setEnabled(True)
        QMessageBox.critical(self, "Generation Error", error)
    
    def _regenerate_with_notes(self):
        """Regenerate with additional user notes."""
        notes, ok = QInputDialog.getMultiLineText(
            self,
            "Additional Notes",
            "What else should be changed?",
            "",
        )
        
        if ok and notes.strip():
            self._generate_improvement(additional_notes=notes.strip())
    
    def _apply_changes(self):
        """Apply the improved template content."""
        if self.improved_content:
            self.changes_applied.emit(self.improved_content)
            self.accept()
