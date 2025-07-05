from ai.api_extractor.utils.file_loader import clone_repo, load_backend_files, delete_temp_repo
from ai.api_extractor.utils.chunker import chunk_all_backend_files
from typing import List, Dict, Optional
from graph.graph import create_graph
# from configs.logger import get_custom_logger

# logger = get_custom_logger(__name__)

def load_files():
    repo_url = "https://github.com/tiangolo/full-stack-fastapi-postgresql"
    branch = "master"
    try:
        # logger.info(f"Cloning repository {repo_url} on branch {branch}")
        repo_path = clone_repo(repo_url, branch)
        
        # logger.info(f"Loading backend files from {repo_path}")
        backend_files = load_backend_files(repo_path)
        print(f"Backend Files: {len(backend_files)}")
        # logger.info(f"Loaded {len(backend_files)} backend files successfully.")
        return repo_path,backend_files
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        # logger.error(f"An error occurred: {e}")

def chunk_backend_files(repo_path:str, backend_files:List[Dict]) -> List[Dict]:
    """
    Process and chunk backend files.
    """
    if not repo_path or not backend_files:
        print("No repository path or backend files to process.")
        return

    # logger.info(f"Processing {len(backend_files)} backend files in {repo_path}")
   
    try:
        # logger.info(f"Chunking file: {file_obj['path']}")
        all_chunks = chunk_all_backend_files(backend_files)
        # logger.info(f"Chunked {len(all_chunks)} code blocks from {len(backend_files)} files.")
        print(f"Chunked {len(all_chunks)} code blocks from {len(backend_files)} files.")
        return all_chunks
    except Exception as e:
        print(f"Error chunking files: {e}")
        

# repo_path,backend_files=load_files()
# all_chunks = chunk_backend_files(repo_path, backend_files)
# print(f"Sample Chunk: {all_chunks[20] if all_chunks else 'No chunks available'}")
# if repo_path:
#     delete_temp_repo(repo_path)