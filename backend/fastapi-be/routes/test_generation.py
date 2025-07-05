from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from db.get_mongo_client import get_mongo_client
from db.db_connection import MongoDBClient  

from ai.test_case_generation.tester import invoke_graph as invoke_test_graph

from models.TestGenerationRequest import TestGenerationRequest
from models.TestCase import TestCase

from configs.logger import get_custom_logger

router = APIRouter()

logger = get_custom_logger(__name__)

@router.post("/test-generation", summary="Test Generation", tags=["Test Generation"])
async def test_generation(payload: TestGenerationRequest, mongo_client: MongoDBClient = Depends(get_mongo_client)):
    """
    Test generation endpoint for validating the functionality of the API.
    
    Args:
        payload (TestGenerationRequest): Request payload containing necessary data.
    
    Returns:
        dict: A dictionary containing the test results.
    """
    data = payload.dict()
    logger.info(f"Received request for test generation: {data}")
    
    user_id = data.get("user_id")
    repo_url = data.get("repo_url") 
    branch = data.get("branch", None)
    
    if not repo_url:
            logger.warning("Request missing repository URL.")
            raise HTTPException(status_code=400, detail="Repository URL is required.")

    # Simulate some processing logic
    try:
        # Here you would typically call your test generation logic
        logger.info(f"Processing test generation for repo: {repo_url} (branch: {branch or 'default'})")
        endpoint_details = mongo_client.find_one("endpoints", {"repo_url": repo_url, "branch": branch})
        
        endpoints = endpoint_details.get("endpoints", []) if endpoint_details else []
        if not endpoints:
            logger.info("No endpoints found for the provided repository.")
            return JSONResponse(status_code=404, content={"message": "No endpoints found."})
        logger.info(f"Successfully retrieved {len(endpoints)} endpoints for test generation.")
        
        state = {
            "endpoints":endpoints
        }
        
        updated_state = await invoke_test_graph(state)
        print(updated_state.keys())
        # batches = updated_state.get("batched_endpoints",[])
        test_cases = updated_state.get("test_cases")
        
        # if not batches:
        #     return JSONResponse(status_code=400, content={"message":"No test cases formed"})
        # print(len(batches))
        # return JSONResponse(status_code=200, content={"user_id":user_id, "repo_url":repo_url,"branch":branch,"count":len(batches),"test_cases": batches})   
        
        if not test_cases:
            return JSONResponse(status_code=400, content={"message":"No test cases formed"})
        print(len(test_cases))
        return JSONResponse(status_code=200, content={"user_id":user_id, "repo_url":repo_url,"branch":branch,"count":len(test_cases),"test_cases": test_cases})   
    except Exception as e:
        logger.error(f"Error during test generation: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    

@router.post("/save-test-cases", summary="Save Generated Test Cases", tags=["Test Generation"])
def save_test_cases(payload: TestCase, mongo_client: MongoDBClient = Depends(get_mongo_client)):
    """
    Save LLM-generated test cases to the database.
    Args:
        payload (TestCase): Contains user_id, repo_url, branch, and generated test_cases.
    Returns:
        JSONResponse with save status.
    """
    data = payload.dict()
    user_id = data.get("user_id")
    repo_url = data.get("repo_url")
    branch = data.get("branch", None)

    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required.")

    logger.info(f"Saving test cases for repo: {repo_url}, branch: {branch}, user: {user_id}")

    query = {
        "repo_url": repo_url,
        "branch": branch,
    }
    if user_id:
        query["user_id"] = user_id

    try:
        result = mongo_client.update_one(
            collection="test_cases",
            query=query,
            update=data,
            upsert=True
        )

        logger.info(f"Test cases {'updated' if result.modified_count else 'inserted'} for {repo_url}")
        return JSONResponse(status_code=200, content={"message": "Test cases saved successfully."})
    
    except Exception as e:
        logger.error(f"Error saving test cases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save test cases: {str(e)}")
