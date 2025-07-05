import json
from typing import Dict, List

def get_code_snippets_prompt(batch: Dict[str, List[Dict]]) -> str:
    """
    Generates a prompt asking the LLM to produce code snippets per endpoint ID,
    with all endpoint metadata in readable blocks for context.
    """
    if not batch:
        return "No endpoints provided. Return an empty JSON object: {{}}"

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
You are an expert API documentation assistant.

Given the following API endpoint metadata grouped by collections, generate a JSON object mapping each endpoint ID
to its language-specific code snippets.

Each snippet should include these 5 keys:
- `bash`: A cURL example
- `python`: Using `requests`
- `javascript`: Using `fetch`
- `typescript`: Using `fetch` with type annotations
- `php`: Using `curl` in PHP

Add `Authorization: Bearer <token>` header if the collection is 'auth' or 'users'.

Here’s an example output:

```json
{{
  "f9372bb1-47ab-4a1e-8d91-abc123def456": {{
    "bash": "curl -X GET https://api.example.com/users/123 -H 'Authorization: Bearer <token>'",
    "python": "import requests\\nrequests.get('https://api.example.com/users/123', headers={{'Authorization': 'Bearer <token>'}})",
    "javascript": "fetch('https://api.example.com/users/123', {{ method: 'GET', headers: {{ 'Authorization': 'Bearer <token>' }} }});",
    "typescript": "const res = await fetch('https://api.example.com/users/123', {{ method: 'GET', headers: {{ Authorization: 'Bearer <token>' }} }});",
    "php": "$ch = curl_init('https://api.example.com/users/123');\\ncurl_setopt($ch, CURLOPT_HTTPHEADER, array('Authorization: Bearer <token>'));\\n$response = curl_exec($ch);\\ncurl_close($ch);"
  }}
}}


Output only a JSON object. No markdown, explanations, or extra formatting.
Always use ```json <JSON content> ``` for json response     

Now generate code snippets for the following endpoints:
{batch_blocks}

"""
    return prompt

