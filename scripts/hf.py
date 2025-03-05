import os
import re
import subprocess
import shutil
from pathlib import Path


def update_version(app_path, version):
    """Update version in app.py"""
    with open(app_path, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(r'EK_VERSION = "[^"]+"', f'EK_VERSION = "{version}"', content)

    with open(app_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def print_tree(path, prefix=""):
    """Print directory structure in tree format"""
    if not os.path.isdir(path):
        return

    items = os.listdir(path)
    for i, item in enumerate(items):
        is_last = i == len(items) - 1
        print(f"{prefix}{'└──' if is_last else '├──'} {item}")
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print_tree(full_path, prefix + ("    " if is_last else "│   "))


def obfuscate_with_pyarmor(app_path):
    """Obfuscate app.py using pyarmor and replace the original file with obfuscated version"""
    app_dir = os.path.dirname(app_path)
    dist_dir = os.path.join(os.getcwd(), "dist")

    # Run pyarmor with explicit dist directory
    subprocess.run(["pyarmor", "gen", "--recursive", "--output", dist_dir, app_dir], check=True)

    print("Current directory structure:")
    print_tree(os.getcwd())

    if os.path.exists(dist_dir):
        # Get the obfuscated app.py from dist directory
        obfuscated_app = os.path.join(dist_dir, "hf", "app.py")
        runtime_dir = os.path.join(dist_dir, "pyarmor_runtime_000000")

        if os.path.exists(obfuscated_app) and os.path.exists(runtime_dir):
            # Replace original app.py with obfuscated version
            shutil.copy2(obfuscated_app, app_path)

            # Copy runtime directory to hf folder
            target_runtime_dir = os.path.join(app_dir, "pyarmor_runtime_000000")
            if os.path.exists(target_runtime_dir):
                shutil.rmtree(target_runtime_dir)
            shutil.copytree(runtime_dir, target_runtime_dir)

            # Clean up dist directory
            shutil.rmtree(dist_dir)
            return True
    return False


def main():
    # Get version from environment variable (set by GitHub Actions)
    version = os.environ.get("GITHUB_REF_NAME", "").lstrip("v")
    if not version:
        raise ValueError("Version not found in GITHUB_REF_NAME")

    # Paths
    hf_dir = Path("hf")
    app_path = hf_dir / "app.py"

    # Update version in app.py
    update_version(app_path, version)

    # Obfuscate app.py
    if not obfuscate_with_pyarmor(app_path):
        raise RuntimeError("Failed to obfuscate app.py")

    print(f"Successfully processed app.py with version {version}")


if __name__ == "__main__":
    main()
