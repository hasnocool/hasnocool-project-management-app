from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject
import os
import csv

class SizeCalculationWorker(QObject):
    size_calculated = pyqtSignal(str, int)

    def calculate_size(self, file_info):
        file_path = file_info.absoluteFilePath()

        if file_info.isDir():
            size = self.calculate_dir_size(file_path)
        else:
            size = file_info.size()

        self.size_calculated.emit(file_path, size)

    def calculate_dir_size(self, dir_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        return total_size


class CustomFileSystemModel(QFileSystemModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ignored_dirs = ['.venv', '.git']
        self.size_data = {}
        self.csv_file_path = "file_sizes.csv"
        self.load_size_data()

        self.worker_thread = QThread()
        self.worker = SizeCalculationWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker.size_calculated.connect(self.on_size_calculated)
        self.worker_thread.start()

    def filterAcceptsRow(self, source_row, source_parent):
        index = self.index(source_row, 0, source_parent)
        if index.isValid():
            file_info = self.fileInfo(index)
            if self.is_ignored(file_info):
                return False
        return super().filterAcceptsRow(source_row, source_parent)

    def is_ignored(self, file_info):
        if file_info.isDir():
            if file_info.fileName() in self.ignored_dirs:
                return True
            dir_path = file_info.absoluteFilePath()
            for dir_name in dir_path.split(os.path.sep):
                if dir_name in self.ignored_dirs:
                    return True
        return False

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 1:  # Assuming the "Size" column is column 1
                file_info = self.fileInfo(index)
                file_path = file_info.absoluteFilePath()

                # Check if the size is already known
                if file_path in self.size_data:
                    return self.human_readable_size(self.size_data[file_path])

                # If size is not known, start calculation in a separate thread
                self.worker.calculate_size(file_info)
                return "Calculating..."

        return super().data(index, role)

    def on_size_calculated(self, file_path, size):
        self.size_data[file_path] = size
        self.save_size_data()
        self.layoutChanged.emit()  # Notify the view that data has changed

    def human_readable_size(self, size, decimal_places=2):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.{decimal_places}f} {unit}"
            size /= 1024.0
        return f"{size:.{decimal_places}f} TB"

    def load_size_data(self):
        if os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.size_data[row['path']] = int(row['size'])

    def save_size_data(self):
        with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['path', 'size'])
            writer.writeheader()
            for path, size in self.size_data.items():
                writer.writerow({'path': path, 'size': size})
