from typing import List, Dict

def get_fastapi_extraction_prompt(batch: List[Dict]) -> str:
    code_blocks = "\n\n".join([f"# File: {chunk['file_name']}\n{chunk['code']}" for chunk in batch])
    prompt = f"""
You are an expert in reading and understanding FastAPI backend code.

From the following code chunks, extract all FastAPI API endpoints and return them as a **JSON list**, formatted like OpenAPI-style schemas.

Each endpoint must include:
- path: API path string (e.g., "/users/{{user_id}}")
- method: HTTP method (GET, POST, etc.)
- handler: Function name (e.g., "get_user")
- file: Filename or relative path
- params: List of parameter objects. Each param must have:
  - name: Param name
  - in: "query", or "body"
  - required: true or false
  - type: "string", "int", "boolean", etc.
- summary: A two-line summary (15-20 words) describing what the API does, including any database or CRUD actions.
- responses: A dictionary of status codes to their details:
  - description: Short explanation of the response
  - content_type: Typically "application/json"
  - response: An example response body with field names and types
Each endpoint must also include:
- operation (one of: "create", "read", "update", "delete", or "other")

Use the function body or summary to infer the operation.  
If it's a POST/PUT that writes to the DB, it's probably "create" or "update".  
If it's a GET with query/path param, it's likely "read" or "list" for getting list of data.  
If it's a DELETE call, it's "delete".  
If it performs login/auth/email logic, use "other".



Output only a JSON list. No markdown, explanations, or extra formatting.Always use ```json <JSON content> ``` for json response

Example:
```json
[
  {{
    "path": "/users/{{user_id}}",
    "method": "GET",
    "handler": "get_user",
    "file": "routes/users.py",
    "params": [
      {{
        "name": "user_id",
        "in": "query",
        "required": true,
        "type": "int",
        "description": "User ID to fetch"
      }}
    ],
    "summary": "Fetches a user by ID from the database.",
    "operation": "read", 
    "responses": {{
      "200": {{
        "description": "User found",
        "content_type": "application/json",
        "response": {{
          "id": "int",
          "name": "string",
          "email": "string"
        }}
      }},
      "404": {{
        "description": "User not found",
        "content_type": "application/json",
        "response": {{
          "detail": "string"
        }}
      }}
    }}
  }}
]
```

Example:
-When no endpoints found.

```json
[]
```

Here is the code block:
{code_blocks}
    
    """
    
    return prompt.strip()
    
    