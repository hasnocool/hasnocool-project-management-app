import os

class VersionManager:
    @staticmethod
    def generate_version(project_path, increment=False):
        version_file = os.path.join(project_path, "version.txt")

        if os.path.exists(version_file):
            with open(version_file, 'r') as f:
                version = f.read().strip()
        else:
            version = "1.0.0"  # Start with version 1.0.0

        if increment:
            version_parts = version.split('.')
            version_parts[2] = str(int(version_parts[2]) + 1)
            version = '.'.join(version_parts)

            with open(version_file, 'w') as f:
                f.write(version)

        return version
