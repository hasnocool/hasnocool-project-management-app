from PyQt6.QtCore import QThread, pyqtSignal
from project_creation.project_creator import ProjectCreator

class ProjectCreationThread(QThread):
    update_ui_signal = pyqtSignal(str)

    def __init__(self, project_path, project_type, dependencies):
        super().__init__()
        self.project_path = project_path
        self.project_type = project_type
        self.dependencies = dependencies

    def run(self):
        try:
            ProjectCreator.create_project_structure(self.project_path, self.project_type, self.dependencies)
            self.update_ui_signal.emit(f"Project '{self.project_path}' created successfully.")
        except Exception as e:
            self.update_ui_signal.emit(f"An error occurred: {e}")
