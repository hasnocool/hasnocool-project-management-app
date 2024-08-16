import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton,
                             QTreeView, QSplitter, QLabel, QLineEdit, QComboBox, QTextEdit,
                             QFileDialog, QMenu, QMessageBox, QPlainTextEdit, QDialog,
                             QDialogButtonBox, QInputDialog, QHeaderView, QMenuBar,
                             QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QDir, QDateTime, QCoreApplication
from PyQt6.QtGui import QIcon, QAction
from file_system.custom_file_system_model import CustomFileSystemModel
from context_menu.context_menu import ContextMenu
from project_creation.project_creation_thread import ProjectCreationThread
from file_monitoring.file_monitor_thread import FileMonitorThread
from config.config_manager import ConfigManager  # Import ConfigManager
from version_management.version_manager import VersionManager
from file_monitoring.file_tracker import FileTracker


class FileTrackerThread(QThread):
    tracker_finished = pyqtSignal(str)

    def __init__(self, project_root_dir):
        super().__init__()
        self.project_root_dir = project_root_dir

    def run(self):
        FileTracker.scan_and_track_untracked_files(self.project_root_dir)
        self.tracker_finished.emit("Scan complete, file_tracker.json updated.")


class CompressionThread(QThread):
    compression_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, files_to_compress, output_file):
        super().__init__()
        self.files_to_compress = files_to_compress
        self.output_file = output_file

    def run(self):
        try:
            result = subprocess.run(["7z", "a", self.output_file] + self.files_to_compress, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                self.compression_finished.emit(f"Successfully compressed to {self.output_file}")
            else:
                raise subprocess.CalledProcessError(result.returncode, result.args, output=result.stdout, stderr=result.stderr)
        except subprocess.CalledProcessError as e:
            error_message = e.stderr or e.stdout or str(e)
            self.error_occurred.emit(f"An error occurred while compressing: {error_message}")


class FileReadWriteThread(QThread):
    operation_finished = pyqtSignal(str, str)  # file_path, content or error message
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path, mode, content=None):
        super().__init__()
        self.file_path = file_path
        self.mode = mode
        self.content = content

    def run(self):
        try:
            if self.mode == 'read':
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.operation_finished.emit(self.file_path, content)
            elif self.mode == 'write':
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    f.write(self.content)
                self.operation_finished.emit(self.file_path, "Save successful")
        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {str(e)}")

class DeleteFileThread(QThread):
    operation_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            if os.path.isdir(self.file_path):
                os.rmdir(self.file_path)
            else:
                os.remove(self.file_path)
            self.operation_finished.emit(f"Successfully deleted: {self.file_path}")
        except Exception as e:
            self.error_occurred.emit(f"An error occurred while deleting: {e}")

class RenameFileThread(QThread):
    operation_finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, old_path, new_path):
        super().__init__()
        self.old_path = old_path
        self.new_path = new_path

    def run(self):
        try:
            os.rename(self.old_path, self.new_path)
            self.operation_finished.emit(f"Successfully renamed to: {self.new_path}")
        except Exception as e:
            self.error_occurred.emit(f"An error occurred while renaming: {e}")

class ImageLoadThread(QThread):
    image_loaded = pyqtSignal(QPixmap)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            pixmap = QPixmap(self.file_path)
            if pixmap.isNull():
                raise Exception("Failed to load image")
            self.image_loaded.emit(pixmap)
        except Exception as e:
            self.error_occurred.emit(f"An error occurred while loading the image: {e}")



class TodoApp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced TODO App")
        self.setGeometry(200, 200, 800, 600)

        self.tasks = []
        # Use QCoreApplication.applicationDirPath() to get the current directory
        self.todo_file = os.path.join(QCoreApplication.applicationDirPath(), "TODO.json")

        layout = QVBoxLayout()

        self.task_input = QLineEdit()
        layout.addWidget(QLabel("Task:"))
        layout.addWidget(self.task_input)

        self.priority_input = QComboBox()
        self.priority_input.addItems(["Low", "Medium", "High"])
        layout.addWidget(QLabel("Priority:"))
        layout.addWidget(self.priority_input)

        self.category_input = QLineEdit()
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_input)

        self.start_date_input = QLineEdit()
        layout.addWidget(QLabel("Start Date (YYYY-MM-DD):"))
        layout.addWidget(self.start_date_input)

        self.due_date_input = QLineEdit()
        layout.addWidget(QLabel("Due Date (YYYY-MM-DD):"))
        layout.addWidget(self.due_date_input)

        self.notes_input = QTextEdit()
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(self.notes_input)

        self.create_task_button = QPushButton("Create Task")
        self.create_task_button.clicked.connect(self.create_task)
        layout.addWidget(self.create_task_button)

        self.delete_task_button = QPushButton("Delete Selected Task")
        self.delete_task_button.clicked.connect(self.delete_task)
        layout.addWidget(self.delete_task_button)

        self.start_task_button = QPushButton("Start Selected Task")
        self.start_task_button.clicked.connect(self.start_task_timer)
        layout.addWidget(self.start_task_button)

        self.stop_task_button = QPushButton("Stop Selected Task")
        self.stop_task_button.clicked.connect(self.stop_task_timer)
        layout.addWidget(self.stop_task_button)

        self.task_list = QTreeWidget()
        self.task_list.setHeaderLabels(["Task", "Priority", "Category", "Start Date", "Due Date", "Time Spent (s)", "Progress"])
        self.task_list.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.task_list)

        self.setLayout(layout)

        self.load_tasks()
        self.timer = None

    def create_task(self):
        task_name = self.task_input.text().strip()
        priority = self.priority_input.currentText()
        category = self.category_input.text().strip()
        start_date = self.start_date_input.text().strip()
        due_date = self.due_date_input.text().strip()
        notes = self.notes_input.toPlainText().strip()

        if not task_name or not due_date:
            QMessageBox.warning(self, "Error", "Task name and due date are required.")
            return

        task = {
            "name": task_name,
            "priority": priority,
            "category": category,
            "start_date": start_date,
            "due_date": due_date,
            "notes": notes,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "completed": False,
            "progress": 0,
            "time_spent": 0,
            "subtasks": []
        }

        self.tasks.append(task)
        self.add_task_to_list(task)
        self.save_tasks()
        self.clear_inputs()

    def add_task_to_list(self, task):
        item = QTreeWidgetItem([
            task["name"], task["priority"], task["category"], task["start_date"],
            task["due_date"], str(task["time_spent"]), f'{task["progress"]}%'
        ])
        self.task_list.addTopLevelItem(item)

    def clear_inputs(self):
        self.task_input.clear()
        self.priority_input.setCurrentIndex(0)
        self.category_input.clear()
        self.start_date_input.clear()
        self.due_date_input.clear()
        self.notes_input.clear()

    def delete_task(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "No task selected.")
            return

        selected_item = selected_items[0]
        task_name = selected_item.text(0)

        self.tasks = [task for task in self.tasks if task["name"] != task_name]
        self.task_list.takeTopLevelItem(self.task_list.indexOfTopLevelItem(selected_item))
        self.save_tasks()

    def start_task_timer(self):
        selected_items = self.task_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Error", "No task selected.")
            return

        selected_item = selected_items[0]
        task_name = selected_item.text(0)

        if self.timer:
            QMessageBox.warning(self, "Error", "A task is already being timed.")
            return

        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.increment_time_spent(task_name))
        self.timer.start(1000)

    def stop_task_timer(self):
        if self.timer:
            self.timer.stop()
            self.timer = None
        else:
            QMessageBox.warning(self, "Error", "No task is currently being timed.")

    def increment_time_spent(self, task_name):
        for task in self.tasks:
            if task["name"] == task_name:
                task["time_spent"] += 1
                self.update_task_list_item(task)
                break

    def update_task_list_item(self, task):
        for i in range(self.task_list.topLevelItemCount()):
            item = self.task_list.topLevelItem(i)
            if item.text(0) == task["name"]:
                item.setText(5, str(task["time_spent"]))
                item.setText(6, f'{task["progress"]}%')
                break

    def load_tasks(self):
        if os.path.exists(self.todo_file):
            with open(self.todo_file, 'r') as f:
                self.tasks = json.load(f)

            for task in self.tasks:
                self.add_task_to_list(task)

    def save_tasks(self):
        with open(self.todo_file, 'w') as f:
            json.dump(self.tasks, f, indent=4)

    def update_task_progress(self, task_name, progress):
        for task in self.tasks:
            if task["name"] == task_name:
                task["progress"] = progress
                self.save_tasks()
                self.update_task_list_item(task)
                break

    def mark_task_complete(self, task_name):
        self.update_task_progress(task_name, 100)

    def update_due_date(self, task_name, new_due_date):
        for task in self.tasks:
            if task["name"] == task_name:
                task["due_date"] = new_due_date
                self.save_tasks()
                self.update_task_list_item(task)
                break

    def update_start_date(self, task_name, new_start_date):
        for task in self.tasks:
            if task["name"] == task_name:
                task["start_date"] = new_start_date
                self.save_tasks()
                self.update_task_list_item(task)
                break

class LoadTaskFileThread(QThread):
    tasks_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def __init__(self, todo_file):
        super().__init__()
        self.todo_file = todo_file

    def run(self):
        try:
            if os.path.exists(self.todo_file):
                with open(self.todo_file, 'r') as f:
                    tasks = json.load(f)
                self.tasks_loaded.emit(tasks)
            else:
                self.tasks_loaded.emit([])
        except Exception as e:
            self.error_occurred.emit(f"Error loading tasks: {str(e)}")

class SaveTaskFileThread(QThread):
    save_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, todo_file, tasks):
        super().__init__()
        self.todo_file = todo_file
        self.tasks = tasks

    def run(self):
        try:
            with open(self.todo_file, 'w') as f:
                json.dump(self.tasks, f, indent=4)
            self.save_completed.emit()
        except Exception as e:
            self.error_occurred.emit(f"Error saving tasks: {str(e)}")

class ConfigLoadThread(QThread):
    config_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            config = ConfigManager.load_config()
            self.config_loaded.emit(config)
        except Exception as e:
            self.error_occurred.emit(f"Error loading config: {str(e)}")

class ConfigSaveThread(QThread):
    save_completed = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            ConfigManager.save_config(self.config)
            self.save_completed.emit()
        except Exception as e:
            self.error_occurred.emit(f"Error saving config: {str(e)}")



class ProjectManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Manager")
        self.setGeometry(200, 200, 800, 600)
        self.setWindowIcon(QIcon("icon.png"))

        self.projects_root_dir = None
        self.current_tree_index = None
        self.file_model = CustomFileSystemModel()
        self.config = ConfigManager.load_config()
        self.context_menu = ContextMenu(self)

        self.initUI()
        self.load_project_root()  # Ensure this is defined before calling

    def initUI(self):
        self.create_menu_bar()

        layout = QVBoxLayout()

        self.set_root_button = QPushButton("Set Projects Root Directory")
        self.set_root_button.clicked.connect(self.set_root_directory)
        layout.addWidget(self.set_root_button)

        self.scan_untracked_button = QPushButton("Scan for Untracked Files")
        self.scan_untracked_button.clicked.connect(self.scan_for_untracked_files)
        layout.addWidget(self.scan_untracked_button)

        self.start_file_parsing_button = QPushButton("Start File Parsing")
        self.start_file_parsing_button.clicked.connect(self.start_file_parsing)
        layout.addWidget(self.start_file_parsing_button)

        self.project_name_label = QLabel("Project Name:")
        self.project_name_input = QLineEdit()
        layout.addWidget(self.project_name_label)
        layout.addWidget(self.project_name_input)

        self.project_type_label = QLabel("Project Type:")
        self.project_type_input = QComboBox()
        self.project_type_input.addItems(["python", "rust", "nodejs", "java", "csharp", "cpp", "go"])
        self.project_type_input.currentTextChanged.connect(self.update_placeholder_text)
        layout.addWidget(self.project_type_label)
        layout.addWidget(self.project_type_input)

        self.dependencies_label = QLabel("Dependencies (comma-separated):")
        self.dependencies_input = QTextEdit()
        layout.addWidget(self.dependencies_label)
        layout.addWidget(self.dependencies_input)

        self.create_project_button = QPushButton("Create Project")
        self.create_project_button.clicked.connect(self.create_project)
        layout.addWidget(self.create_project_button)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.project_tree = QTreeView()
        self.project_tree.setModel(self.file_model)
        self.project_tree.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.project_tree.setAnimated(True)
        self.project_tree.setIndentation(20)
        self.project_tree.setSortingEnabled(True)
        self.project_tree.clicked.connect(self.on_project_tree_clicked)
        self.project_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.project_tree.customContextMenuRequested.connect(self.open_context_menu)

        self.project_tree.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        splitter.addWidget(self.project_tree)

        layout.addWidget(splitter)
        layout.setStretchFactor(splitter, 1)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        #self.update_placeholder_text(self.project_type_input.currentText())

    def load_project_root(self):
        """Load the project root directory from the configuration."""
        if 'settings' in self.config and 'project_root' in self.config['settings']:
            self.projects_root_dir = self.config['settings']['project_root']
            self.file_model.setRootPath(self.projects_root_dir)
            self.project_tree.setRootIndex(self.file_model.index(self.projects_root_dir))
        else:
            QMessageBox.warning(self, "Error", "Project root directory is not set in the configuration.")

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('View')
        view_todo_action = QAction('View Todo', self)
        view_todo_action.triggered.connect(self.open_todo_window)
        view_menu.addAction(view_todo_action)

    def open_todo_window(self):
        """Method to open the TODO window."""
        todo_window = TodoApp(self)
        todo_window.exec()

    def start_file_parsing(self):
        if self.projects_root_dir:
            self.file_parsing_thread = FileTrackerThread(self.projects_root_dir)
            self.file_parsing_thread.tracker_finished.connect(self.on_tracker_finished)
            self.file_parsing_thread.start()
        else:
            QMessageBox.warning(self, "Error", "Project root directory is not set.")

    def scan_for_untracked_files(self):
        if self.projects_root_dir:
            self.file_tracker_thread = FileTrackerThread(self.projects_root_dir)
            self.file_tracker_thread.tracker_finished.connect(self.on_tracker_finished)
            self.file_tracker_thread.start()
        else:
            QMessageBox.warning(self, "Error", "Project root directory is not set.")

    def on_tracker_finished(self, message):
        QMessageBox.information(self, "Scan Complete", message)

    def set_root_directory(self):
        self.projects_root_dir = QFileDialog.getExistingDirectory(self, "Select Projects Root Directory")
        if self.projects_root_dir:
            self.file_model.setRootPath(self.projects_root_dir)
            self.project_tree.setRootIndex(self.file_model.index(self.projects_root_dir))

            if 'settings' not in self.config:
                self.config['settings'] = {}
            self.config['settings']['project_root'] = self.projects_root_dir
            ConfigManager.save_config(self.config)

    def on_project_tree_clicked(self, index):
        self.current_tree_index = index
        file_path = self.file_model.filePath(index)
        if os.path.isdir(file_path):
            print(f"Folder clicked: {file_path}")
        else:
            self.open_file_editor(file_path)

    def open_context_menu(self, position: QPoint):
        index = self.project_tree.indexAt(position)
        if not index.isValid():
            return

        file_path = self.file_model.filePath(index)
        menu = QMenu(self)

        compress_action = QAction("7-Zip to Backups", self)
        compress_action.triggered.connect(lambda: self.compress_to_7zip(file_path))
        menu.addAction(compress_action)

        set_working_action = QAction("Set as Working", self)
        set_working_action.triggered.connect(lambda: self.set_as_working(file_path))
        menu.addAction(set_working_action)

        git_add_action = QAction("Git Add", self)
        git_add_action.triggered.connect(lambda: self.context_menu.git_add(file_path))
        menu.addAction(git_add_action)

        git_commit_action = QAction("Git Commit", self)
        git_commit_action.triggered.connect(lambda: self.context_menu.git_commit(file_path))
        menu.addAction(git_commit_action)

        git_push_action = QAction("Git Push", self)
        git_push_action.triggered.connect(lambda: self.context_menu.git_push(file_path))
        menu.addAction(git_push_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_file_or_folder(file_path))
        menu.addAction(delete_action)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(lambda: self.rename_file_or_folder(file_path))
        menu.addAction(rename_action)

        menu.exec(self.project_tree.viewport().mapToGlobal(position))

    def delete_file_or_folder(self, file_path):
        try:
            if os.path.isdir(file_path):
                os.rmdir(file_path)
            else:
                os.remove(file_path)
            QMessageBox.information(self, "Delete", f"Successfully deleted: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Delete Error", f"An error occurred while deleting: {e}")

    def rename_file_or_folder(self, file_path):
        new_name, ok = QInputDialog.getText(self, "Rename", "Enter new name:")
        if ok and new_name:
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            try:
                os.rename(file_path, new_path)
                QMessageBox.information(self, "Rename", f"Successfully renamed to: {new_path}")
            except Exception as e:
                QMessageBox.critical(self, "Rename Error", f"An error occurred while renaming: {e}")

    def compress_to_7zip(self, file_path):
        project_dir = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        tracker_file = FileTracker.get_tracked_files(project_dir)

        if not tracker_file:
            QMessageBox.warning(self, "Error", f"Tracker file not found in {project_dir}")
            return

        backups_dir = os.path.join(project_dir, "backups")
        os.makedirs(backups_dir, exist_ok=True)

        version = VersionManager.generate_version(project_dir)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(backups_dir, f"{os.path.basename(project_dir)}_v{version}_{current_time}.7z")

        files_to_compress = [os.path.join(project_dir, file) for file in tracker_file]
        self.compression_thread = CompressionThread(files_to_compress, output_file)
        self.compression_thread.compression_finished.connect(self.show_information_message)
        self.compression_thread.error_occurred.connect(self.show_error_message)
        self.compression_thread.start()

    def set_as_working(self, file_path):
        project_dir = file_path if os.path.isdir(file_path) else os.path.dirname(file_path)
        tracker_file = FileTracker.get_tracked_files(project_dir)

        if not tracker_file:
            QMessageBox.warning(self, "Error", f"Tracker file not found in {project_dir}")
            return

        working_dir = os.path.join(project_dir, "working_versions")
        os.makedirs(working_dir, exist_ok=True)

        version = VersionManager.generate_version(project_dir, increment=True)
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(working_dir, f"{os.path.basename(project_dir)}_v{version}_{current_time}.7z")

        files_to_compress = [os.path.join(project_dir, file) for file in tracker_file]
        self.compression_thread = CompressionThread(files_to_compress, output_file)
        self.compression_thread.compression_finished.connect(self.show_information_message)
        self.compression_thread.error_occurred.connect(self.show_error_message)
        self.compression_thread.start()

    def open_file_editor(self, file_path):
        # Check if the file is an image
        if self.is_image(file_path):
            self.open_image_viewer(file_path)
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editing: {os.path.basename(file_path)}")
        dialog.setGeometry(300, 300, 800, 600)

        layout = QVBoxLayout(dialog)

        editor = QPlainTextEdit()

        # Load the file in a separate thread
        self.file_read_thread = FileReadWriteThread(file_path, 'read')
        self.file_read_thread.operation_finished.connect(lambda file_path, content: editor.setPlainText(content))
        self.file_read_thread.error_occurred.connect(self.show_error_message)
        self.file_read_thread.start()

        highlighter = PythonHighlighter(editor.document())

        layout.addWidget(editor)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(lambda: self.save_file(file_path, editor.toPlainText(), dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.exec()

    def is_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                return img.format is not None
        except IOError:
            return False

    def open_image_viewer(self, file_path):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Viewing: {os.path.basename(file_path)}")
        dialog.setGeometry(300, 300, 800, 600)

        layout = QVBoxLayout(dialog)

        label = QLabel()
        pixmap = QPixmap(file_path)
        label.setPixmap(pixmap)
        label.setScaledContents(True)

        layout.addWidget(label)

        dialog.exec()

    def save_file(self, file_path, content, dialog):
        # Save the file in a separate thread
        self.file_write_thread = FileReadWriteThread(file_path, 'write', content)
        self.file_write_thread.operation_finished.connect(lambda file_path, message: dialog.accept())
        self.file_write_thread.error_occurred.connect(self.show_error_message)
        self.file_write_thread.start()

    def create_project(self):
        project_name = self.project_name_input.text().strip()
        project_type = self.project_type_input.currentText().lower()
        dependencies = self.dependencies_input.toPlainText().split(',')
        dependencies = [dep.strip() for dep in dependencies if dep.strip()]

        if not project_name:
            QMessageBox.warning(self, "Error", "Please enter a project name.")
            return

        if not self.projects_root_dir:
            QMessageBox.warning(self, "Error", "Please set the projects root directory first!")
            return

        project_path = os.path.normpath(os.path.join(self.projects_root_dir, project_type, project_name))
        if os.path.exists(project_path):
            QMessageBox.warning(self, "Error", "Project already exists!")
        else:
            self.start_project_creation(project_path, project_type, dependencies)

    def start_project_creation(self, project_path, project_type, dependencies):
        self.project_thread = ProjectCreationThread(project_path, project_type, dependencies)
        self.project_thread.update_ui_signal.connect(self.on_project_created)
        self.project_thread.start()

    def on_project_created(self, message):
        QMessageBox.information(self, "Project Creation", message)
        if "created successfully" in message:
            self.start_file_monitoring()

    def start_file_monitoring(self):
        project_name = self.project_name_input.text().strip()
        project_type = self.project_type_input.currentText().lower()
        project_path = os.path.normpath(os.path.join(self.projects_root_dir, project_type, project_name))
        self.monitor_thread = FileMonitorThread(project_path)
        self.monitor_thread.start()

    def update_placeholder_text(self, project_type):
        placeholders = {
            'python': "Example: requests, flask, numpy",
            'rust': "Example: serde, rand, tokio",
            'nodejs': "Example: express, lodash, axios",
            'java': "Example: spring-boot-starter-web, junit, hibernate-core",
            'csharp': "Example: Newtonsoft.Json, Serilog, Dapper",
            'cpp': "Example: boost, fmt, spdlog",
            'go': "Example: gin, go-sql-driver/mysql, logrus"
        }
        self.dependencies_input.setPlaceholderText(placeholders.get(project_type, ""))


def main():
    app = QApplication(sys.argv)
    window = ProjectManagerUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

