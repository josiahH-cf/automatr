"""Template improvement dialog for Automatr.

Unified workflow for template improvement:
1. Prompt user for feedback on what could be better
2. Generate AI-improved template based on feedback
3. Allow user to edit the improved template before saving
4. Save creates a version snapshot for revert capability
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
    """Dialog for reviewing and applying template improvements.
    
    Unified workflow:
    1. User provides feedback on what could be improved
    2. AI generates improved version
    3. User can edit the improved version
    4. User saves, which creates a version snapshot and updates template
    """
    
    # Emitted when user wants to apply changes - carries the new content
    changes_applied = pyqtSignal(str)
    
    def __init__(self, template: Template, initial_feedback: str = "", parent=None):
        super().__init__(parent)
        self.template = template
        self.original_content = template.content
        self.initial_feedback = initial_feedback
        self.improved_content: Optional[str] = None
        self.worker: Optional[ImprovementWorker] = None
        
        self.setWindowTitle(f"Improve Template: {template.name}")
        self.setMinimumSize(800, 600)
        self._setup_ui()
        
        # Start improvement generation with initial feedback
        self._generate_improvement(additional_notes=initial_feedback)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with feedback info
        if self.initial_feedback:
            feedback_label = QLabel(f"Improving based on: \"{self.initial_feedback[:100]}{'...' if len(self.initial_feedback) > 100 else ''}\"")
            feedback_label.setStyleSheet("color: #888; font-style: italic;")
            feedback_label.setWordWrap(True)
            layout.addWidget(feedback_label)
        elif self.template.refinements:
            refinements_label = QLabel(
                f"Improving based on {len(self.template.refinements)} accumulated feedback item(s)"
            )
            refinements_label.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(refinements_label)
        else:
            no_refinements_label = QLabel(
                "No feedback provided. AI will suggest general improvements."
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
        
        # Right side: Improved (editable)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(5, 0, 0, 0)
        
        right_header = QHBoxLayout()
        right_label = QLabel("Improved Template (Editable)")
        right_label.setStyleSheet("font-weight: bold;")
        right_header.addWidget(right_label)
        right_header.addStretch()
        
        # Edit hint
        edit_hint = QLabel("You can edit this before saving")
        edit_hint.setStyleSheet("color: #888; font-size: 11px;")
        right_header.addWidget(edit_hint)
        right_layout.addLayout(right_header)
        
        self.improved_text = QPlainTextEdit()
        self.improved_text.setPlaceholderText("Generating improvements...")
        # Editable - user can modify before saving
        self.improved_text.setReadOnly(False)
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
        
        # Edit system prompt button (left side)
        self.edit_prompt_btn = QPushButton("Edit AI Prompt...")
        self.edit_prompt_btn.setObjectName("secondary")
        self.edit_prompt_btn.setStyleSheet("background-color: #ffcccc;")
        self.edit_prompt_btn.setToolTip("Customize the system prompt used for AI improvements")
        self.edit_prompt_btn.clicked.connect(self._edit_system_prompt)
        button_layout.addWidget(self.edit_prompt_btn)
        
        button_layout.addStretch()
        
        self.discard_btn = QPushButton("Discard")
        self.discard_btn.setObjectName("secondary")
        self.discard_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.discard_btn)
        
        self.regenerate_btn = QPushButton("Regenerate with Notes")
        self.regenerate_btn.setObjectName("secondary")
        self.regenerate_btn.setEnabled(False)
        self.regenerate_btn.setToolTip("Re-run AI improvement with additional guidance")
        self.regenerate_btn.clicked.connect(self._regenerate_with_notes)
        button_layout.addWidget(self.regenerate_btn)
        
        self.apply_btn = QPushButton("Save Changes")
        self.apply_btn.setEnabled(False)
        self.apply_btn.setToolTip("Save your edits as the new template version")
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
        self.status_label.setText("Review and edit the improvements, then save")
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
        """Apply the edited template content.
        
        Uses the user's edits (not just the raw AI output).
        """
        # Get the user-edited content from the text box
        edited_content = self.improved_text.toPlainText().strip()
        if edited_content:
            self.changes_applied.emit(edited_content)
            self.accept()
    
    def _edit_system_prompt(self):
        """Open dialog to edit the system improvement prompt."""
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            "Edit AI Prompt?",
            "Editing the AI prompt will affect how all future template improvements are generated.\n\nAre you sure you want to continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        dialog = ImprovementPromptEditor(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Prompt was saved, user might want to regenerate
            reply = QMessageBox.question(
                self,
                "Regenerate?",
                "System prompt updated. Would you like to regenerate the improvement with the new prompt?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._generate_improvement(additional_notes=self.initial_feedback)


class ImprovementPromptEditor(QDialog):
    """Dialog for editing the system prompt used for template improvements."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit AI Improvement Prompt")
        self.setMinimumSize(700, 500)
        self._setup_ui()
    
    def _setup_ui(self):
        from automatr.core.config import load_improvement_prompt, DEFAULT_IMPROVEMENT_PROMPT
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Customize the prompt sent to the AI when improving templates.\n"
            "Available placeholders: {{template_content}}, {{refinements}}, {{additional_notes}}"
        )
        instructions.setStyleSheet("color: #888; margin-bottom: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Text editor
        self.prompt_edit = QPlainTextEdit()
        self.prompt_edit.setPlainText(load_improvement_prompt())
        self.prompt_edit.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.prompt_edit)
        
        # Validation warning
        self.warning_label = QLabel("")
        self.warning_label.setStyleSheet("color: #ff6b6b;")
        self.warning_label.setVisible(False)
        layout.addWidget(self.warning_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.setObjectName("secondary")
        reset_btn.setToolTip("Restore the default improvement prompt")
        reset_btn.clicked.connect(lambda: self.prompt_edit.setPlainText(DEFAULT_IMPROVEMENT_PROMPT))
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _save(self):
        """Save the prompt and close dialog."""
        from automatr.core.config import save_improvement_prompt
        
        prompt = self.prompt_edit.toPlainText()
        
        # Validate required placeholder
        if "{{template_content}}" not in prompt:
            self.warning_label.setText("Warning: Prompt must contain {{template_content}} placeholder")
            self.warning_label.setVisible(True)
            reply = QMessageBox.warning(
                self,
                "Missing Placeholder",
                "The prompt is missing the {{template_content}} placeholder.\n\n"
                "Without this, the AI won't receive the template to improve.\n\n"
                "Save anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        if save_improvement_prompt(prompt):
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save prompt")
