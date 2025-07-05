import os
import shutil
import tempfile
from git import Repo
from typing import List, Dict,Optional
import stat

# from configs.logger import get_custom_logger

# logger = get_custom_logger(__name__)

BACKEND_EXTS = [".py", ".js", ".ts"]
API_HINTS = ["api", "endpoint", "route", "service", "controller"]

def clone_repo(repo_url: str, branch: Optional[str] = None) -> str:
    """Clone a Git repository to a temporary directory."""
    temp_dir = tempfile.mkdtemp(prefix="cloned_repo_")
    try:
        # logger.info(f"Cloning repository {repo_url} on branch {branch} to {temp_dir}")
        if branch:
            Repo.clone_from(repo_url, temp_dir, branch=branch)
        else:
            Repo.clone_from(repo_url, temp_dir)
        # logger.info(f"Successfully cloned repository to {temp_dir}")
        return temp_dir
    except Exception as e:
        print(f"Failed to clone repository {repo_url} on branch {branch}: {e}")
        # logger.error(f"Failed to clone repository {repo_url} on branch {branch}: {e}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise

def load_backend_files(repo_path: str) -> List[str]:
    """Load all backend files from the cloned repository."""
    backend_files = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.endswith(ext) for ext in BACKEND_EXTS):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                    language = (
                        "python" if file.endswith(".py") else
                        "javascript" if file.endswith(".js") else
                        "typescript" if file.endswith(".ts") else
                        "unknown"
                    )
                    is_api_file = any(hint in content.lower() for hint in API_HINTS)
                    backend_files.append({
                        "path": os.path.join(root, file),
                        "language": language,
                        "is_api_file": is_api_file,
                        "content": content
                    })
                except Exception as e:
                    print(f"Could not read file {file} in {root}: {e}")
                    # logger.error(f"Could not read file {file} in {root}: {e}")
    # logger.info(f"Found {len(backend_files)} backend files in {repo_path}")
    return backend_files

def handle_remove_readonly(func, path, exc_info):
    """
    Windows fix for deleting read-only or locked files (e.g. .git/index, .idx).
    """
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        print(f"Still failed to delete {path}: {e}")

def delete_temp_repo(path: str):
    """
    Deletes the temporary repo folder — handles Windows Git locks.
    """
    if os.path.exists(path):
        try:
            shutil.rmtree(path, onerror=handle_remove_readonly)
            print(f"Deleted temp repo folder: {path}")
        except Exception as e:
            print(f"Failed to delete {path}: {e}")
    else:
        print(f"Path does not exist: {path}")