from typing import List, Dict

def get_js_extraction_prompt(batch:List[Dict]) -> str:
    code_blocks = "\n\n".join([
        f"// File: {chunk['file_name']}\n{chunk['code']}" for chunk in batch
    ])
    
    prompt= f"""
You are an expert in analyzing Express.js backend code.

From the following JavaScript or TypeScript code chunks, extract all Express API endpoints and return them as a **JSON list**, OpenAPI-style.

Each endpoint must include:
- path: API path (e.g., "/users/:id")
- method: HTTP method (GET, POST, etc.)
- handler: Name of the handler function (if available)
- file: Relative file path
- params: A list of parameter objects. Each param must have:
  - name: Parameter name
  - in: "query", or "body"
  - required: true or false
  - type: "string", "number", "boolean", etc.
- summary: A 5–10 word summary describing the API’s purpose, including any CRUD or database actions
- responses: A dictionary of status codes with:
  - description: Short explanation of the response
  - content_type: Usually "application/json"
  - response: Example response with field names and types
Each endpoint must also include:
- operation (one of: "create", "read", "update", "delete", or "other")

Use the function body or summary to infer the operation.  
If it's a POST/PUT that writes to the DB, it's probably "create" or "update".  
If it's a GET with query/path param, it's likely "read" or "list" for getting list of data.  
If it's a DELETE call, it's "delete".  
If it performs login/auth/email logic, use "other".

Output only a JSON list. No markdown, explanations, or extra formatting.Always use ```json <JSON content> ``` for json response

### Example:
```json
[
  {{
    "path": "/users/:id",
    "method": "GET",
    "handler": "getUser",
    "file": "routes/users.js",
    "params": [
      {{
        "name": "id",
        "in": "query",
        "required": true,
        "type": "number",
        "description": "User ID to fetch"
      }}
    ],
    "summary": "Fetch user by ID from the database.",
    "operation": "read",
    "responses": {{
      "200": {{
        "description": "User found",
        "content_type": "application/json",
        "response": {{
          "id": "number",
          "name": "string",
          "email": "string"
        }}
      }},
      "404": {{
        "description": "User not found",
        "content_type": "application/json",
        "response": {{
          "error": "string"
        }}
      }}
    }}
  }}
]  

Example:
- When no endpoints found.

```json
[]
```
 
here is the code block:
{code_blocks}
    
    """
    
    return prompt.strip()
    