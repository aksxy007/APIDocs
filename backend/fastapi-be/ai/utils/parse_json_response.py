import json
import re

def parse_json_response(response: str) -> dict | list:
    """
    Extracts and parses JSON (list or dict) from LLM output,
    even if surrounded by non-JSON text, markdown, or with multiple top-level JSON objects.
    """
    response = response.strip()

    # Step 1: Remove markdown-style ```json blocks if any
    markdown_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response, re.DOTALL)
    if markdown_match:
        response = markdown_match.group(1).strip()

    # Step 2: Try direct parse first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Step 3: Try to extract all individual JSON objects
    json_objects = re.findall(r"\{[^{}]+\}", response, re.DOTALL)
    if json_objects:
        result = {}
        for obj in json_objects:
            try:
                parsed = json.loads(obj)
                if isinstance(parsed, dict):
                    result.update(parsed)
            except json.JSONDecodeError:
                continue
        if result:
            return result

    # Step 4: Try list matching
    json_list_match = re.search(r"\[\s*[\s\S]+?\s*\]", response)
    if json_list_match:
        try:
            return json.loads(json_list_match.group().strip())
        except json.JSONDecodeError:
            pass

    raise ValueError("Invalid JSON after fallback attempt.")
