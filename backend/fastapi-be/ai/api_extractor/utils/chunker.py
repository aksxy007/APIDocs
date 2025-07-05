import ast
import re
from typing import List, Dict
import os

def chunk_python_file_by_function(file_obj: Dict,repo_path:str) -> List[Dict]:
    chunks = []
    content = file_obj["content"]
    file_path = file_obj["path"]
    relative_path = os.path.relpath(file_path, start=repo_path)


    try:
        tree = ast.parse(content)
        lines = content.splitlines()

        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                start_line = node.lineno - 1
                next_index = tree.body.index(node) + 1
                end_line = tree.body[next_index].lineno - 2 if next_index < len(tree.body) else len(lines) - 1
                chunk_code = "\n".join(lines[start_line:end_line + 1])
                chunks.append({
                    "file_name": relative_path,
                    "function_name": node.name,
                    "code": chunk_code,
                    "start_line": start_line + 1,
                    "end_line": end_line + 1,
                    "language": "python"
                })

    except Exception as e:
        print(f"⚠️ Error chunking {file_path}: {e}")

    return chunks


def chunk_javascript_functions(file_obj: Dict,repo_path:str) -> List[Dict]:
    """
    Rough chunking of JS/TS files per API or function block.
    Looks for: app.get/post/put/delete, function xyz(), async function xyz()
    """
    chunks = []
    content = file_obj["content"]
    file_path = file_obj["path"]
    lines = content.splitlines()
    relative_path = os.path.relpath(file_path, start=repo_path)

    # Match Express-style route definitions or traditional functions
    pattern = re.compile(r"""(?x)
        ^\s*(?:export\s+)?        # optional export
        (?:
            (?:async\s+)?function\s+(\w+)\s*\( |  # named functions
            (app|router)\.(get|post|put|delete|patch)\s*\(  # express routes
        )
    """)

    start_idx = None
    current_chunk = []
    function_name = "unknown"

    for idx, line in enumerate(lines):
        if match := pattern.match(line):
            # Save previous chunk
            if current_chunk:
                chunks.append({
                    "file_name": relative_path,
                    "function_name": function_name,
                    "code": "\n".join(current_chunk),
                    "start_line": start_idx + 1,
                    "end_line": idx,
                    "language": file_obj["language"]
                })
                current_chunk = []

            start_idx = idx
            current_chunk = [line]

            function_name = match.group(1) or f"{match.group(2)}.{match.group(3)}"

        elif current_chunk:
            current_chunk.append(line)

    # Add last chunk
    if current_chunk:
        chunks.append({
            "file_name": relative_path,
            "function_name": function_name,
            "code": "\n".join(current_chunk),
            "start_line": start_idx + 1,
            "end_line": len(lines),
            "language": file_obj["language"]
        })

    return chunks


def chunk_all_backend_files(files: List[Dict], repo_path:str) -> List[Dict]:
    all_chunks = []

    for file in files:
        if file["language"] == "python" and file["is_api_file"]:
            all_chunks.extend(chunk_python_file_by_function(file,repo_path))

        elif file["language"] in ["javascript", "typescript"] and file["is_api_file"]:
            all_chunks.extend(chunk_javascript_functions(file,repo_path))

    return all_chunks
