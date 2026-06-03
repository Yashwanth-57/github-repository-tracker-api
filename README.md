



# 1. Project Overview

This project is a backend REST API built with FastAPI that allows users to save and manage GitHub repository information using PostgreSQL.

The application connects to the GitHub REST API to fetch repository details from a GitHub repository URL. Once the data is retrieved, it is stored in a PostgreSQL database, making it available for future access without repeatedly calling the GitHub API.

Users can create repository records, retrieve stored information, refresh repository data with the latest details from GitHub, and delete repositories when they are no longer needed.

The project follows a layered architecture, where each responsibility is separated into dedicated modules. API routes handle incoming requests, service layers contain business logic, repositories manage database interactions, schemas perform request validation, and external integrations communicate with the GitHub API. This separation makes the codebase easier to maintain, test, and extend.

## Key Features

* Store GitHub repository information from a repository URL
* Retrieve saved repository details from PostgreSQL
* Refresh repository metadata using the latest GitHub API data
* Delete stored repositories
* Centralized exception handling with consistent error responses
* Request and response validation using Pydantic
* Asynchronous database operations using SQLAlchemy Async ORM
* Asynchronous communication with external APIs using HTTPX
* PostgreSQL database integration with Docker support
* Unit and integration testing using Pytest

## GitHub API Integration

The GitHub REST API was chosen because it provides reliable and well-structured repository metadata through a public API. Before making external API requests, the application validates the provided GitHub repository URL to ensure only valid repositories are processed.

## Supported API Operations

| Method | Endpoint           | Description                          |
| ------ | ------------------ | ------------------------------------ |
| POST   | /repositories      | Create and store a GitHub repository |
| GET    | /repositories/{id} | Retrieve repository details          |
| PUT    | /repositories/{id} | Refresh repository metadata          |
| DELETE | /repositories/{id} | Delete a repository                  |

## Technology Stack

* FastAPI
* PostgreSQL
* SQLAlchemy Async ORM
* HTTPX
* Pydantic
* AsyncPG
* Docker & Docker Compose
* Pytest

The application can be run locally for development or deployed in a containerized environment using Docker and Docker Compose.


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 2. Architecture Summary

## Overview

This project follows a layered monolithic architecture built with FastAPI, PostgreSQL, SQLAlchemy Async ORM, and the GitHub REST API.

The application is organized into separate layers, where each layer has a specific responsibility. This approach keeps the codebase easier to understand, maintain, test, and extend as the project grows.

The overall request flow follows:

```text
Client Request
      │
      ▼
API Routes
      │
      ▼
Schema Validation
      │
      ▼
Service Layer
      │
 ┌────┴────┐
 ▼         ▼
Database   GitHub API
      │
      ▼
Response
```

---

## Project Structure

```text
app/
│
├── api/
│   └── repository_routes.py
│
├── core/
│   ├── config.py
│   ├── exceptions.py
│   └── handlers.py
│
├── database/
│   ├── base.py
│   ├── db.py
│   └── init_db.py
│
├── models/
│   └── repository.py
│
├── schemas/
│   └── repository.py
│
├── services/
│   ├── github_service.py
│   └── repository_service.py
│
├── utils/
│   └── mapper.py
│
└── main.py


tests/
│
├── integration/
│   ├── test_post.py
│   ├── test_get.py
│   ├── test_put.py
│   └── test_delete.py
│
├── unit/
│   ├── test_validation.py
│   ├── test_duplicate.py
│ 
│
├── conftest.py
│
├
│
└── pytest.ini


Dockerfile
docker-compose.yml
.env
.env.test
.gitignore
requirements.txt
create_table.py
```

---

## Layer Responsibilities

### API Layer (`api/`)

The API layer is responsible for:

* Registering FastAPI routes
* Receiving HTTP requests
* Returning HTTP responses
* Managing dependency injection

Route handlers remain intentionally lightweight and delegate business operations to the service layer.

Example:

```python
@router.post("/repositories")
async def create_repository(
    data: RepositoryCreate,
    session: AsyncSession = Depends(get_session)
):
    repo = await create_repository_service(
        str(data.url),
        session
    )

    await session.commit()

    return repo
```

---

### Validation Layer (`schemas/`)

Pydantic schemas validate incoming request data before any database or external API operation occurs.

Validation rules include:

* Valid URL format
* GitHub-only URLs
* Repository owner validation
* Repository name validation

Example:

```python
@field_validator("url")
@classmethod
def validate_github_url(cls, v):
    if "github.com" not in str(v):
        raise ValueError(
            "Only GitHub URLs allowed"
        )

    return v
```

This prevents invalid requests from reaching the service layer.

---

### Service Layer (`services/`)

The service layer contains all application business logic.

Responsibilities include:

* Fetching repository data from GitHub
* Duplicate repository detection
* Refreshing repository metadata
* Querying database records
* Raising custom application exceptions

Example:

```python
existing = await session.execute(
    select(Repository).where(
        Repository.github_id == repo_data["github_id"]
    )
)

if existing.scalar_one_or_none():
    raise ConflictError()
```

Separating business logic from routes improves maintainability and testability.

---

### External API Layer (`github_service.py`)

This layer handles communication with the GitHub REST API using asynchronous HTTP requests.

Example:

```python
async with httpx.AsyncClient(
    timeout=setting.HTTPTIMEOUT()
) as client:

    response = await client.get(api_url)
```

The layer also handles:

* API timeouts
* Network failures
* Invalid responses
* Missing repositories

Custom exceptions are raised and handled centrally by the application.

---

### Database Layer (`database/` + `models/`)

The database layer is responsible for:

* PostgreSQL connections
* Session management
* ORM model definitions
* Transaction handling

The application uses SQLAlchemy Async ORM with AsyncSession for non-blocking database operations.

Example:

```python
github_id: Mapped[int] = mapped_column(
    Integer,
    unique=True,
    index=True
)
```

Database-level constraints provide an additional layer of data integrity beyond application-level validation.

---

### Utility Layer (`utils/`)

The utility layer contains reusable helper functions that transform external API responses into application-specific formats.

Example:

```python
def map_github_response(data):

    return {
        "github_id": data["id"],
        "name": data["name"],
        "owner": data["owner"]["login"],
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data["stargazers_count"],
        "repo_url": data["html_url"]
    }
```

This keeps transformation logic separate from service logic.

---

### Exception Handling Layer (`core/`)

The application uses custom exception classes and centralized exception handling to provide consistent error responses.

Custom exceptions:

```python
class NotFoundError(AppError):
    pass

class ConflictError(AppError):
    pass

class ExternalAPIError(AppError):
    pass
```

Global exception handlers convert application errors into standardized HTTP responses.

```python
def error_response(status_code: int, message: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": message
        }
    )
```
Benefits:

* Consistent API responses
* Reduced duplicate error handling
* Easier maintenance

---------------------------------------------------------------------------------------------

## Testing Architecture

The project includes both unit tests and integration tests.

### Unit Tests

Unit tests validate individual pieces of functionality in isolation.

Covered areas:

* URL validation
* Duplicate detection

External dependencies are mocked to keep tests fast and deterministic.

---

### Integration Tests

Integration tests verify complete endpoint behavior using:

* FastAPI test client
* PostgreSQL test database
* Dependency overrides
* Real database operations

The application overrides database sessions during testing:

```python

app.dependency_overrides[
    get_session
] = override_get_session

```

This ensures that test execution never affects development data.

---

## Database Isolation Strategy

A dedicated PostgreSQL test database is used during integration testing.

Example:

```text
github_tracker_test
```

Before every test:

* Repository records are removed
* Primary keys are reset
* Test isolation is maintained

Example:

```python
TRUNCATE TABLE repositories
RESTART IDENTITY CASCADE
```

This ensures reliable and repeatable test execution regardless of test order.

---

## Request Lifecycle Example

POST `/repositories`

1. Client submits a GitHub repository URL.
2. FastAPI receives the request.
3. Pydantic validates the input.
4. Dependency injection creates a database session.
5. Service layer requests repository metadata from GitHub.
6. Duplicate repository validation is performed.
7. Repository entity is created.
8. Data is written to PostgreSQL.
9. Transaction is committed.
10. Repository data is returned with HTTP 201 Created.

```
```

# Running the Tests

The project uses **pytest** and **pytest-asyncio** for automated testing.

The test suite is divided into:

* Unit Tests
* Integration Tests

All tests run in a fully isolated environment using a dedicated PostgreSQL test database.

---

## Run All Tests

```bash
pytest
```

This command runs the complete test suite.

### Example Output

```text
======================================= test session starts ========================================

platform win32 -- Python 3.14.5
pytest-9.0.3

collected 12 items

tests/integration/test_delete.py ..
tests/integration/test_get.py ..
tests/integration/test_post.py .
tests/integration/test_put.py ..
tests/unit/test_duplicate.py .
tests/unit/test_validation.py ....

======================================== 12 passed in 4.45s ========================================
```

---

## What This Command Runs

Running `pytest` executes:

### Unit Tests

* Input validation logic
* Duplicate detection logic
* Service-layer business rules

### Integration Tests

* Full FastAPI request → response cycle
* PostgreSQL database operations
* External API integration (mocked)
* CRUD endpoint behavior

---

## Test Structure

```text
tests/
│
├── integration/
│   ├── test_post.py
│   ├── test_get.py
│   ├── test_put.py
│   └── test_delete.py
│
├── unit/
│   ├── test_validation.py
│   ├── test_duplicate.py
│
└── conftest.py
```

---

# Unit Tests

Unit tests focus on business logic only.

No real database or HTTP requests are made.

All external dependencies are mocked.

## Covered Scenarios

### 1. Input Validation

Ensures only valid GitHub repository URLs are accepted.

Example invalid input:

```json
{
  "url": "https://gitlab.com/user/repo"
}
```

Expected response:

```text
422 Unprocessable Entity
```

Includes validation for:

* Invalid URL format
* Non-GitHub domains
* Missing owner/repository structure

### 2. Duplicate Detection

Ensures duplicate repositories are not inserted into the database.

Logic tested:

```python
if existing.scalar_one_or_none():
    raise ConflictError()
```

Expected response:

```text
409 Conflict
```

---

## Run Unit Tests Only

```bash
pytest tests/unit
```

---

# Integration Tests

Integration tests validate the full request lifecycle:

```text
FastAPI Route → Service Layer → Database → Response
```

## Technologies Used

* FastAPI Test Client (`httpx.AsyncClient`)
* Async SQLAlchemy Session
* PostgreSQL Test Database
* Dependency Override System
* Mocked GitHub API Responses

## Covered Scenarios

| Method | Scenario             | Expected Status |
| ------ | -------------------- | --------------- |
| POST   | Create repository    | 201             |
| POST   | Duplicate repository | 409             |
| POST   | Invalid input        | 422             |
| GET    | Existing record      | 200             |
| GET    | Non-existing record  | 404             |
| PUT    | Refresh record       | 200             |
| PUT    | Missing record       | 404             |
| DELETE | Delete record        | 204             |
| DELETE | Missing record       | 404             |

---

## Run Integration Tests Only

```bash
pytest tests/integration
```

---

# Test Environment Architecture

This project uses a fully isolated test database system.

## 1. Separate Test Database

All tests run against:

```text
github_tracker_test
```

The development database is never used during testing.

---

## 2. Dependency Override (FastAPI)

The application database session is overridden during tests:

```python
app.dependency_overrides[get_session] = override_get_session
```

This ensures:

* API routes use the test database only
* No production/development data is affected
* Fully controlled test execution

---

## 3. Async Test Database Engine

A separate async engine is created:

```python
create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool
)
```

This helps ensure:

* Clean database connections
* Proper session isolation
* Predictable test execution

---

## 4. Automatic Schema Setup

Before the test suite starts:

```python
await conn.run_sync(Base.metadata.drop_all)
await conn.run_sync(Base.metadata.create_all)
```

This ensures every test run starts with a fresh database schema.

---

## 5. Automatic Cleanup Between Tests

Before each test:

```sql
TRUNCATE TABLE repositories RESTART IDENTITY CASCADE;
```

This guarantees:

* No leftover records
* No duplicate-key conflicts from previous tests
* Consistent and repeatable results

---

## 6. Test Client Setup

API tests use:

```python
AsyncClient(
    transport=ASGITransport(app=app),
    base_url="http://test"
)
```

This allows:

* Full FastAPI application testing
* No real server required
* Fast in-memory request execution

---

# Key Testing Guarantees

This testing architecture ensures:

* Fully isolated PostgreSQL test database
* No dependency on the development database
* No real external API calls
* Deterministic test results
* Repeatable test execution
* Clean database state before every test

---

# Why This Testing Design Was Used

This testing approach was chosen to satisfy backend engineering best practices:

* Avoids flaky tests caused by external APIs
* Prevents cross-test data contamination
* Verifies complete API behavior
* Matches the application's async architecture
* Keeps tests fast, reliable, and maintainable


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# 3. Prerequisites

Before running this project, ensure the following software is installed on your machine.

| Requirement | Minimum Version | Purpose |
|------------|----------------|----------|
| Python | 3.10+ | Application runtime |
| PostgreSQL | 13+ | Primary database |
| Git | Latest | Clone repository |
| pip | Latest | Dependency management |
| Docker | 20+ | Containerized application setup (Optional) |
| Docker Compose | 2+ | Run application and PostgreSQL containers (Optional) |

## Verify Installation

### Python

```bash
python --version
```

Expected:

```bash
Python 3.10+
```

### PostgreSQL

```bash
psql --version
```

Expected:

```bash
psql (PostgreSQL) 13+
```

### Git

```bash
git --version
```

Expected:

```bash
git version 2.x.x
```

### pip

```bash
pip --version
```

Expected:

```bash
pip 23+
```

### Docker (Optional)

```bash
docker --version
```

Expected:

```bash
Docker version 20+
```

### Docker Compose (Optional)

```bash
docker compose version
```

Expected:

```bash
Docker Compose version 2+
```

## External API Access

The application integrates with the GitHub REST API to retrieve repository metadata.

Only publicly accessible GitHub repositories are supported.

No GitHub account or user authentication is required to use the application.

### GitHub Personal Access Token (Optional)

A GitHub Personal Access Token may be configured through the `.env` file to increase GitHub API rate limits.

Example:

```env
GITHUB_TOKEN=your_personal_access_token
```

The token is used only by the backend service when communicating with the GitHub API and is never exposed to API consumers.


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# 4. Setup Instructions

Follow the steps below to set up and run the project locally.

---

## Step 1: Create a Workspace Directory

Create a folder where you want to store the project.

Example:

```bash
mkdir Projects
cd Projects
```

---

## Step 2: Clone the Repository

Clone the repository from GitHub:

```bash
git clone https://github.com/Yashwanth-57/github-repository-tracker-api
```

Move into the project directory:

```bash
cd BasicProject
```

Verify that the project files are present:

```bash
dir
```

Expected output should include files similar to:

```text
app/
tests/
create_tables.py
requirements.txt
docker-compose.yml
Dockerfile
.env.example
README.md
```

---

# Option 1: Local Development Setup

## Step 3: Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

Linux / macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

After activation, your terminal should display:

```text
(venv)
```

---

## Step 4: Install Dependencies

Install all required packages:

```bash
pip install -r requirements.txt
```

###  *** Important***

 The requirements file contains pinned dependency versions to ensure the application runs with the same package versions used during development and testing.

Verify installation:

```bash
pip list
```

---

## Step 5: Configure Environment Variables

Create a new `.env` file in the project root.

Copy values from `.env.example`.

Example:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/github_tracker

GITHUB_API_BASE_URL=https://api.github.com


HTTP_TIEMOUT=10
```

---

## Step 6: Start PostgreSQL

Ensure PostgreSQL is running.

Connect to PostgreSQL:

```bash
psql -U postgres
```

Create the application database:

```sql
CREATE DATABASE github_tracker;
```

Verify database creation:

```sql
\l
```

Expected output should contain:

```text
github_tracker
```

Exit PostgreSQL:

```sql
\q
```

---

## Step 7: Create Database Tables

Run the database initialization script:

```bash
python create_tables.py
```

This automatically creates all required tables using SQLAlchemy ORM models.

If successful, the script completes without errors.

---

## Step 8: Start the FastAPI Application

Run:

```bash
uvicorn app.main:app --reload
```

Expected output:

```text
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

## Step 9: Verify the Application

Open:

Application:

```text
http://localhost:8000/docs
```
```

The API is now ready to use.


Test using postman

---

# Option 2: Docker Setup

## Step 1: Clone the Repository

```bash
git clone https://github.com/Yashwanth-57/github-repository-tracker-api
cd BasicProject
```

---

## Step 2: Configure Environment Variables

Create a `.env` file using `.env.example`.

---

## Step 3: Build and Start Containers

before that you need double check that in .env in DATABSE_URL the name should be "db" not "local"

DATABASE_URL=postgresql+asyncpg://postgres:your_pass@db:5432/github_tracker


```bash
docker compose up --build
```

This command:

* Builds the FastAPI image
* Pulls PostgreSQL image
* Creates required containers
* Starts PostgreSQL
* Starts FastAPI
* Loads environment variables from `.env`

---

## Step 4: Verify Running Containers

```bash
docker ps
```

Expected containers:

```text
basicproject-db
basicproject-api
```

---

## Step 5: Access the Application

Swagger UI:

```text
http://localhost:8000/docs
```


---

# Option 3: Run Using a Pre-Built Docker Image

Pull the image:

```bash
docker pull yashwanth57/github-repository-tracker-api:latest
```

Run the container:

```bash
docker run -p 8000:8000 --env-file .env yashwanth57/github-repository-tracker-api:latest
```
next thing after this , in ddocker terminal you need run that command first for create_tabel

# python create_table.py

Access: open in browser automatically that opens with the swagger ui for better ui tetsing.

```text
http://localhost:8000/docs
```

---

## Docker Compose Configuration

The project includes a Docker Compose configuration that starts both PostgreSQL and the FastAPI application.

```yaml
services:

  db:
    image: postgres:16

    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: yashwanth
      POSTGRES_DB: github_tracker

    ports:
      - "5432:5432"

    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .

    depends_on:
      - db

    env_file:
      - .env

    ports:
      - "8000:8000"

volumes:
  postgres_data:
```

Start the complete stack:

```bash
docker compose up --build
```


----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# 5. Environment Variables Reference

The application uses environment variables for configuration.

Create a `.env` file in the project root using the values from `.env.example`.

For testing, a separate `.env.test` file is used to isolate test execution from the development database.

## Application Environment Variables (.env)

| Variable            | Required | Default                | Description                                           |
| ------------------- | -------- | ---------------------- | ----------------------------------------------------- |
| DATABASE_URL        | Yes      | None                   | PostgreSQL connection string used by the application  |
| GITHUB_API_BASE_URL | Yes      | https://api.github.com | Base URL for GitHub REST API requests                 |
| HTTP_TIMEOUT        | No       | 10                     | Timeout (in seconds) for external GitHub API requests |

Example:

```env
DATABASE_URL=postgresql+asyncpg://your_username:your_password@db:5432/github_tracker

GITHUB_API_BASE_URL=https://api.github.com

HTTP_TIMEOUT=10
```

---

## Test Environment Variables (.env.test)

The test suite uses a completely separate database to ensure isolation from development data.

| Variable            | Required | Default                | Description                                           |
| ------------------- | -------- | ---------------------- | ----------------------------------------------------- |
| DATABASE_URL        | Yes      | None                   | PostgreSQL connection string used only during testing |
| GITHUB_API_BASE_URL | Yes      | https://api.github.com | GitHub API base URL used in tests                     |
| HTTP_TIMEOUT        | No       | 10                     | Timeout configuration used during tests               |

Example:

```env
DATABASE_URL=postgresql+asyncpg://your_username:your_password@local:5432/github_tracker_test

GITHUB_API_BASE_URL=https://api.github.com

HTTP_TIMEOUT=10
```

---

## Environment Separation

Two separate databases are used:

| Environment | Database            |
| ----------- | ------------------- |
| Development | github_tracker      |
| Testing     | github_tracker_test |

This separation ensures:

* Test execution never modifies development data
* Integration tests remain isolated and repeatable
* Test failures cannot corrupt application data
* Developers can safely run tests at any time

---

## Notes

* Environment variables are loaded automatically when the application starts.
* Sensitive configuration values should never be committed to source control.
* The `.env` and `.env.test` files are excluded through `.gitignore`.
* Developers should use `.env.example` as the template for creating local configuration files.



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


# 6. API Reference

The API manages GitHub repositories by fetching metadata from the GitHub REST API and storing it locally in PostgreSQL.

---

## POST /repositories

Creates a new repository record.

### Request Body

```json
{
  "url": "https://github.com/fastapi/fastapi"
}
```

### Success Response

**201 Created**

```json
{
  "id": 1,
  "github_id": 123456,
  "name": "fastapi",
  "description": "FastAPI framework",
  "language": "Python",
  "stars": 100000,
  "repo_url": "https://github.com/fastapi/fastapi",
  "created_at": "2026-06-03T10:00:00",
  "updated_at": "2026-06-03T10:00:00"
}
```

### Possible Responses

| Status | Description                             |
| ------ | --------------------------------------- |
| 201    | Repository created successfully         |
| 404    | Repository does not exist on GitHub     |
| 409    | Repository already exists in database   |
| 422    | Invalid GitHub URL                      |
| 502    | GitHub API returned an unexpected error |
| 503    | GitHub API unavailable or timeout       |

---

## GET /repositories/{id}

Returns a repository stored in the local database.

### Path Parameter

| Parameter | Type    | Description |
| --------- | ------- | ----------- |
| id        | integer | Database ID |

### Example Request

```http
GET /repositories/1
```

### Success Response

**200 OK**

```json
{
  "id": 1,
  "github_id": 123456,
  "name": "fastapi",
  "description": "FastAPI framework",
  "language": "Python",
  "stars": 100000,
  "repo_url": "https://github.com/fastapi/fastapi",
  "created_at": "2026-06-03T10:00:00",
  "updated_at": "2026-06-03T10:00:00"
}
```

### Possible Responses

| Status | Description                  |
| ------ | ---------------------------- |
| 200    | Repository found             |
| 404    | Repository ID does not exist |

---

## PUT /repositories/{id}

Refreshes repository metadata from GitHub and updates the stored record.

### Path Parameter

| Parameter | Type    | Description |
| --------- | ------- | ----------- |
| id        | integer | Database ID |

### Example Request

```http
PUT /repositories/1
```

### Success Response

**200 OK**

```json
{
  "id": 1,
  "github_id": 123456,
  "name": "fastapi",
  "description": "FastAPI framework",
  "language": "Python",
  "stars": 100250,
  "repo_url": "https://github.com/fastapi/fastapi",
  "created_at": "2026-06-03T10:00:00",
  "updated_at": "2026-06-03T11:00:00"
}
```

### Possible Responses

| Status | Description                                         |
| ------ | --------------------------------------------------- |
| 200    | Repository refreshed successfully                   |
| 404    | Repository not found locally or removed from GitHub |
| 502    | GitHub API returned an error                        |
| 503    | GitHub API unavailable or timeout                   |

---

## DELETE /repositories/{id}

Deletes a repository from the local database.

### Path Parameter

| Parameter | Type    | Description |
| --------- | ------- | ----------- |
| id        | integer | Database ID |

### Example Request

```http
DELETE /repositories/1
```

### Success Response

**204 No Content**

Response body is empty.

### Possible Responses

| Status | Description                     |
| ------ | ------------------------------- |
| 204    | Repository deleted successfully |
| 404    | Repository not found            |

---

## Validation Rules

The repository URL is validated at the schema layer before any database or external API interaction occurs.

### Accepted Format

```json
{
  "url": "https://github.com/owner/repository"
}
```

### Rejected Examples

Wrong Domain:

```json
{
  "url": "https://gitlab.com/user/project"
}
```

Malformed URL:

```json
{
  "url": "abc123"
}
```

Missing Repository Name:

```json
{
  "url": "https://github.com/owner"
}
```

### Validation Response

**422 Unprocessable Entity**

```json
{
  "detail": [
    {
      "loc": ["body", "url"],
      "msg": "Invalid GitHub repository URL",
      "type": "value_error"
    }
  ]
}
```

---

## Error Response Format

Application errors follow a consistent structure:

```json
{
  "success": false,
  "data": null,
  "error": "Repository not found"
}
```

Common errors include:

* Repository not found
* Repository already exists
* Invalid GitHub URL
* External API unavailable
* External API timeout
* Upstream GitHub API failure

```
```



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# 7. Design Decisions

## 1. GitHub REST API Integration

I chose the GitHub REST API because it provides reliable repository metadata, stable documentation, and a simple URL structure that is easy to validate.

### Benefits

* Well-documented API
* Rich repository metadata
* Supports authenticated and unauthenticated requests
* Stable JSON responses

### Trade-off

GitHub enforces rate limits on unauthenticated requests. Optional token-based authentication can be added to reduce this limitation.

---



## 2. Async-First Architecture

The application uses:

* FastAPI
* SQLAlchemy Async ORM
* asyncpg
* httpx.AsyncClient

### Benefits

* Non-blocking I/O operations
* Better scalability under concurrent requests
* Aligns with FastAPI best practices

### Trade-off

Async code is slightly more complex than synchronous code and requires async-compatible libraries.

---

## 3. Layered Architecture

The project is separated into:

* API Layer
* Service Layer
* Data Layer

### Benefits

* Separation of concerns
* Easier maintenance
* Better testability
* Cleaner code organization

### Trade-off

More files and abstraction compared to a single-file implementation.

---

## 4. Database-Level Uniqueness

Duplicate repositories are prevented using a UNIQUE database constraint rather than relying solely on application logic.

### Benefits

* Prevents race conditions
* Guarantees data integrity
* Satisfies assessment requirements

### Trade-off

Constraint violations must be converted into user-friendly API responses.

---

## 5. Global Exception Handling

A centralized exception handling layer converts application exceptions into consistent HTTP responses.

### Benefits

* Consistent error format
* Cleaner route handlers
* Easier maintenance

### Trade-off

Requires additional exception classes and handler configuration.

---

## 6. Dedicated PostgreSQL Test Database

Integration tests run against a completely separate PostgreSQL database rather than the development database.

### Benefits

* Prevents accidental modification of development data
* Provides realistic database testing
* Improves test reliability
* Supports repeatable test execution

### Trade-off

Requires maintaining an additional database specifically for testing.

---

## 6. Dependency Version Pinning

All dependencies are pinned to exact versions in `requirements.txt` using:

```bash
pip freeze > requirements.txt
```

### Trade-off

Dependencies must be updated manually when newer versions are required.



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# 8. Assumptions

During development, the following assumptions were made where requirements were open to interpretation:

1. A GitHub repository URL is the only accepted input format for repository creation.

Example:

https://github.com/owner/repository

Other formats such as repository IDs or GitHub API URLs are rejected.

---

2. Repository uniqueness is determined using GitHub's repository ID rather than repository name.

This ensures uniqueness even if a repository is renamed.

---

3. The GET endpoint must read only from the local PostgreSQL database and never trigger external GitHub API calls.

This follows the assessment specification.

---

4. GitHub authentication is optional because the repository endpoints used by this project are publicly accessible.

The application can operate without authentication but may be subject to GitHub rate limits.

---

5. Metadata returned by GitHub is treated as the source of truth.

The PUT endpoint refreshes stored data by re-fetching metadata from GitHub and replacing the existing values.

---

6. Only public GitHub repositories are supported.

Repositories that are private, inaccessible, or restricted by GitHub permissions are treated as unavailable resources.

---

7. Only selected repository metadata is stored locally.

The application stores only the fields required by the service:

* GitHub ID
* Repository Name
* Description
* Primary Language
* Star Count
* Repository URL

The complete GitHub API response is not persisted in the database.

```
```



----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------







# 9. Troubleshooting

## 1. Database Session Already Closed Error

### Error

During development and testing, database operations occasionally failed because sessions were being closed or reused incorrectly.

Typical symptoms included:

* Session already closed
* Transaction errors
* Failed commits or rollbacks

### Solution

Database session management was centralized using FastAPI dependency injection:

```python
async def override_get_session():
    async with TestingSessionLocal() as session:
        yield session
```

This ensures each request receives a fresh session and that sessions are cleaned up correctly after use.

---

## 2. Integration Tests Affecting Development Data

### Error

Initially, integration tests were running against the development database.

This caused:

* Test data mixing with development data
* Duplicate repository conflicts
* Unpredictable test results

### Solution

A dedicated PostgreSQL test database was created:

```text
github_tracker_test
```

FastAPI dependencies were overridden during testing so all test requests use the isolated database.

```python
app.dependency_overrides[get_session] = override_get_session
```

---

## 3. Test Data Persisting Between Test Runs

### Error

Records created by one test remained in the database and affected subsequent tests.

Symptoms included:

* Duplicate key errors
* Unexpected test failures
* Inconsistent results

### Solution

The repositories table is automatically cleaned before every test:

```sql
TRUNCATE TABLE repositories
RESTART IDENTITY CASCADE;
```

This guarantees complete isolation between tests.

---

## 4. Docker Cannot Connect to PostgreSQL

### Error

The FastAPI container failed to connect to PostgreSQL when using:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yashwanth@localhost:5432/github_tracker
```

Inside Docker, `localhost` refers to the container itself rather than the PostgreSQL container.

### Solution

Use the Docker service name instead:

```env
DATABASE_URL=postgresql+asyncpg://postgres:yashwanth@db:5432/github_tracker
```

Where:

```yaml
services:
  db:
    image: postgres:16
```

Docker Compose automatically creates a network where containers can communicate using service names.

---

## 5. Missing Database Tables

### Error

Application startup succeeded but database operations failed because tables had not yet been created.

Typical error:

```text
relation "repositories" does not exist
```

### Solution

Initialize the database before starting the application:

```bash
python create_tables.py
```

This creates all required tables using SQLAlchemy ORM models.

---

## 6. First-Time Pytest Configuration Issues

### Error

While setting up pytest for the first time, tests failed because the testing environment was not isolated correctly.

Issues included:

* Dependency override problems
* Database contamination between tests
* Fixture configuration errors

### Solution

The test environment was configured using:

* Dedicated test database
* Dependency overrides
* Automatic schema creation
* Automatic table cleanup
* Async test client

This ensures tests are repeatable and independent.

---
