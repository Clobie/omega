import os
import ast
import subprocess

def find_python_files(directory):
    py_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))
    return py_files

def extract_imports(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            tree = ast.parse(file.read(), filename=file_path)
            return {node.names[0].name for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)}
    except (UnicodeDecodeError, FileNotFoundError):
        print(f"Could not read file: {file_path}")
        return set()

def is_package_installable(package):
    try:
        subprocess.run(['pip', 'install', package], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    current_directory = os.getcwd()
    all_imports = set()
    
    for py_file in find_python_files(current_directory):
        all_imports.update(extract_imports(py_file))

    installable = []
    not_installable = []

    for imp in sorted(all_imports):
        if is_package_installable(imp):
            installable.append(imp)
        else:
            not_installable.append(imp)

    print("\nInstallable Packages:")
    for imp in installable:
        print(imp)

    print("\nNot Installable Packages:")
    for imp in not_installable:
        print(imp)

if __name__ == "__main__":
    main()