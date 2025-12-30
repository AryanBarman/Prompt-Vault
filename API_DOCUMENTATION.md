# FastAPI Auth & Prompts API Documentation

This documentation details the available endpoints, their functionalities, and the expected input/output formats for the **FastAPI Auth** project.

## Base URL

By default, the API is served at:
- **Local:** `http://127.0.0.1:8000`

The API endpoints are prefixed with `/api/v1`.

---

## 1. Authentication

### Signup
Create a new user account.

- **Endpoint:** `POST /api/v1/signup`
- **Description:** Registers a new user. Checks if the email is already registered.
- **Request Body:** `UserCreate`
  ```json
  {
    "email": "user@example.com",
    "password": "password123" // Must be at least 6 characters
  }
  ```
- **Response (201 Created):** `UserOut`
  ```json
  {
    "email": "user@example.com",
    "id": 1,
    "created_at": "2023-10-27T10:00:00",
    "updated_at": "2023-10-27T10:00:00"
  }
  ```
- **Errors:**
  - `400 Bad Request`: Email already registered.

### Login
Login with email and password to receive an access token.

- **Endpoint:** `POST /api/v1/login`
- **Description:** Authenticates a user and returns a JWT access token.
- **Request Body:** `UserLogin`
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response (200 OK):** `Token`
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
    "token_type": "bearer"
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Incorrect email or password.

### Get Profile
Get the currently authenticated user's profile.

- **Endpoint:** `GET /api/v1/profile`
- **Headers:** `Authorization: Bearer <access_token>`
- **Description:** Returns the details of the logged-in user.
- **Response (200 OK):** `UserOut`
  ```json
  {
    "email": "user@example.com",
    "id": 1,
    "created_at": "2023-10-27T10:00:00",
    "updated_at": "2023-10-27T10:00:00"
  }
  ```

---

## 2. Prompts Management

All prompt endpoints require authentication (`Authorization: Bearer <access_token>`).

### Create Prompt
Create a new prompt.

- **Endpoint:** `POST /api/v1/prompts/`
- **Request Body:** `PromptCreate`
  ```json
  {
    "title": "My Prompt",
    "content": "This is the content of the prompt.",
    "description": "Optional description"
  }
  ```
- **Response (201 Created):** `PromptOut`
  ```json
  {
    "id": 1,
    "title": "My Prompt",
    "content": "This is the content of the prompt.",
    "description": "Optional description",
    "user_id": 1
  }
  ```

### Get All Prompts
Retrieve all prompts for the current user.

- **Endpoint:** `GET /api/v1/prompts/`
- **Query Parameters:**
  - `skip` (int, default=0): Number of records to skip.
  - `limit` (int, default=100): Maximum number of records to return.
- **Response (200 OK):** List of `PromptOut`
  ```json
  [
    {
      "id": 1,
      "title": "My Prompt",
      "content": "...",
      "description": "...",
      "user_id": 1
    }
  ]
  ```

### Search Prompts
Search prompts by title or description.

- **Endpoint:** `GET /api/v1/prompts/search`
- **Query Parameters:**
  - `query` (str): Search term.
  - `skip` (int, default=0)
  - `limit` (int, default=100)
- **Response (200 OK):** List of `PromptOut`

### Get Semantic Search
Search prompts using semantic similarity (Mock service logic).

- **Endpoint:** `GET /api/v1/prompts/search/semantic`
- **Query Parameters:**
  - `q` (str): The semantic query string.
- **Response (200 OK):** List of Objects
  ```json
  [
    {
      "id": 1,
      "title": "My Prompt",
      "content": "..."
    }
  ]
  ```

### Get Specific Prompt
Get a prompt by its ID.

- **Endpoint:** `GET /api/v1/prompts/{prompt_id}`
- **Response (200 OK):** `PromptOut`
- **Errors:**
  - `404 Not Found`: Prompt does not exist.
  - `403 Forbidden`: Prompt belongs to another user.

### Update Prompt
Update a prompt's content, title, or description. Creates a new version history entry if content changes.

- **Endpoint:** `PUT /api/v1/prompts/{prompt_id}`
- **Request Body:** `PromptUpdate`
  ```json
  {
    "title": "Updated Title",      // Optional
    "content": "Updated content",  // Optional
    "description": "New desc"      // Optional
  }
  ```
- **Response (200 OK):** `PromptOut`

### Delete Prompt
Delete a prompt.

- **Endpoint:** `DELETE /api/v1/prompts/{prompt_id}`
- **Response (204 No Content):** Empty body.

### Get Prompt Versions
Get the version history of a prompt.

- **Endpoint:** `GET /api/v1/prompts/{prompt_id}/versions`
- **Response (200 OK):** List of `PromptVersionOut`
  ```json
  [
    {
      "id": 10,
      "prompt_id": 1,
      "version_number": 1,
      "content": "Original content",
      "created_at": "..."
    }
  ]
  ```

### Get Version Count
Get total number of versions for a prompt.

- **Endpoint:** `GET /api/v1/prompts/{prompt_id}/version_count`
- **Response (200 OK):**
  ```json
  {
    "total_versions": 5
  }
  ```

### Rollback to Version
Revert a prompt's content to a specific version.

- **Endpoint:** `POST /api/v1/prompts/{prompt_id}/rollback/{version_number}`
- **Response (200 OK):** `PromptOut` (The prompt with content reverted)

### AI Suggest Version
Get an AI suggestion for the next version of the prompt (Mock service logic).

- **Endpoint:** `GET /api/v1/prompts/{prompt_id}/ai/suggest-version`
- **Response (200 OK):**
  ```json
  {
    "prompt_id": 1,
    "title": "Prompt Title",
    "ai_suggestion": "Suggested improved content..."
  }
  ```

---

## 3. Metrics

### System Metrics
Get system-wide metrics.

- **Endpoint:** `GET /api/v1/metrics/`
- **Response (200 OK):**
  ```json
  {
    "total_requests": 150,
    "total_errors": 2,
    "total_domain_errors": 1,
    "total_internal_errors": 1,
    "average_response_time_ms": 120.5
  }
  ```

---

## 4. General

### Root
- **Endpoint:** `GET /`
- **Response:**
  ```json
  {
    "message": "Welcome to FastAPI Auth & Prompts API",
    "docs": "/docs",
    "version": "1.0.0"
  }
  ```

### Health Check
- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "healthy"
  }
  ```

---

## 5. Data Schemas

### User
- **UserCreate**: `{ email: str, password: str (min 6 chars) }`
- **UserLogin**: `{ email: str, password: str }`
- **UserOut**: `{ id: int, email: str, created_at: datetime, updated_at: datetime }`
- **Token**: `{ access_token: str, token_type: str }`

### Prompt
- **PromptCreate**: `{ title: str (<200 chars), content: str, description: str? }`
- **PromptUpdate**: `{ title: str?, content: str?, description: str? }`
- **PromptOut**: `{ id: int, title: str, content: str, description: str?, user_id: int }`
- **PromptVersionOut**: `{ id: int, prompt_id: int, version_number: int, content: str, created_at: datetime }`
