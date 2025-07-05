from typing import Dict, List
import json

def get_doc_builder_prompt(batch: Dict[str, List[Dict]]) -> str:
    """
    Generates a prompt for creating OpenAPI JSON and language-specific code snippets for a batch of endpoints across multiple collections.
    """

    if not batch:
        return "No endpoints provided. Return an empty JSON object: {}"

    batch_blocks = []
    for collection_name, endpoints in batch.items():
        if not endpoints:
            continue
        collection_block = [f"Collection: {collection_name}"]
        for ep in endpoints:
            block = (
                f"  ID: {ep.get('id', 'unknown')}\n"
                f"  Operation: {ep.get('operation', 'other')}\n"
                f"  Path: {ep.get('path', '')}\n"
                f"  Method: {ep.get('method', '').upper()}\n"
                f"  Handler: {ep.get('handler', '')}\n"
                f"  Params: {json.dumps(ep.get('params', []), default=str)}\n"
                f"  Summary: {ep.get('summary', '')}\n"
                f"  Responses: {json.dumps(ep.get('responses', {}), default=str)}\n"
                f"  File: {ep.get('file', '')}\n"
            )
            collection_block.append(block)
        batch_blocks.append("\n".join(collection_block))

    prompt = f"""
You are an expert in generating API documentation.

Given the following API endpoint metadata grouped by their collections (e.g., Users, Items), generate a JSON object where each collection maps to its endpoints and each endpoint contains:

- An OpenAPI-compliant `openapi_snippet` with:
    - path, method, operationId
    - summary and description
    - parameters and/or requestBody
    - responses
    - tags (collection name)
    - security if applicable (e.g., BearerAuth)

- `code_snippets` as a dictionary with the following keys:
    - `bash`: A cURL example
    - `python`: A Python requests example
    - `javascript`: A fetch example
    - `typescript`: A TypeScript fetch example

Use parameter types and values from `params` and `test_cases` to form examples.
Use appropriate auth headers for endpoints in auth-protected collections (like "auth", "users").

The expected response format:

```json
{{
  "Items": {{
    "/items": {{
      "openapi_snippet": {{
        "post": {{
          "operationId": "createItem",
          "summary": "Create a new item",
          "description": "Adds a new item to the database",
          "tags": ["Items"],
          "requestBody": {{
            "required": true,
            "content": {{
              "application/json": {{
                "schema": {{
                  "type": "object",
                  "properties": {{
                    "name": {{ "type": "string" }},
                    "price": {{ "type": "number" }}
                  }},
                  "required": ["name", "price"]
                }},
                "example": {{
                  "name": "Sample Item",
                  "price": 99.99
                }}
              }}
            }}
          }},
          "responses": {{
            "201": {{
              "description": "Item created",
              "content": {{
                "application/json": {{
                  "example": {{
                    "id": "abc123",
                    "name": "Sample Item",
                    "price": 99.99
                  }}
                }}
              }}
            }},
            "400": {{
              "description": "Invalid input"
            }}
          }}
        }}
      }},
      "code_snippets": {{
        "bash": "curl -X POST https://api.example.com/items -H 'Content-Type: application/json' -H 'Authorization: Bearer <token>' -d '{{\"name\": \"Sample Item\", \"price\": 99.99}}'",
        "python": "import requests\\nrequests.post('https://api.example.com/items', json={{'name': 'Sample Item', 'price': 99.99}}, headers={{'Authorization': 'Bearer <token>'}})",
        "javascript": "fetch('/items', {{ method: 'POST', headers: {{ 'Authorization': 'Bearer <token>', 'Content-Type': 'application/json' }}, body: JSON.stringify({{ name: 'Sample Item', price: 99.99 }}) }});",
        "typescript": "const res = await fetch('/items', {{ method: 'POST', headers: {{ 'Authorization': 'Bearer <token>', 'Content-Type': 'application/json' }}, body: JSON.stringify({{ name: 'Sample Item', price: 99.99 }}) }});"
      }}
    }}
  }}
}}
Now generate documentation for the following endpoints grouped by their collections:
""" + "\n\n".join(batch_blocks)

    return prompt
