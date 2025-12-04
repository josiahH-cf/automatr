"""Main window for Automatr GUI."""

import shutil
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QKeySequence, QDesktopServices, QShortcut, QWheelEvent
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPlainTextEdit,
    QProgressDialog,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QScrollArea,
    QFrame,
    QTextEdit,
)

from automatr import __version__
from automatr.core.config import get_config, save_config
from automatr.core.templates import Template, get_template_manager
from automatr.integrations.llm import get_llm_client, get_llm_server
from automatr.integrations.espanso import get_espanso_manager
from automatr.ui.theme import get_theme_stylesheet
from automatr.ui.template_editor import TemplateEditor
from automatr.ui.llm_settings import LLMSettingsDialog


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


class ModelCopyWorker(QThread):
    """Background worker for copying model files with progress."""
    
    finished = pyqtSignal(bool, str)  # success, message or path
    progress = pyqtSignal(int)  # percentage 0-100
    
    def __init__(self, source: Path, dest: Path):
        super().__init__()
        self.source = source
        self.dest = dest
        self._canceled = False
    
    def cancel(self):
        """Request cancellation of the copy operation."""
        self._canceled = True
    
    def run(self):
        try:
            total_size = self.source.stat().st_size
            copied = 0
            chunk_size = 1024 * 1024  # 1MB chunks
            
            with open(self.source, "rb") as src:
                with open(self.dest, "wb") as dst:
                    while True:
                        if self._canceled:
                            dst.close()
                            if self.dest.exists():
                                self.dest.unlink()
                            self.finished.emit(False, "Copy canceled")
                            return
                        
                        chunk = src.read(chunk_size)
                        if not chunk:
                            break
                        dst.write(chunk)
                        copied += len(chunk)
                        percent = int((copied / total_size) * 100)
                        self.progress.emit(percent)
            
            # Copy file metadata
            shutil.copystat(self.source, self.dest)
            self.finished.emit(True, str(self.dest))
            
        except PermissionError:
            # Clean up partial file
            if self.dest.exists():
                self.dest.unlink()
            self.finished.emit(False, f"Permission denied writing to:\n{self.dest.parent}")
        except OSError as e:
            if self.dest.exists():
                self.dest.unlink()
            self.finished.emit(False, f"Failed to copy file: {e}")


class VariableFormWidget(QScrollArea):
    """Widget for displaying and editing template variables."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        
        self.container = QWidget()
        self.layout = QFormLayout(self.container)
        self.layout.setContentsMargins(0, 0, 10, 0)
        self.layout.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.layout.setVerticalSpacing(12)
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
            label.setWordWrap(True)
            self.layout.addRow(label)
            return
        
        for var in template.variables:
            # Create label with word wrap
            label = QLabel(f"{var.label}:")
            label.setWordWrap(True)
            
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
            self.layout.addRow(label, widget)
    
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
        
        download_models_action = QAction("&Download Models (Hugging Face)...", self)
        download_models_action.triggered.connect(self._open_hugging_face)
        llm_menu.addAction(download_models_action)
        
        llm_menu.addSeparator()
        
        refresh_action = QAction("&Check Status", self)
        refresh_action.triggered.connect(self._check_llm_status)
        llm_menu.addAction(refresh_action)
        
        llm_menu.addSeparator()
        
        settings_action = QAction("S&ettings...", self)
        settings_action.triggered.connect(self._show_llm_settings)
        llm_menu.addAction(settings_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About Automatr", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_shortcuts(self):
        """Set up additional keyboard shortcuts."""
        # Font scaling shortcuts
        QShortcut(QKeySequence("Ctrl++"), self).activated.connect(self._increase_font)
        QShortcut(QKeySequence("Ctrl+="), self).activated.connect(self._increase_font)
        QShortcut(QKeySequence("Ctrl+-"), self).activated.connect(self._decrease_font)
        QShortcut(QKeySequence("Ctrl+0"), self).activated.connect(self._reset_font)
    
    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel events for font scaling with Ctrl."""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._increase_font()
            elif delta < 0:
                self._decrease_font()
            event.accept()
        else:
            super().wheelEvent(event)
    
    def _apply_font_size(self, size: int):
        """Apply a new font size to the application."""
        # Clamp to reasonable bounds
        size = max(8, min(24, size))
        
        config = get_config()
        config.ui.font_size = size
        save_config(config)
        
        # Apply new stylesheet
        stylesheet = get_theme_stylesheet(config.ui.theme, size)
        QApplication.instance().setStyleSheet(stylesheet)
        
        # Update section labels (they have hardcoded sizes)
        label_size = size + 1
        label_style = f"font-weight: bold; font-size: {label_size}pt;"
        for label in self.findChildren(QLabel):
            if label.text() in ("Templates", "Variables", "Output"):
                label.setStyleSheet(label_style)
        
        self.status_bar.showMessage(f"Font size: {size}pt", 2000)
    
    def _increase_font(self):
        """Increase font size by 1pt."""
        config = get_config()
        self._apply_font_size(config.ui.font_size + 1)
    
    def _decrease_font(self):
        """Decrease font size by 1pt."""
        config = get_config()
        self._apply_font_size(config.ui.font_size - 1)
    
    def _reset_font(self):
        """Reset font size to default (13pt)."""
        self._apply_font_size(13)
    
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
            
            self.model_menu.addSeparator()
            add_action = QAction("Add Model from File...", self)
            add_action.triggered.connect(self._add_model_from_file)
            self.model_menu.addAction(add_action)
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
        
        # Always show Add Model option at the bottom
        self.model_menu.addSeparator()
        add_action = QAction("Add Model from File...", self)
        add_action.triggered.connect(self._add_model_from_file)
        self.model_menu.addAction(add_action)
    
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
    
    def _open_hugging_face(self):
        """Open Hugging Face models page in browser."""
        url = QUrl("https://huggingface.co/models?sort=trending&search=gguf")
        QDesktopServices.openUrl(url)
        self.status_bar.showMessage("Opened Hugging Face in browser", 3000)

    def _launch_web_server(self):
        """Open the LLM web server in the default browser."""
        config = get_config()
        port = config.llm.server_port
        url = QUrl(f"http://127.0.0.1:{port}")
        QDesktopServices.openUrl(url)
        self.status_bar.showMessage(f"Opened http://127.0.0.1:{port} in browser", 3000)

    def _add_model_from_file(self):
        """Add a model from a local GGUF file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select GGUF Model",
            str(Path.home()),
            "GGUF Models (*.gguf);;All Files (*)",
        )
        
        if not file_path:
            return  # User cancelled
        
        source = Path(file_path)
        server = get_llm_server()
        dest_dir = server.get_models_dir()
        dest = dest_dir / source.name
        
        # Check if already exists
        if dest.exists():
            QMessageBox.warning(
                self,
                "Model Exists",
                f"A model with this name already exists:\n{dest}\n\n"
                "Please rename the file or remove the existing model.",
            )
            return
        
        # Get file size for progress
        file_size = source.stat().st_size
        size_gb = file_size / (1024 ** 3)
        
        # Set up progress dialog
        self.progress_dialog = QProgressDialog(
            f"Copying {source.name} ({size_gb:.1f} GB)...",
            "Cancel",
            0,
            100,
            self,
        )
        self.progress_dialog.setWindowTitle("Adding Model")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.setValue(0)
        
        # Start copy worker
        self.copy_worker = ModelCopyWorker(source, dest)
        self.copy_worker.progress.connect(self.progress_dialog.setValue)
        self.copy_worker.finished.connect(self._on_model_copy_finished)
        self.progress_dialog.canceled.connect(self._on_model_copy_canceled)
        
        self.copy_worker.start()
        self.progress_dialog.show()
    
    def _on_model_copy_canceled(self):
        """Handle user canceling the copy operation."""
        if hasattr(self, "copy_worker") and self.copy_worker.isRunning():
            self.copy_worker.cancel()
            self.copy_worker.wait(timeout=5000)  # Wait up to 5 seconds
        
        self.status_bar.showMessage("Model import canceled", 3000)
    
    def _on_model_copy_finished(self, success: bool, message: str):
        """Handle model copy completion."""
        self.progress_dialog.close()
        
        if success:
            # Auto-select the new model
            from automatr.core.config import get_config_manager
            from automatr.integrations.llm import ModelInfo
            
            model_path = Path(message)
            model = ModelInfo.from_path(model_path)
            
            config_manager = get_config_manager()
            config_manager.config.llm.model_path = str(model_path)
            config_manager.save()
            
            QMessageBox.information(
                self,
                "Model Added",
                f"Successfully added model:\n{model.name}\n\n"
                "The model is now selected and ready to use.",
            )
            self.status_bar.showMessage(f"Added model: {model.name}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Import Failed",
                f"Failed to import model:\n\n{message}",
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
        config = get_config()
        label_size = config.ui.font_size + 1
        left_label.setStyleSheet(f"font-weight: bold; font-size: {label_size}pt;")
        left_header.addWidget(left_label)
        
        new_folder_btn = QPushButton("📁")
        new_folder_btn.setMaximumWidth(30)
        new_folder_btn.setToolTip("Create new folder")
        new_folder_btn.clicked.connect(self._new_folder)
        left_header.addWidget(new_folder_btn)
        
        new_btn = QPushButton("+")
        new_btn.setMaximumWidth(30)
        new_btn.setToolTip("Create new template")
        new_btn.clicked.connect(self._new_template)
        left_header.addWidget(new_btn)
        
        left_layout.addLayout(left_header)
        
        self.template_tree = QTreeWidget()
        self.template_tree.setHeaderHidden(True)
        self.template_tree.itemClicked.connect(self._on_tree_item_clicked)
        self.template_tree.itemDoubleClicked.connect(self._on_tree_item_double_clicked)
        left_layout.addWidget(self.template_tree)
        
        # Template action buttons
        template_actions = QHBoxLayout()
        
        edit_btn = QPushButton("Edit")
        edit_btn.setObjectName("secondary")
        edit_btn.clicked.connect(self._edit_template)
        template_actions.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("danger")
        delete_btn.clicked.connect(self._delete_selected)
        template_actions.addWidget(delete_btn)
        
        left_layout.addLayout(template_actions)
        
        splitter.addWidget(left_panel)
        
        # Middle panel: Variables
        middle_panel = QWidget()
        middle_layout = QVBoxLayout(middle_panel)
        middle_layout.setContentsMargins(5, 10, 5, 10)
        
        middle_label = QLabel("Variables")
        middle_label.setStyleSheet(f"font-weight: bold; font-size: {label_size}pt;")
        middle_layout.addWidget(middle_label)
        
        self.variable_form = VariableFormWidget()
        middle_layout.addWidget(self.variable_form)
        
        # Generate button
        self.generate_btn = QPushButton("Render with AI (Ctrl+G)")
        self.generate_btn.setEnabled(False)
        self.generate_btn.setShortcut(QKeySequence("Ctrl+G"))
        self.generate_btn.clicked.connect(self._generate)
        middle_layout.addWidget(self.generate_btn)
        
        # Render template only button (no AI)
        self.render_template_btn = QPushButton("Copy Template (Ctrl+Shift+G)")
        self.render_template_btn.setEnabled(False)
        self.render_template_btn.setShortcut(QKeySequence("Ctrl+Shift+G"))
        self.render_template_btn.clicked.connect(self._render_template_only)
        middle_layout.addWidget(self.render_template_btn)
        
        splitter.addWidget(middle_panel)
        
        # Right panel: Output
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 10, 10, 10)
        
        right_header = QHBoxLayout()
        right_label = QLabel("Output")
        right_label.setStyleSheet(f"font-weight: bold; font-size: {label_size}pt;")
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

        self.launch_server_btn = QPushButton("Launch Web Server")
        self.launch_server_btn.setObjectName("secondary")
        self.launch_server_btn.clicked.connect(self._launch_web_server)
        self.status_bar.addWidget(self.launch_server_btn)

        self.llm_status_label = QLabel("LLM: Checking...")
        self.status_bar.addPermanentWidget(self.llm_status_label)
    
    def _load_templates(self):
        """Load templates from disk, grouped by folder."""
        self.template_tree.clear()
        manager = get_template_manager()
        
        # Get all templates and organize by folder
        templates_by_folder: dict[str, list[Template]] = {"": []}  # "" = root/uncategorized
        
        for folder in manager.list_folders():
            templates_by_folder[folder] = []
        
        for template in manager.list_all():
            folder = manager.get_template_folder(template)
            if folder not in templates_by_folder:
                templates_by_folder[folder] = []
            templates_by_folder[folder].append(template)
        
        total_count = 0
        
        # Add uncategorized templates first (root level)
        for template in sorted(templates_by_folder.get("", []), key=lambda t: t.name.lower()):
            item = QTreeWidgetItem([template.name])
            item.setData(0, Qt.ItemDataRole.UserRole, ("template", template))
            if template.description:
                item.setToolTip(0, template.description)
            self.template_tree.addTopLevelItem(item)
            total_count += 1
        
        # Add folders with their templates
        for folder in sorted(templates_by_folder.keys()):
            if folder == "":
                continue  # Already handled uncategorized
            
            folder_item = QTreeWidgetItem([f"📁 {folder}"])
            folder_item.setData(0, Qt.ItemDataRole.UserRole, ("folder", folder))
            folder_item.setExpanded(True)
            
            folder_templates = templates_by_folder[folder]
            if not folder_templates:
                folder_item.setToolTip(0, "Empty folder")
            
            for template in sorted(folder_templates, key=lambda t: t.name.lower()):
                child = QTreeWidgetItem([template.name])
                child.setData(0, Qt.ItemDataRole.UserRole, ("template", template))
                if template.description:
                    child.setToolTip(0, template.description)
                folder_item.addChild(child)
                total_count += 1
            
            self.template_tree.addTopLevelItem(folder_item)
        
        self.status_bar.showMessage(f"Loaded {total_count} templates", 3000)
    
    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item single click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == "template":
            template = data[1]
            self.current_template = template
            self.variable_form.set_template(template)
            self.generate_btn.setEnabled(True)
            self.render_template_btn.setEnabled(True)
        else:
            # Folder clicked - clear selection
            self.current_template = None
            self.variable_form.clear()
            self.generate_btn.setEnabled(False)
            self.render_template_btn.setEnabled(False)
    
    def _on_tree_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle tree item double click."""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == "template":
            self._edit_template()
    
    def _new_folder(self):
        """Create a new template folder."""
        name, ok = QInputDialog.getText(
            self,
            "New Folder",
            "Enter folder name:",
        )
        if ok and name.strip():
            manager = get_template_manager()
            if manager.create_folder(name.strip()):
                self._load_templates()
                self.status_bar.showMessage(f"Created folder '{name.strip()}'", 3000)
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not create folder '{name.strip()}'. It may already exist or contain invalid characters.",
                )
    
    def _delete_selected(self):
        """Delete the selected item (template or folder)."""
        item = self.template_tree.currentItem()
        if not item:
            return
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if not data:
            return
        
        if data[0] == "template":
            self._delete_template()
        elif data[0] == "folder":
            self._delete_folder(data[1])
    
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
    
    def _show_llm_settings(self):
        """Show the LLM settings dialog."""
        dialog = LLMSettingsDialog(self)
        dialog.exec()
    
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
        
        # Build confirmation message
        message = f"Are you sure you want to delete '{self.current_template.name}'?"
        if self.current_template.trigger:
            message += f"\n\nThis template has an Espanso trigger ({self.current_template.trigger}) which will be removed."
        
        reply = QMessageBox.question(
            self,
            "Delete Template",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            manager = get_template_manager()
            had_trigger = bool(self.current_template.trigger)
            
            if manager.delete(self.current_template):
                self.current_template = None
                self.variable_form.clear()
                self.generate_btn.setEnabled(False)
                self.render_template_btn.setEnabled(False)
                self._load_templates()
                
                # Auto-sync Espanso if enabled and template had a trigger
                config = get_config()
                if had_trigger and config.espanso.enabled and config.espanso.auto_sync:
                    espanso = get_espanso_manager()
                    if espanso.is_available():
                        espanso.sync()
                        self.status_bar.showMessage("Template deleted and Espanso synced", 3000)
                    else:
                        self.status_bar.showMessage("Template deleted", 3000)
                else:
                    self.status_bar.showMessage("Template deleted", 3000)
            else:
                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    f"Failed to delete template '{self.current_template.name}'."
                )
    
    def _on_template_saved(self, template: Template):
        """Handle template saved signal."""
        self._load_templates()
        # Re-select the saved template in tree
        self._select_template_in_tree(template.name)
        
        # Auto-sync Espanso if enabled and template has a trigger
        config = get_config()
        if template.trigger and config.espanso.enabled and config.espanso.auto_sync:
            espanso = get_espanso_manager()
            if espanso.is_available():
                espanso.sync()
                self.status_bar.showMessage(f"Template saved and Espanso synced", 3000)
    
    def _select_template_in_tree(self, template_name: str):
        """Select a template in the tree by name."""
        def find_in_item(item: QTreeWidgetItem) -> bool:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data[0] == "template" and data[1].name == template_name:
                self.template_tree.setCurrentItem(item)
                self._on_tree_item_clicked(item, 0)
                return True
            for i in range(item.childCount()):
                if find_in_item(item.child(i)):
                    return True
            return False
        
        for i in range(self.template_tree.topLevelItemCount()):
            if find_in_item(self.template_tree.topLevelItem(i)):
                break
    
    def _delete_folder(self, folder_name: str):
        """Delete a template folder."""
        manager = get_template_manager()
        success, error_msg = manager.delete_folder(folder_name)
        
        if success:
            self._load_templates()
            self.status_bar.showMessage(f"Deleted folder '{folder_name}'", 3000)
        else:
            QMessageBox.warning(
                self,
                "Cannot Delete Folder",
                error_msg,
            )
    
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
    
    def _render_template_only(self):
        """Render template with variable substitution only (no AI)."""
        if not self.current_template:
            return
        
        # Get variable values and render
        values = self.variable_form.get_values()
        rendered = self.current_template.render(values)
        
        # Display in output
        self.output_text.setPlainText(rendered)
        
        # Auto-copy to clipboard
        QApplication.clipboard().setText(rendered)
        self.status_bar.showMessage("Template copied to clipboard", 3000)
    
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
    
    # Apply theme with font size
    config = get_config()
    stylesheet = get_theme_stylesheet(config.ui.theme, config.ui.font_size)
    app.setStyleSheet(stylesheet)
    
    window = MainWindow()
    window.show()
    
    return app.exec()
