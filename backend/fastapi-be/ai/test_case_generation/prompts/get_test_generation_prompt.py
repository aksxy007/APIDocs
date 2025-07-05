from typing import List, Dict
import json

def get_test_generation_prompt(batch: List[Dict[str, List[Dict]]]) -> str:
    """
    Generates a test case prompt for a batch of collections with realistic, domain-specific test cases.
    Each batch is a dictionary where key = collection name, value = list of endpoints.
    """
    instructions = """
You are an expert software tester AI.

Your task is to generate realistic and comprehensive test cases for API endpoints grouped by their collection (e.g., Users, Items, Login). The test cases MUST be generated and returned in the EXACT order specified below for each collection, with domain-specific data and logical dependencies.

- Each collection contains endpoints related to a specific resource (e.g., Users for user accounts, Items for products).
- Use the **operation** field to identify whether the endpoint is for `create`, `read`, `update`, `delete`, `list`, `register`, `login`, or `other` type.
- For each endpoint:
    - Use the **summary** to infer the domain and generate realistic data (e.g., valid emails for Users, product names/prices for Items).
    - Use **params** to determine required/optional fields, their data types, and constraints (e.g., string length, numeric ranges).
    - Use **responses** to shape expected outputs for success (2xx) and failure (4xx, 5xx) cases.
    - Populate **payload** with realistic, domain-specific values (e.g., "john.doe@example.com" for email, 19.99 for price).
- Generate test cases for ALL provided endpoints, ensuring no endpoints are skipped.
- For non-authentication collections (e.g., Users, Items), generate and return test cases in this EXACT order:
    1. `create` (create a resource with realistic data)
    2. `read_after_create` (retrieve the created resource by ID)
    3. `update` (update the created resource with new valid data)
    4. `read_after_update` (retrieve the updated resource by ID)
    5. `delete` (delete the resource)
    6. `read_after_delete` (verify the resource is deleted)
    7. `list` (retrieve the list of resources, verifying state after create/update/delete)
    8. `other` (any other operations)
- For authentication collections (e.g., Login, Register, Auth), generate and return test cases in this EXACT order:
    1. `register` (register a new user with realistic credentials)
    2. `login_success` (login with correct credentials from register)
    3. `login_failure` (login with incorrect credentials, e.g., wrong password)
    4. `list` (retrieve a list of resources, if applicable)
    5. `other` (any other operations)
- Ensure logical dependencies:
    - For non-auth collections, use the same resource ID (e.g., from `create` response) across `read`, `update`, `delete`, and verify in `list` test cases (e.g., list contains created resource).
    - For auth collections, use the same credentials (e.g., from `register`) in `login_success` and `login_failure`.
- For `list` endpoints:
    - Success cases: Verify empty list before `create`, list contains created/updated resources after `create`/`update`, and list reflects deletions.
    - Failure cases: Test invalid query parameters (e.g., negative limit, invalid sort), unauthorized access, and incorrect data types.
- For each endpoint, generate comprehensive test cases:
    - Success: At least 2 valid payloads (e.g., typical case, edge case like max length).
    - Failure: At least 3 invalid cases (e.g., missing required fields, invalid data types, unauthorized access).
- For non-CRUD/non-auth (`operation: other`) endpoints, generate validation-focused test cases after CRUD/auth tests:
    - Missing required params, invalid credentials, wrong data types, rate limits, server errors.
- If multiple `read` or `list` endpoints exist, use the endpoint with a path containing `{id}` (e.g., `/users/{id}`) for `read` operations and without `{id}` (e.g., `/users`) for `list` operations.
- Use the exact endpoint IDs provided (e.g., `2_read_after_create`, `3_list`, `5_login_success`) to ensure all test cases are correctly associated.
- Ensure the JSON output lists test cases in the exact order specified above for each collection.

Respond in this JSON format:

```json
{
  "<id>": {
    "operation": "<operation>",
    "success": [
      {
        "payload": { ... },
        "expected_response": { ... },
        "response_code": <code>
      },
      ...
    ],
    "failure": [
      {
        "payload": { ... },
        "expected_response": { ... },
        "response_code": <code>
      },
      ...
    ]
  },
  ...
}
```

Example:

Collection: Items
ID: 1
Operation: create
Path: /items
Method: POST
Handler: createItem
Params: [
  {"name": "name", "in": "body", "required": true, "type": "string"},
  {"name": "price", "in": "body", "required": true, "type": "number"},
  {"name": "description", "in": "body", "required": false, "type": "string"}
]
Summary: Creates a new item in the inventory.
Responses: {
  "201": {
    "description": "Item created successfully",
    "response": {
      "id": "uuid",
      "name": "string",
      "price": "number",
      "description": "string"
    }
  },
  "400": {
    "description": "Invalid input",
    "response": {
      "error": "string"
    }
  }
}
File: routes/items.js

ID: 2
Operation: read
Path: /items/{id}
Method: GET
Handler: getItem
Params: [
  {"name": "id", "in": "path", "required": true, "type": "uuid"}
]
Summary: Retrieves item details by ID.
Responses: {
  "200": {
    "description": "Item found",
    "response": {
      "id": "uuid",
      "name": "string",
      "price": "number",
      "description": "string"
    }
  },
  "404": {
    "description": "Item not found",
    "response": {
      "error": "string"
    }
  }
}
File: routes/items.js

ID: 3
Operation: list
Path: /items
Method: GET
Handler: listItems
Params: [
  {"name": "limit", "in": "query", "required": false, "type": "integer"},
  {"name": "sort", "in": "query", "required": false, "type": "string"}
]
Summary: Retrieves a list of all items.
Responses: {
  "200": {
    "description": "List of items",
    "response": {
      "items": [
        {
          "id": "uuid",
          "name": "string",
          "price": "number",
          "description": "string"
        }
      ]
    }
  },
  "400": {
    "description": "Invalid query parameters",
    "response": {
      "error": "string"
    }
  }
}
File: routes/items.js

Collection: Login
ID: 4
Operation: register
Path: /register
Method: POST
Handler: registerUser
Params: [
  {"name": "username", "in": "body", "required": true, "type": "string"},
  {"name": "password", "in": "body", "required": true, "type": "string"}
]
Summary: Registers a new user.
Responses: {
  "201": {
    "description": "User registered successfully",
    "response": {
      "id": "uuid",
      "username": "string"
    }
  },
  "400": {
    "description": "Invalid input",
    "response": {
      "error": "string"
    }
  }
}
File: routes/auth.js

ID: 5
Operation: login
Path: /login
Method: POST
Handler: loginUser
Params: [
  {"name": "username", "in": "body", "required": true, "type": "string"},
  {"name": "password", "in": "body", "required": true, "type": "string"}
]
Summary: Authenticates a user and returns a token.
Responses: {
  "200": {
    "description": "Login successful",
    "response": {
      "token": "string"
    }
  },
  "401": {
    "description": "Invalid credentials",
    "response": {
      "error": "string"
    }
  }
}
File: routes/auth.js

Expected test cases JSON snippet:
{
  "1": {
    "operation": "create",
    "success": [
      {
        "payload": {
          "name": "Laptop",
          "price": 999.99,
          "description": "High-performance laptop"
        },
        "expected_response": {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "Laptop",
          "price": 999.99,
          "description": "High-performance laptop"
        },
        "response_code": 201
      },
      {
        "payload": {
          "name": "Mouse",
          "price": 29.99
        },
        "expected_response": {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "name": "Mouse",
          "price": 29.99,
          "description": null
        },
        "response_code": 201
      }
    ],
    "failure": [
      {
        "payload": {
          "name": "",
          "price": -10
        },
        "expected_response": {
          "error": "Invalid input: name is required, price must be positive"
        },
        "response_code": 400
      },
      {
        "payload": {
          "name": "Laptop",
          "price": "invalid"
        },
        "expected_response": {
          "error": "Invalid input: price must be a number"
        },
        "response_code": 400
      },
      {
        "payload": {},
        "expected_response": {
          "error": "Missing required fields: name, price"
        },
        "response_code": 400
      }
    ]
  },
  "2_read_after_create": {
    "operation": "read_after_create",
    "success": [
      {
        "payload": {
          "id": "550e8400-e29b-41d4-a716-446655440000"
        },
        "expected_response": {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "name": "Laptop",
          "price": 999.99,
          "description": "High-performance laptop"
        },
        "response_code": 200
      }
    ],
    "failure": [
      {
        "payload": {
          "id": "00000000-0000-0000-0000-000000000000"
        },
        "expected_response": {
          "error": "Item not found"
        },
        "response_code": 404
      },
      {
        "payload": {},
        "expected_response": {
          "error": "Missing required field: id"
        },
        "response_code": 400
      },
      {
        "payload": {
          "id": "invalid-uuid"
        },
        "expected_response": {
          "error": "Invalid UUID format"
        },
        "response_code": 400
      }
    ]
  },
  "3_list": {
    "operation": "list",
    "success": [
      {
        "payload": {
          "limit": 10,
          "sort": "name"
        },
        "expected_response": {
          "items": [
            {
              "id": "550e8400-e29b-41d4-a716-446655440000",
              "name": "Laptop",
              "price": 999.99,
              "description": "High-performance laptop"
            },
            {
              "id": "550e8400-e29b-41d4-a716-446655440001",
              "name": "Mouse",
              "price": 29.99,
              "description": null
            }
          ]
        },
        "response_code": 200
      },
      {
        "payload": {},
        "expected_response": {
          "items": [
            {
              "id": "550e8400-e29b-41d4-a716-446655440000",
              "name": "Laptop",
              "price": 999.99,
              "description": "High-performance laptop"
            }
          ]
        },
        "response_code": 200
      }
    ],
    "failure": [
      {
        "payload": {
          "limit": -1
        },
        "expected_response": {
          "error": "Invalid query parameter: limit must be positive"
        },
        "response_code": 400
      },
      {
        "payload": {
          "sort": "invalid_field"
        },
        "expected_response": {
          "error": "Invalid sort field"
        },
        "response_code": 400
      },
      {
        "payload": {
          "limit": "invalid"
        },
        "expected_response": {
          "error": "Invalid query parameter: limit must be an integer"
        },
        "response_code": 400
      }
    ]
  },
  "4": {
    "operation": "register",
    "success": [
      {
        "payload": {
          "username": "testuser123",
          "password": "StrongPass!23"
        },
        "expected_response": {
          "id": "550e8400-e29b-41d4-a716-446655440000",
          "username": "testuser123"
        },
        "response_code": 201
      },
      {
        "payload": {
          "username": "testuser456",
          "password": "AnotherPass!23"
        },
        "expected_response": {
          "id": "550e8400-e29b-41d4-a716-446655440001",
          "username": "testuser456"
        },
        "response_code": 201
      }
    ],
    "failure": [
      {
        "payload": {
          "username": "",
          "password": "123"
        },
        "expected_response": {
          "error": "Invalid input: username is required"
        },
        "response_code": 400
      },
      {
        "payload": {
          "username": "testuser123",
          "password": ""
        },
        "expected_response": {
          "error": "Invalid input: password is required"
        },
        "response_code": 400
      },
      {
        "payload": {},
        "expected_response": {
          "error": "Missing required fields: username, password"
        },
        "response_code": 400
      }
    ]
  },
  "5_login_success": {
    "operation": "login_success",
    "success": [
      {
        "payload": {
          "username": "testuser123",
          "password": "StrongPass!23"
        },
        "expected_response": {
          "token": "jwt_token_string"
        },
        "response_code": 200
      }
    ],
    "failure": []
  },
  "5_login_failure": {
    "operation": "login_failure",
    "success": [],
    "failure": [
      {
        "payload": {
          "username": "testuser123",
          "password": "WrongPass!23"
        },
        "expected_response": {
          "error": "Invalid credentials"
        },
        "response_code": 401
      },
      {
        "payload": {
          "username": "nonexistent",
          "password": "StrongPass!23"
        },
        "expected_response": {
          "error": "Invalid credentials"
        },
        "response_code": 401
      },
      {
        "payload": {},
        "expected_response": {
          "error": "Missing required fields: username, password"
        },
        "response_code": 400
      }
    ]
  }
}

Return only the JSON object, no explanation.

Here are the endpoints in their collection:
"""

    crud_order = [
        "create",
        "read_after_create",
        "update",
        "read_after_update",
        "delete",
        "read_after_delete",
        "list",
        "other"
    ]

    auth_order = [
        "register",
        "login_success",
        "login_failure",
        "list",
        "other"
    ]

    valid_operations = {"create", "read", "update", "delete", "list", "register", "login", "other"}

    ep_blocks = []

    for collection_dict in batch:
        for collection_name, endpoints in collection_dict.items():
            instructions += f"\n# Collection: {collection_name}\n"
            is_auth_collection = collection_name.lower() in ["login", "register", "auth"]

            # Validate endpoint definitions
            for ep in endpoints:
                operation = ep.get("operation", "other")
                if operation not in valid_operations:
                    print(f"Warning: Endpoint ID {ep.get('id', 'unknown')} in collection {collection_name} has invalid operation '{operation}'. Defaulting to 'other'.")
                    ep["operation"] = "other"
                if not ep.get("params") or not ep.get("responses"):
                    print(f"Warning: Endpoint ID {ep.get('id', 'unknown')} in collection {collection_name} is missing params or responses.")

            # Assign context to read, list, and login operations
            def assign_operation_context(ep, index, endpoints):
                operation = ep.get("operation", "other")
                if operation not in ["read", "list", "login"]:
                    return operation
                path = ep.get("path", "")
                if is_auth_collection and operation == "login":
                    if index > 0 and endpoints[index-1].get("operation") == "register":
                        return "login_success"
                    elif index > 0 and endpoints[index-1].get("operation") == "login_success":
                        return "login_failure"
                    return "login_success"
                if operation == "read":
                    if "{id}" not in path:
                        return "other"
                    if index == 0 or (index > 0 and endpoints[index-1].get("operation") in ["create", "read"]):
                        return "read_after_create"
                    elif index > 0 and endpoints[index-1].get("operation") == "update":
                        "read_after_update"
                    elif index > 0 and endpoints[index-1].get("operation") == "delete":
                        return "read_after_delete"
                    return "read_after_create"
                if operation == "list":
                    if "{id}" in path:
                        return "other"
                    return "list"
                return operation

            # Apply context to endpoints
            endpoints_with_context = [
                {**ep, "operation": assign_operation_context(ep, i, endpoints)}
                for i, ep in enumerate(endpoints)
            ]

            # Sort endpoints by appropriate order
            order = auth_order if is_auth_collection else crud_order
            sorted_endpoints = sorted(
                endpoints_with_context,
                key=lambda ep: (order.index(ep.get("operation", "other")), ep.get("id", ""), ep.get("path", ""))
            )

            # Track operations to ensure unique IDs
            operation_count = {op: 0 for op in order}
            for ep in sorted_endpoints:
                ep_id = ep.get("id", "unknown_id")
                operation = ep.get("operation", "other")
                if operation in operation_count:
                    operation_count[operation] += 1
                    if operation_count[operation] > 1 or operation in ["read_after_create", "read_after_update", "read_after_delete", "login_success", "login_failure", "list"]:
                        ep_id = f"{ep_id}_{operation}"
                else:
                    operation_count[operation] = 1

                path = ep.get("path", "")
                method = ep.get("method", "")
                handler = ep.get("handler", "")
                params = json.dumps(ep.get("params", []))
                summary = ep.get("summary", "")
                responses = json.dumps(ep.get("responses", {}))
                file = ep.get("file", "")

                block = (
                    f"ID: {ep_id}\n"
                    f"Operation: {operation}\n"
                    f"Path: {path}\n"
                    f"Method: {method}\n"
                    f"Handler: {handler}\n"
                    f"Params: {params}\n"
                    f"Summary: {summary}\n"
                    f"Responses: {responses}\n"
                    f"File: {file}\n"
                )
                ep_blocks.append(block)

    return instructions + "\n\n" + "\n".join(ep_blocks)