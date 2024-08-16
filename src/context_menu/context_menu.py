import os
import subprocess
from PyQt6.QtWidgets import QMenu, QMessageBox, QInputDialog
from PyQt6.QtGui import QAction
from PyQt6.QtCore import QPoint

class ContextMenu:
    def __init__(self, parent):
        self.parent = parent



    def git_add(self, file_path):
        if os.path.isdir(file_path):
            command = ["git", "add", "."]
        else:
            command = ["git", "add", file_path]

        self.run_git_command(command, file_path, "add")

    def git_commit(self, file_path):
        commit_message, ok = QInputDialog.getText(self.parent, 'Git Commit', 'Enter commit message:')
        if ok and commit_message:
            if os.path.isdir(file_path):
                command = ["git", "commit", "-m", commit_message]
            else:
                command = ["git", "commit", file_path, "-m", commit_message]

            self.run_git_command(command, file_path, "commit")

    def git_push(self, file_path):
        # Use "git push origin" to push the changes to the remote repository
        command = ["git", "push", "origin"]

        # You may need to specify the branch depending on your setup
        self.run_git_command(command, file_path, "push")

    def run_git_command(self, command, file_path, action):
        try:
            result = subprocess.run(command, cwd=os.path.dirname(file_path), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            QMessageBox.information(self.parent, f"Git {action.capitalize()}", f"Successfully executed git {action} on {file_path}")
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.decode('utf-8') if e.stderr else str(e)
            if "detected dubious ownership" in error_message:
                self.handle_dubious_ownership(file_path, error_message)
            else:
                self.handle_non_zero_exit_status(error_message, file_path, action)

    def handle_dubious_ownership(self, file_path, error_message):
        try:
            safe_directory = self.extract_directory_from_error(error_message)
            if safe_directory:
                subprocess.run(["git", "config", "--global", "--add", "safe.directory", safe_directory], check=True)
                QMessageBox.information(self.parent, "Git Safe Directory", f"Added {safe_directory} to the safe directories list.")
                # Retry the original git command after adding the safe directory
                self.run_git_command(["git", "add", "." if os.path.isdir(file_path) else file_path], file_path, "add")
            else:
                QMessageBox.critical(self.parent, "Git Safe Directory Error", "Could not extract the safe directory path from the error message.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self.parent, "Git Safe Directory Error", f"Failed to add safe directory: {str(e)}")

    def handle_non_zero_exit_status(self, error_message, file_path, action):
        if "returned a non-zero exit status 128" in error_message:
            QMessageBox.critical(self.parent, f"Git {action.capitalize()} Error", f"Git returned error 128 for {file_path}. This might be due to an issue with the repository. Error details: {error_message}")
        else:
            QMessageBox.critical(self.parent, f"Git {action.capitalize()} Error", f"An error occurred while executing git {action}: {error_message}")

    def extract_directory_from_error(self, error_message):
        try:
            start_index = error_message.find("safe.directory '") + len("safe.directory '")
            end_index = error_message.find("'", start_index)
            safe_directory = error_message[start_index:end_index]
            return safe_directory.strip()
        except:
            return None