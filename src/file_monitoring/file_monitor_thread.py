import os
from PyQt6.QtCore import QThread
from watchdog.observers import Observer
from file_monitoring.file_change_handler import FileChangeHandler

class FileMonitorThread(QThread):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path

    def run(self):
        normalized_project_path = os.path.normpath(self.project_path)
        if not os.path.exists(normalized_project_path):
            print(f"Cannot start monitoring. The directory {normalized_project_path} does not exist.")
            return

        event_handler = FileChangeHandler(normalized_project_path)
        observer = Observer()
        observer.schedule(event_handler, normalized_project_path, recursive=True)
        observer.start()
        print(f"Started monitoring project: {normalized_project_path}")

        try:
            while observer.is_alive():
                observer.join(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
