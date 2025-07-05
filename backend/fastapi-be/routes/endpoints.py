from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from db.get_mongo_client import get_mongo_client
from db.db_connection import MongoDBClient

from models.EndpointsRequest import EndpointRequest
from models.SaveEndpoints import SaveEndpoint

from ai.api_extractor.main import invoke_graph

from configs.logger import get_custom_logger

logger = get_custom_logger(__name__)
router = APIRouter()

@router.post("/get-endpoints", summary="Get API Endpoints", tags=["API"])
async def get_api_endpoints(payload: EndpointRequest):
    """
    Get API endpoints from the backend codebase.

    Args:
        payload (EndpointsRequest): Request payload containing repo URL and optional branch.

    Returns:
        dict: A dictionary containing the extracted API endpoints.
    """
    data = payload.dict()
    repo_url = data.get("repo_url")
    branch = data.get("branch", None)

    if not repo_url:
        logger.warning("Request missing repository URL.")
        raise HTTPException(status_code=400, detail="Repository URL is required.")

    logger.info(f"Received request to extract endpoints from repo: {repo_url} (branch: {branch or 'default'})")

    state = {
        "repo_url": repo_url
    }
    if branch:
        state["branch"] = branch

    try:
        updated_state = await invoke_graph(state)
        endpoints = updated_state.get("endpoints", [])

        if not endpoints:
            logger.info("No endpoints found after graph invocation.")
            return JSONResponse(status_code=404, content={"message": "No endpoints found."})

        logger.info(f"Successfully extracted {len(endpoints)} endpoints.")
        collection_lengths ={}
        for group_name, group in endpoints.items():
            collection_lengths[group_name] = len(group)
        return JSONResponse(status_code=200, content={"user_id":None, "repo_url":updated_state.get("repo_url"), "branch":updated_state.get("branch",None) ,"count":len(endpoints),"group_count":collection_lengths,"endpoints": endpoints})

    except Exception as e:
        logger.error(f"Error processing /get-endpoints: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")



@router.post("/save-endpoints", summary="Save API Endpoints", tags=["API"])
def save_api_endpoints(payload: SaveEndpoint, mongo_client: MongoDBClient = Depends(get_mongo_client)):
    """
    Save or update API endpoints in the database.
    If a document with matching repo_url (+ optional branch/user_id) exists, update it. Else, insert new.
    """
    data = payload.dict()
    logger.info(f"Received request to save endpoints")

    if not data.get("repo_url"):
        logger.warning("Request missing repository URL.")
        raise HTTPException(status_code=400, detail="Repository URL is required.")

    try:
        # Build the query with only available fields
        query = {"repo_url": data["repo_url"]}
        if data.get("branch"):
            query["branch"] = data["branch"]
        if data.get("user_id"):
            query["user_id"] = data["user_id"]


        result = mongo_client.update_one(
            collection="endpoints",
            query=query,
            update=data,
            upsert=True
        )

        action = "updated" if result.matched_count > 0 else "inserted"
        logger.info(f"Endpoints {action} successfully for repo: {data['repo_url']}")

        return JSONResponse(
            status_code=200,
            content={
                "message": f"Endpoints {action} successfully.",
                "repo_url": data["repo_url"],
                "branch": data.get("branch"),
                "user_id": data.get("user_id")
            }
        )

    except Exception as e:
        logger.error(f"Error saving endpoints: {e}")
        raise HTTPException(status_code=500, detail=f"Error saving endpoints: {str(e)}")
    
    
    
    
    
    