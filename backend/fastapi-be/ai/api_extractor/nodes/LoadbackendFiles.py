from ai.api_extractor.utils.file_loader import clone_repo, load_backend_files
from ai.api_extractor.graph.GraphState import GraphState
from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)

def LoadBackendFilesNode(state: GraphState) -> GraphState:
    """Clone repo and load backend files, update state."""

    repo_url = state.get("repo_url")
    branch = state.get("branch")

    if not repo_url:
        logger.error("No repository URL provided in the state.")
        return None

    if state.get("repo_path"):
        logger.info(f"Repository already cloned at: {state.get('repo_path')}")
        return state

    try:
        logger.info(f"Cloning repository: {repo_url} (branch: {branch or 'default'})...")
        repo_path = clone_repo(repo_url=repo_url, branch=branch)
        logger.info(f"Repo cloned successfully to: {repo_path}")
    except Exception as e:
        logger.error(f"Failed to clone repo: {e}")
        return None

    backend_files = load_backend_files(repo_path)
    logger.info(f"Loaded {len(backend_files)} backend files from cloned repo.")

    if not backend_files:
        logger.warning("No backend files detected in the repo.")

    return {
        "backend_files": backend_files,
        "repo_path": repo_path
    }
