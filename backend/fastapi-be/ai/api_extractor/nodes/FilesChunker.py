from ai.api_extractor.utils.chunker import chunk_all_backend_files
from ai.api_extractor.utils.batch_chunks import prepare_batches
from ai.api_extractor.utils.file_loader import delete_temp_repo
from typing import List, Dict, Optional
from ai.api_extractor.graph.GraphState import GraphState
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

def FilesChunkerNode(state: GraphState) -> GraphState:
    """Chunk backend files into code blocks and cleanup repo, update state."""
    backend_files = state.get('backend_files')

    if not backend_files:
        logger.warning("No files provided for chunking.")
        return state

    try:
        logger.info(f"Starting chunking of {len(backend_files)} backend files...")
        all_chunks = chunk_all_backend_files(files=backend_files, repo_path=state.get('repo_path'))
        logger.info(f"Chunked {len(all_chunks)} code blocks.")

        batches = prepare_batches(chunks=all_chunks)
        logger.info(f"Prepared {len(batches)} language-wise batches: {list(batches.keys())}")

        # Optionally store chunks
        # state['chunks'] = all_chunks
        # state['chunk_batches'] = batches

        repo_path = state.get('repo_path')
        if repo_path:
            logger.info(f"Cleaning up cloned repo from {repo_path}...")
            delete_temp_repo(repo_path)
            logger.info("Repo cleanup successful.")

        # Return updated state
        return {
            'chunks': all_chunks,
            'repo_path': None,
            'chunk_batches': batches
        }

    except Exception as e:
        logger.error(f"Error while chunking files: {e}")
        return state
