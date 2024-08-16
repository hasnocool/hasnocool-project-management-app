import os
import sys
import shutil
import tempfile
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QPoint  # Add QPoint here
from PyQt6.QtGui import QPixmap, QImage, QPainter, QColor, QFont

def load_script_to_ram(script_path):
    with open(script_path, 'r') as file:
        return file.read()

def copy_to_temp_and_import(script_path):
    temp_dir = tempfile.mkdtemp()
    temp_script_path = os.path.join(temp_dir, os.path.basename(script_path))
    shutil.copy2(script_path, temp_script_path)

    # Add the temp directory to sys.path
    sys.path.insert(0, temp_dir)

    # Import the module
    module_name = os.path.splitext(os.path.basename(script_path))[0]
    return __import__(module_name)

def main():
    script_path = r"X:\_PM_APP_DATA\python\project_management_app\src\ui\project_manager_ui.py"

    # Load and execute the script content
    script_content = load_script_to_ram(script_path)

    # Create a new namespace for execution
    namespace = {}

    # Include necessary imports in the namespace
    namespace['QThread'] = QThread
    namespace['pyqtSignal'] = pyqtSignal
    namespace['QApplication'] = QApplication
    namespace['QPixmap'] = QPixmap
    namespace['QImage'] = QImage
    namespace['QPainter'] = QPainter
    namespace['QColor'] = QColor
    namespace['QFont'] = QFont
    namespace['QPoint'] = QPoint  # Add QPoint to the namespace
    # Add any other imports that might be required by the script

    # Execute the script content in the provided namespace
    exec(script_content, namespace)

    # Retrieve the main class or function from the executed script
    ProjectManagerUI = namespace.get('ProjectManagerUI')

    if ProjectManagerUI is None:
        raise ValueError("ProjectManagerUI class was not found in the script.")

    # Initialize and run the application
    app = QApplication(sys.argv)
    window = ProjectManagerUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
