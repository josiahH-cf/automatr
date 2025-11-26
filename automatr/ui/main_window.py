"""Main window for Automatr GUI."""

import sys
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QScrollArea,
    QFrame,
    QTextEdit,
)

from automatr import __version__
from automatr.core.config import get_config
from automatr.core.templates import Template, get_template_manager
from automatr.integrations.llm import get_llm_client, get_llm_server
from automatr.integrations.espanso import get_espanso_manager
from automatr.ui.theme import get_theme_stylesheet
from automatr.ui.template_editor import TemplateEditor


class GenerationWorker(QThread):
    """Background worker for LLM generation."""
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    token_received = pyqtSignal(str)
    
    def __init__(self, prompt: str, stream: bool = True):
        super().__init__()
        self.prompt = prompt
        self.stream = stream
    
    def run(self):
        try:
            client = get_llm_client()
            
            if self.stream:
                result = []
                for token in client.generate_stream(self.prompt):
                    result.append(token)
                    self.token_received.emit(token)
                self.finished.emit("".join(result))
            else:
                result = client.generate(self.prompt)
                self.finished.emit(result)
                
        except Exception as e:
            self.error.emit(str(e))


class VariableFormWidget(QScrollArea):
    """Widget for displaying and editing template variables."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        self.container = QWidget()
        self.layout = QFormLayout(self.container)
        self.layout.setContentsMargins(0, 0, 10, 0)
        self.setWidget(self.container)
        
        self.inputs: dict[str, QWidget] = {}
        self.template: Optional[Template] = None
    
    def set_template(self, template: Template):
        """Set the template and create input fields for its variables."""
        self.template = template
        self.inputs.clear()
        
        # Clear existing widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not template.variables:
            label = QLabel("No variables in this template.")
            label.setStyleSheet("color: #808080; font-style: italic;")
            self.layout.addRow(label)
            return
        
        for var in template.variables:
            if var.multiline:
                widget = QPlainTextEdit()
                widget.setPlaceholderText(var.default or f"Enter {var.label.lower()}...")
                widget.setMaximumHeight(100)
                if var.default:
                    widget.setPlainText(var.default)
            else:
                widget = QLineEdit()
                widget.setPlaceholderText(var.default or f"Enter {var.label.lower()}...")
                if var.default:
                    widget.setText(var.default)
            
            self.inputs[var.name] = widget
            self.layout.addRow(f"{var.label}:", widget)
    
    def get_values(self) -> dict[str, str]:
        """Get the current values from all input fields."""
        values = {}
        for name, widget in self.inputs.items():
            if isinstance(widget, QPlainTextEdit):
                values[name] = widget.toPlainText()
            else:
                values[name] = widget.text()
        return values
    
    def clear(self):
        """Clear all input fields."""
        for widget in self.inputs.values():
            if isinstance(widget, QPlainTextEdit):
                widget.clear()
            else:
                widget.clear()


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Automatr v{__version__}")
        self.setMinimumSize(900, 600)
        
        config = get_config()
        self.resize(config.ui.window_width, config.ui.window_height)
        
        self.current_template: Optional[Template] = None
        self.worker: Optional[GenerationWorker] = None
        
        self._setup_menu_bar()
        self._setup_ui()
        self._setup_status_bar()
        self._setup_shortcuts()
        self._load_templates()
        self._check_llm_status()
    
    def _setup_menu_bar(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Template", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_template)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        sync_action = QAction("&Sync to Espanso", self)
        sync_action.setShortcut(QKeySequence("Ctrl+E"))
        sync_action.triggered.connect(self._sync_espanso)
        file_menu.addAction(sync_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # LLM menu
        llm_menu = menubar.addMenu("&LLM")
        
        self.start_server_action = QAction("&Start Server", self)
        self.start_server_action.triggered.connect(self._start_server)
        llm_menu.addAction(self.start_server_action)
        
        self.stop_server_action = QAction("S&top Server", self)
        self.stop_server_action.triggered.connect(self._stop_server)
        llm_menu.addAction(self.stop_server_action)
        
        llm_menu.addSeparator()
        
        # Model selector submenu
        self.model_menu = llm_menu.addMenu("Select &Model")
        self.model_menu.aboutToShow.connect(self._populate_model_menu)
        
        llm_menu.addSeparator()
        
        refresh_action = QAction("&Check Status", self)
        refresh_action.triggered.connect(self._check_llm_status)
        llm_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About Automatr", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_shortcuts(self):
        """Set up additional keyboard shortcuts."""
        # Generate shortcut
        pass  # Ctrl+G is handled below via button
    
    def _sync_espanso(self):
        """Sync templates to Espanso."""
        manager = get_espanso_manager()
        count = manager.sync()
        
        if count > 0:
            self.status_bar.showMessage(f"Synced {count} templates to Espanso", 3000)
            QMessageBox.information(
                self,
                "Espanso Sync",
                f"Successfully synced {count} templates to Espanso.\n\n"
                "Restart Espanso to apply changes.",
            )
        else:
            self.status_bar.showMessage("No templates to sync", 3000)
    
    def _start_server(self):
        """Start the LLM server."""
        server = get_llm_server()
        if server.is_running():
            self.status_bar.showMessage("Server already running", 3000)
            return
        
        self.status_bar.showMessage("Starting server...", 0)
        QApplication.processEvents()
        
        success, message = server.start()
        
        if success:
            self.status_bar.showMessage("Server started", 3000)
        else:
            QMessageBox.critical(self, "Server Error", message)
        
        self._check_llm_status()
    
    def _stop_server(self):
        """Stop the LLM server."""
        server = get_llm_server()
        success, message = server.stop()
        
        if success:
            self.status_bar.showMessage(message, 3000)
        else:
            QMessageBox.warning(self, "Server", message)
        
        self._check_llm_status()
    
    def _populate_model_menu(self):
        """Populate the model selector submenu with discovered models."""
        self.model_menu.clear()
        
        server = get_llm_server()
        models = server.find_models()
        
        if not models:
            no_models = QAction("No models found", self)
            no_models.setEnabled(False)
            self.model_menu.addAction(no_models)
            
            hint = QAction("Place .gguf files in ~/models/", self)
            hint.setEnabled(False)
            self.model_menu.addAction(hint)
            return
        
        config = get_config()
        current_model = config.llm.model_path
        
        for model in models:
            action = QAction(f"{model.name} ({model.size_gb:.1f} GB)", self)
            action.setCheckable(True)
            action.setChecked(str(model.path) == current_model)
            action.setData(str(model.path))
            action.triggered.connect(lambda checked, m=model: self._select_model(m))
            self.model_menu.addAction(action)
    
    def _select_model(self, model):
        """Select a model and update configuration."""
        from automatr.core.config import get_config_manager
        
        config_manager = get_config_manager()
        config_manager.config.llm.model_path = str(model.path)
        config_manager.save()
        
        self.status_bar.showMessage(f"Selected model: {model.name}", 3000)
        
        # If server is running, inform user they need to restart
        server = get_llm_server()
        if server.is_running():
            QMessageBox.information(
                self,
                "Model Changed",
                f"Model changed to {model.name}.\n\n"
                "Restart the server (LLM → Stop, then Start) to use the new model.",
            )
    
    def _show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Automatr",
            f"<h2>Automatr v{__version__}</h2>"
            "<p>Minimal prompt automation with local LLM.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Template-driven prompts</li>"
            "<li>Local llama.cpp integration</li>"
            "<li>Espanso text expansion</li>"
            "</ul>"
            "<p><a href='https://github.com/yourname/automatr'>GitHub</a></p>",
        )
    
    def _setup_ui(self):
        """Set up the main UI."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Template list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 5, 10)
        
        left_header = QHBoxLayout()
        left_label = QLabel("Templates")
        left_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        left_header.addWidget(left_label)
        
        new_btn = QPushButton("+")
        new_btn.setMaximumWidth(30)
        new_btn.setToolTip("Create new template")
        new_btn.clicked.connect(self._new_template)
        left_header.addWidget(new_btn)
        
        left_layout.addLayout(left_header)
        
        self.template_list = QListWidget()
        self.template_list.itemClicked.connect(self._on_template_selected)
        self.template_list.itemDoubleClicked.connect(self._edit_template)
        left_layout.addWidget(self.template_list)
        
        # Template action buttons
        template_actions = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self._edit_template)
        template_actions.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self._delete_template)
        template_actions.addWidget(delete_btn)
        
        left_layout.addLayout(template_actions)
        
        splitter.addWidget(left_panel)
        
        # Middle panel: Variables
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(5, 10, 5, 10)
        
        middle_label = QLabel("Variables")
        middle_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        middle_layout.addWidget(middle_label)
        
        self.variable_form = VariableFormWidget()
        middle_layout.addWidget(self.variable_form)
        
        # Generate button
        self.generate_btn = QPushButton("Generate (Ctrl+G)")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setShortcut(QKeySequence("Ctrl+G"))
        self.generate_btn.clicked.connect(self._generate)
        middle_layout.addWidget(self.generate_btn)
        
        splitter.addWidget(middle_panel)
        
        # Right panel: Output
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 10, 10, 10)
        
        right_header = QHBoxLayout()
        right_label = QLabel("Output")
        right_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        right_header.addWidget(right_label)
        right_header.addStretch()
        
        copy_btn = QPushButton("Copy")
        copy_btn.setObjectName("secondary")
        copy_btn.clicked.connect(self._copy_output)
        right_header.addWidget(copy_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.setObjectName("secondary")
        clear_btn.clicked.connect(self._clear_output)
        right_header.addWidget(clear_btn)
        
        right_layout.addLayout(right_header)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText(
            "Generated output will appear here.\n\n"
            "1. Select a template from the left\n"
            "2. Fill in the variables\n"
            "3. Click Generate"
        )
        right_layout.addWidget(self.output_text)
        
        splitter.addWidget(right_panel)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 300, 400])
        
        main_layout.addWidget(splitter)
    
    def _setup_status_bar(self):
        """Set up the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.llm_status_label = QLabel("LLM: Checking...")
        self.status_bar.addPermanentWidget(self.llm_status_label)
    
    def _load_templates(self):
        """Load templates from disk."""
        self.template_list.clear()
        manager = get_template_manager()
        
        for template in manager.list_all():
            item = QListWidgetItem(template.name)
            item.setData(Qt.ItemDataRole.UserRole, template)
            if template.description:
                item.setToolTip(template.description)
            self.template_list.addItem(item)
        
        self.status_bar.showMessage(
            f"Loaded {self.template_list.count()} templates", 3000
        )
    
    def _check_llm_status(self):
        """Check if the LLM server is running and update UI."""
        server = get_llm_server()
        is_running = server.is_running()
        
        if is_running:
            self.llm_status_label.setText("LLM: Connected")
            self.llm_status_label.setStyleSheet("color: #4ec9b0;")
        else:
            self.llm_status_label.setText("LLM: Not Running")
            self.llm_status_label.setStyleSheet("color: #f48771;")
        
        # Update menu actions
        self.start_server_action.setEnabled(not is_running)
        self.stop_server_action.setEnabled(is_running)
    
    def _on_template_selected(self, item: QListWidgetItem):
        """Handle template selection."""
        template = item.data(Qt.ItemDataRole.UserRole)
        if template:
            self.current_template = template
            self.variable_form.set_template(template)
            self.generate_btn.setEnabled(True)
    
    def _new_template(self):
        """Create a new template."""
        dialog = TemplateEditor(parent=self)
        dialog.template_saved.connect(self._on_template_saved)
        dialog.exec()
    
    def _edit_template(self):
        """Edit the selected template."""
        if not self.current_template:
            return
        
        dialog = TemplateEditor(self.current_template, parent=self)
        dialog.template_saved.connect(self._on_template_saved)
        dialog.exec()
    
    def _delete_template(self):
        """Delete the selected template."""
        if not self.current_template:
            return
        
        reply = QMessageBox.question(
            self,
            "Delete Template",
            f"Are you sure you want to delete '{self.current_template.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            manager = get_template_manager()
            if manager.delete(self.current_template):
                self.current_template = None
                self.variable_form.clear()
                self.generate_btn.setEnabled(False)
                self._load_templates()
    
    def _on_template_saved(self, template: Template):
        """Handle template saved signal."""
        self._load_templates()
        # Re-select the saved template
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if item and item.text() == template.name:
                self.template_list.setCurrentItem(item)
                self._on_template_selected(item)
                break
    
    def _generate(self):
        """Generate output using the LLM."""
        if not self.current_template:
            return
        
        # Get variable values
        values = self.variable_form.get_values()
        
        # Render the prompt
        prompt = self.current_template.render(values)
        
        # Check LLM status
        server = get_llm_server()
        if not server.is_running():
            reply = QMessageBox.question(
                self,
                "LLM Not Running",
                "The LLM server is not running. Would you like to start it?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success, message = server.start()
                if not success:
                    QMessageBox.critical(self, "Error", message)
                    return
                self._check_llm_status()
            else:
                return
        
        # Disable generate button during generation
        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("Generating...")
        self.output_text.clear()
        
        # Start generation in background
        self.worker = GenerationWorker(prompt, stream=True)
        self.worker.token_received.connect(self._on_token_received)
        self.worker.finished.connect(self._on_generation_finished)
        self.worker.error.connect(self._on_generation_error)
        self.worker.start()
    
    def _on_token_received(self, token: str):
        """Handle streaming token."""
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(token)
        self.output_text.setTextCursor(cursor)
        self.output_text.ensureCursorVisible()
    
    def _on_generation_finished(self, result: str):
        """Handle generation complete."""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate")
        self.status_bar.showMessage("Generation complete", 3000)
    
    def _on_generation_error(self, error: str):
        """Handle generation error."""
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("Generate")
        QMessageBox.critical(self, "Generation Error", error)
    
    def _copy_output(self):
        """Copy output to clipboard."""
        text = self.output_text.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            self.status_bar.showMessage("Copied to clipboard", 2000)
    
    def _clear_output(self):
        """Clear the output pane."""
        self.output_text.clear()


def run_gui() -> int:
    """Run the GUI application.
    
    Returns:
        Exit code.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Automatr")
    app.setApplicationVersion(__version__)
    
    # Apply theme
    config = get_config()
    stylesheet = get_theme_stylesheet(config.ui.theme)
    app.setStyleSheet(stylesheet)
    
    window = MainWindow()
    window.show()
    
    return app.exec()
