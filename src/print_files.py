import os

def print_file_contents(directory, script_name):
    for root, dirs, files in os.walk(directory):
        # Skip the __pycache__, .git directories, and the script itself
        dirs[:] = [d for d in dirs if d not in ('__pycache__', '.git')]
        
        for filename in files:
            # Skip binary files like .pyc, .git files, .gitattributes, the script itself, and other .md files except README.md or readme.md
            if (filename.endswith('.pyc') or
                filename in ('.git', '.gitattributes', script_name) or
                (filename.endswith('.md') and filename.lower() not in ('readme.md'))):
                continue

            # Get the full path of the file
            filepath = os.path.join(root, filename)
            
            # Print the filename
            print(f"\n{'='*40}\nFile: {filepath}\n{'='*40}")
            
            # Print the contents of the file
            try:
                with open(filepath, 'r') as file:
                    print(file.read())
            except Exception as e:
                print(f"Could not read {filepath}. Error: {e}")

if __name__ == "__main__":
    # Define the directory containing your project files
    project_directory = '.'  # Update this to the correct path if necessary
    
    # Define the script's filename (this file)
    script_name = 'print_files.py'  # Update this if the script has a different name
    
    # Print the contents of each file in the directory
    print_file_contents(project_directory, script_name)
