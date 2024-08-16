from watchdog.events import FileSystemEventHandler
from file_monitoring.file_tracker import FileTracker
import os

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, project_name):
        self.project_name = project_name
        self.tracker_file = os.path.join(project_name, "file_tracker.json")

    def on_modified(self, event):
        if not event.is_directory:
            if event.src_path == self.tracker_file:
                # Ignore modifications to the tracker file itself
                return
            print(f"File modified: {event.src_path}")
            FileTracker.track_file(self.project_name, event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            if event.src_path == self.tracker_file:
                # Ignore creations of the tracker file itself
                return
            print(f"File created: {event.src_path}")
            FileTracker.track_file(self.project_name, event.src_path)
