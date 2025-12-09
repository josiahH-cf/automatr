"""Template editor widget for Automatr."""

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QCheckBox,
    QMessageBox,
)

from automatr.core.templates import Template, Variable, get_template_manager


class VariableEditor(QDialog):
    """Dialog for editing a single variable."""
    
    def __init__(self, variable: Optional[Variable] = None, parent=None):
        super().__init__(parent)
        self.variable = variable
        self.setWindowTitle("Edit Variable" if variable else "Add Variable")
        self.setMinimumWidth(400)
        self._setup_ui()
        
        if variable:
            self._load_variable(variable)
    
    def _setup_ui(self):
        layout = QFormLayout(self)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., code, language, description")
        layout.addRow("Name:", self.name_edit)
        
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Display label (optional)")
        layout.addRow("Label:", self.label_edit)
        
        self.default_edit = QLineEdit()
        self.default_edit.setPlaceholderText("Default value (optional)")
        layout.addRow("Default:", self.default_edit)
        
        self.multiline_check = QCheckBox("Multi-line input")
        layout.addRow("", self.multiline_check)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def _load_variable(self, var: Variable):
        self.name_edit.setText(var.name)
        self.label_edit.setText(var.label)
        self.default_edit.setText(var.default)
        self.multiline_check.setChecked(var.multiline)
    
    def get_variable(self) -> Optional[Variable]:
        name = self.name_edit.text().strip()
        if not name:
            return None
        
        return Variable(
            name=name,
            label=self.label_edit.text().strip(),
            default=self.default_edit.text().strip(),
            multiline=self.multiline_check.isChecked(),
        )


class TemplateEditor(QDialog):
    """Dialog for editing a template."""
    
    template_saved = pyqtSignal(Template)
    
    def __init__(self, template: Optional[Template] = None, parent=None, last_folder: str = ""):
        super().__init__(parent)
        self.template = template
        self.variables: list[Variable] = list(template.variables) if template else []
        self._last_folder = last_folder
        
        # Get initial folder for existing templates
        self._initial_folder = ""
        if template:
            manager = get_template_manager()
            self._initial_folder = manager.get_template_folder(template)
        
        self.setWindowTitle("Edit Template" if template else "New Template")
        self.setMinimumSize(600, 500)
        self._setup_ui()
        
        if template:
            self._load_template(template)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form layout for basic fields
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Template name")
        form.addRow("Name:", self.name_edit)
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Short description (optional)")
        form.addRow("Description:", self.description_edit)
        
        self.trigger_edit = QLineEdit()
        self.trigger_edit.setPlaceholderText(":trigger (for Espanso, optional)")
        form.addRow("Trigger:", self.trigger_edit)
        
        # Folder selection
        self.folder_combo = QComboBox()
        self._populate_folders()
        form.addRow("Folder:", self.folder_combo)
        
        layout.addLayout(form)
        
        # Variables section
        var_label = QLabel("Variables:")
        layout.addWidget(var_label)
        
        var_layout = QHBoxLayout()
        
        self.var_list = QListWidget()
        self.var_list.setMaximumHeight(120)
        var_layout.addWidget(self.var_list)
        
        var_buttons = QVBoxLayout()
        
        add_var_btn = QPushButton("Add")
        add_var_btn.clicked.connect(self._add_variable)
        var_buttons.addWidget(add_var_btn)
        
        edit_var_btn = QPushButton("Edit")
        edit_var_btn.clicked.connect(self._edit_variable)
        var_buttons.addWidget(edit_var_btn)
        
        del_var_btn = QPushButton("Delete")
        del_var_btn.setObjectName("danger")
        del_var_btn.clicked.connect(self._delete_variable)
        var_buttons.addWidget(del_var_btn)
        
        var_buttons.addStretch()
        var_layout.addLayout(var_buttons)
        
        layout.addLayout(var_layout)
        
        # Content section
        content_label = QLabel("Content (use {{variable_name}} for placeholders):")
        layout.addWidget(content_label)
        
        self.content_edit = QPlainTextEdit()
        self.content_edit.setPlaceholderText(
            "Enter your template content here.\n"
            "Use {{variable_name}} for placeholders."
        )
        layout.addWidget(self.content_edit)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _load_template(self, template: Template):
        self.name_edit.setText(template.name)
        self.description_edit.setText(template.description)
        self.trigger_edit.setText(template.trigger)
        self.content_edit.setPlainText(template.content)
        self._refresh_var_list()
    
    def _refresh_var_list(self):
        self.var_list.clear()
        for var in self.variables:
            text = f"{{{{ {var.name} }}}}"
            if var.label != var.name:
                text += f" - {var.label}"
            if var.multiline:
                text += " [multiline]"
            self.var_list.addItem(text)
    
    def _add_variable(self):
        dialog = VariableEditor(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            var = dialog.get_variable()
            if var:
                self.variables.append(var)
                self._refresh_var_list()
    
    def _edit_variable(self):
        row = self.var_list.currentRow()
        if row < 0 or row >= len(self.variables):
            return
        
        dialog = VariableEditor(self.variables[row], parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            var = dialog.get_variable()
            if var:
                self.variables[row] = var
                self._refresh_var_list()
    
    def _delete_variable(self):
        row = self.var_list.currentRow()
        if row < 0 or row >= len(self.variables):
            return
        
        del self.variables[row]
        self._refresh_var_list()
    
    def _populate_folders(self):
        """Populate the folder combobox."""
        manager = get_template_manager()
        self.folder_combo.clear()
        self.folder_combo.addItem("(No folder)", "")  # Root level
        
        for folder in manager.list_folders():
            self.folder_combo.addItem(f"📁 {folder}", folder)
        
        # Select initial folder (existing template) or last used folder (new template)
        folder_to_select = self._initial_folder or self._last_folder
        if folder_to_select:
            index = self.folder_combo.findData(folder_to_select)
            if index >= 0:
                self.folder_combo.setCurrentIndex(index)
    
    def _save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Template name is required.")
            return
        
        content = self.content_edit.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Error", "Template content is required.")
            return
        
        # Get selected folder
        folder = self.folder_combo.currentData() or ""
        
        # Create or update template
        if self.template:
            self.template.name = name
            self.template.description = self.description_edit.text().strip()
            self.template.trigger = self.trigger_edit.text().strip()
            self.template.content = content
            self.template.variables = self.variables
            template = self.template
        else:
            template = Template(
                name=name,
                description=self.description_edit.text().strip(),
                trigger=self.trigger_edit.text().strip(),
                content=content,
                variables=self.variables,
            )
        
        # Save to disk (with folder support)
        manager = get_template_manager()
        if manager.save_to_folder(template, folder):
            self.template_saved.emit(template)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save template.")
