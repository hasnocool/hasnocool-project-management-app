import os
import json
import fnmatch

class FileTracker:
    ignore_next_update = False
    tracker_file_name = "file_tracker.json"

    # Patterns for files and directories to be ignored
    ignored_patterns = [
        '*.pyc', '*.pyo', '*.pyd', '__pycache__', '.git', '.venv', 'node_modules', '.DS_Store',
        '*.log', '*.tmp', '*.swp', '*.bak', '*.old', '*.pid', '.idea', '*.iml', '.vscode',
    ]

    @staticmethod
    def track_file(project_name, file_path):
        if FileTracker.ignore_next_update:
            FileTracker.ignore_next_update = False
            return

        if FileTracker._matches_any_pattern(file_path):
            # Skip tracking for ignored files or directories
            return

        tracker_file = os.path.join(project_name, FileTracker.tracker_file_name)
        tracked_files = []

        if os.path.exists(tracker_file):
            with open(tracker_file, 'r') as f:
                try:
                    tracked_files = json.load(f)
                except json.JSONDecodeError:
                    # If JSON is invalid, recreate the file
                    print(f"Invalid JSON detected in {tracker_file}. Recreating the file.")
                    tracked_files = []

        relative_path = os.path.relpath(file_path, project_name)
        if relative_path not in tracked_files:
            tracked_files.append(relative_path)

        FileTracker.ignore_next_update = True
        with open(tracker_file, 'w') as f:
            json.dump(tracked_files, f, indent=4)

    @staticmethod
    def get_tracked_files(directory):
        tracker_file = os.path.join(directory, FileTracker.tracker_file_name)
        if os.path.exists(tracker_file):
            with open(tracker_file, 'r') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    # If JSON is invalid and not an ignored directory, recreate the file
                    if not FileTracker._matches_any_pattern(directory):
                        print(f"Invalid JSON detected in {tracker_file}. Recreating the file.")
                    return []
        return None

    @staticmethod
    def scan_and_track_untracked_files(project_root_dir):
        for root, dirs, files in os.walk(project_root_dir):
            # Filter out directories that match ignored patterns
            dirs[:] = [d for d in dirs if not FileTracker._matches_any_pattern(d)]
            # Generate or update the file_tracker.json for the current directory
            if not FileTracker._matches_any_pattern(root):
                FileTracker._generate_or_update_tracker(root, files)

    @staticmethod
    def _generate_or_update_tracker(directory, files):
        tracker_file = os.path.join(directory, FileTracker.tracker_file_name)
        tracked_files = FileTracker.get_tracked_files(directory) or []

        for filename in files:
            if not FileTracker._matches_any_pattern(filename):
                relative_path = os.path.relpath(os.path.join(directory, filename), directory)
                if relative_path not in tracked_files:
                    tracked_files.append(relative_path)

        with open(tracker_file, 'w') as f:
            json.dump(tracked_files, f, indent=4)

    @staticmethod
    def _matches_any_pattern(path):
        """Check if a file or directory matches any of the ignored patterns."""
        for pattern in FileTracker.ignored_patterns:
            if fnmatch.fnmatch(path, pattern) or any(fnmatch.fnmatch(part, pattern) for part in path.split(os.path.sep)):
                return True
        return False
