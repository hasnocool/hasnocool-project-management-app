import os
import sys
import subprocess
from file_monitoring.file_tracker import FileTracker
from datetime import datetime

class ProjectCreator:
    @staticmethod
    def create_common_files(project_name, dependencies=None):
        try:
            creation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            version = "1.0.0"
            dependency_list = ', '.join(dependencies) if dependencies else "None"

            files = {
                "README.md": f"# {project_name}\n\n**Project Creation Date**: {creation_date}\n\n**Current Version**: {version}\n\n**Dependencies**: {dependency_list}\n\nA new project initialized using the project setup script.\n",
                "CHANGELOG.md": "# Changelog\n\nAll notable changes to this project will be documented in this file.\n",
                "LICENSE": "MIT License\n\nYour license text here.\n",
                ".gitignore": ".venv/\n__pycache__/\nnode_modules/\n*.log\n.env\n"
            }

            for filename, content in files.items():
                file_path = os.path.join(project_name, filename)
                with open(file_path, 'w') as f:
                    f.write(content)
                FileTracker.track_file(project_name, file_path)

        except Exception as e:
            print(f"Error creating common files: {e}")

    @staticmethod
    def create_python_project(project_name, dependencies):
        try:
            print(f"Initializing Python project: {project_name}")
            os.makedirs(os.path.join(project_name, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "tests"), exist_ok=True)

            subprocess.run([sys.executable, "-m", "venv", os.path.join(project_name, ".venv")], check=True)

            files = {
                "src/main.py": '''if __name__ == "__main__":\n    print("Hello, Python World!")\n''',
                "requirements.txt": '\n'.join(dependencies)
            }

            for filepath, content in files.items():
                full_path = os.path.join(project_name, filepath)
                with open(full_path, 'w') as f:
                    f.write(content)
                FileTracker.track_file(project_name, full_path)

            if dependencies:
                subprocess.run([os.path.join(project_name, ".venv", "Scripts", "pip"), "install"] + dependencies, check=True)

            ProjectCreator.create_common_files(project_name, dependencies)
            subprocess.run(["git", "init", project_name], check=True)
            print(f"Python project '{project_name}' created successfully with dependencies: {dependencies}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the Python project setup: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def create_rust_project(project_name, dependencies):
        try:
            print(f"Initializing Rust project: {project_name}")
            os.makedirs(project_name, exist_ok=True)

            subprocess.run(["cargo", "init", project_name], check=True)

            if dependencies:
                subprocess.run(["cargo", "add"] + dependencies, check=True)

            ProjectCreator.create_common_files(project_name, dependencies)
            subprocess.run(["git", "init", project_name], check=True)
            print(f"Rust project '{project_name}' created successfully with dependencies: {dependencies}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the Rust project setup: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def create_nodejs_project(project_name, dependencies):
        try:
            print(f"Initializing Node.js project: {project_name}")
            os.makedirs(os.path.join(project_name, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "tests"), exist_ok=True)

            subprocess.run(["npm", "init", "-y"], cwd=project_name, check=True)

            files = {
                "src/index.js": '''console.log("Hello, Node.js World!");\n'''
            }

            for filepath, content in files.items():
                full_path = os.path.join(project_name, filepath)
                with open(full_path, 'w') as f:
                    f.write(content)
                FileTracker.track_file(project_name, full_path)

            if dependencies:
                subprocess.run(["npm", "install"] + dependencies, cwd=project_name, check=True)

            ProjectCreator.create_common_files(project_name, dependencies)
            subprocess.run(["git", "init", project_name], check=True)
            print(f"Node.js project '{project_name}' created successfully with dependencies: {dependencies}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the Node.js project setup: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def create_java_project(project_name, dependencies):
        try:
            print(f"Initializing Java project: {project_name}")
            os.makedirs(os.path.join(project_name, "src", "main", "java", project_name), exist_ok=True)
            os.makedirs(os.path.join(project_name, "src", "test", "java", project_name), exist_ok=True)

            main_java_file = os.path.join(project_name, "src", "main", "java", project_name, f"{project_name}.java")
            with open(main_java_file, 'w') as f:
                f.write(f'''public class {project_name} {{\n    public static void main(String[] args) {{\n        System.out.println("Hello, Java World!");\n    }}\n}}\n''')
            FileTracker.track_file(project_name, main_java_file)

            # Note: Java dependencies are usually managed via Maven or Gradle.
            if dependencies:
                print(f"Please add these dependencies to your Maven/Gradle configuration: {dependencies}")

            ProjectCreator.create_common_files(project_name, dependencies)
            subprocess.run(["git", "init", project_name], check=True)
            print(f"Java project '{project_name}' created successfully with dependencies: {dependencies}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the Java project setup: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def create_csharp_project(project_name, dependencies):
        try:
            print(f"Initializing C# project: {project_name}")
            os.makedirs(os.path.join(project_name, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "tests"), exist_ok=True)

            subprocess.run(["dotnet", "new", "console", "-o", os.path.join(project_name, "src")], check=True)

            if dependencies:
                subprocess.run(["dotnet", "add", os.path.join(project_name, "src"), "package"] + dependencies, check=True)

            ProjectCreator.create_common_files(project_name, dependencies)
            subprocess.run(["git", "init", project_name], check=True)
            print(f"C# project '{project_name}' created successfully with dependencies: {dependencies}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the C# project setup: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def create_cpp_project(project_name, dependencies):
        try:
            print(f"Initializing C++ project: {project_name}")
            os.makedirs(os.path.join(project_name, "src"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "include"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "tests"), exist_ok=True)

            main_cpp_file = os.path.join(project_name, "src", "main.cpp")
            with open(main_cpp_file, 'w') as f:
                f.write('''#include <iostream>\n\nint main() {\n    std::cout << "Hello, C++ World!" << std::endl;\n    return 0;\n}\n''')
            FileTracker.track_file(project_name, main_cpp_file)

            if dependencies:
                print(f"Please add these dependencies using your package manager: {dependencies}")

            ProjectCreator.create_common_files(project_name, dependencies)
            subprocess.run(["git", "init", project_name], check=True)
            print(f"C++ project '{project_name}' created successfully with dependencies: {dependencies}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the C++ project setup: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def create_go_project(project_name, dependencies):
        try:
            print(f"Initializing Go project: {project_name}")
            os.makedirs(os.path.join(project_name, "cmd"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "pkg"), exist_ok=True)
            os.makedirs(os.path.join(project_name, "internal"), exist_ok=True)

            main_go_file = os.path.join(project_name, "cmd", "main.go")
            with open(main_go_file, 'w') as f:
                f.write('''package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, Go World!");\n}\n''')
            FileTracker.track_file(project_name, main_go_file)

            if dependencies:
                subprocess.run(["go", "get"] + dependencies, check=True)

            ProjectCreator.create_common_files(project_name, dependencies)
            subprocess.run(["git", "init", project_name], check=True)
            print(f"Go project '{project_name}' created successfully with dependencies: {dependencies}")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the Go project setup: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    @staticmethod
    def create_project_structure(project_path, project_type, dependencies):
        if project_type == 'python':
            ProjectCreator.create_python_project(project_path, dependencies)
        elif project_type == 'rust':
            ProjectCreator.create_rust_project(project_path, dependencies)
        elif project_type == 'nodejs':
            ProjectCreator.create_nodejs_project(project_path, dependencies)
        elif project_type == 'java':
            ProjectCreator.create_java_project(project_path, dependencies)
        elif project_type == 'csharp':
            ProjectCreator.create_csharp_project(project_path, dependencies)
        elif project_type == 'cpp':
            ProjectCreator.create_cpp_project(project_path, dependencies)
        elif project_type == 'go':
            ProjectCreator.create_go_project(project_path, dependencies)
        else:
            raise ValueError(f"Unsupported project type: {project_type}")
