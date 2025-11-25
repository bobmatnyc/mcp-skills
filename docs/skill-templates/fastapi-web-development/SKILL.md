---
name: FastAPI Modern Web Development
skill_id: fastapi-web-development
version: 1.0.0
description: Production-grade FastAPI development with async patterns, Pydantic v2, dependency injection, ML/AI endpoint design, and modern Python best practices for building high-performance REST APIs
category: Python Web Development
tags:
  - fastapi
  - python
  - async
  - pydantic
  - rest-api
  - ml-endpoints
  - dependency-injection
  - web-framework
  - async-programming
  - api-design
author: mcp-skillset
license: MIT
created: 2025-11-25
last_updated: 2025-11-25
toolchain:
  - Python 3.11+
  - FastAPI 0.100+
  - Pydantic v2
  - uvicorn
  - httpx
frameworks:
  - FastAPI
  - Pydantic
  - SQLAlchemy 2.0
  - Alembic
related_skills:
  - test-driven-development
  - systematic-debugging
  - postgresql-optimization
  - security-testing
---

# FastAPI Modern Web Development

## Overview

This skill provides comprehensive guidance for building production-grade FastAPI applications with modern Python patterns (2024-2025 best practices). FastAPI is the #1 framework for AI/ML APIs, combining high performance, automatic OpenAPI documentation, and intuitive async/await patterns.

## When to Use This Skill

Use this skill when:
- Building RESTful APIs for ML/AI services
- Creating high-performance async Python web services
- Developing data-intensive applications requiring concurrent request handling
- Implementing microservices with automatic API documentation
- Building APIs that require strong type safety and validation
- Designing endpoints for LLM integration and AI workflows

## Core Principles

### 1. Async-First Architecture
**Always prefer async/await for I/O-bound operations**

```python
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

app = FastAPI()

# CORRECT: Async database operations
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()

# CORRECT: Async external API calls
@app.get("/external-data")
async def fetch_external():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# WRONG: Blocking synchronous calls in async context
@app.get("/bad-example")
async def bad_handler():
    time.sleep(5)  # Blocks entire event loop!
    return {"status": "done"}
```

**Why**: FastAPI runs on ASGI (asyncio). Blocking calls prevent other requests from processing, degrading performance under load.

### 2. Pydantic v2 Models for Type Safety
**Use Pydantic models for all request/response validation**

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    """Request model for user creation"""
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: Optional[int] = Field(None, ge=13, le=120)

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

class UserResponse(BaseModel):
    """Response model - never expose internal fields"""
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2

    id: int
    username: str
    email: str
    created_at: datetime
    # DON'T expose: password_hash, internal_flags, etc.

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = User(**user.model_dump())  # Pydantic v2 syntax
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

**Key Updates for Pydantic v2**:
- `Config` → `model_config = ConfigDict(...)`
- `orm_mode=True` → `from_attributes=True`
- `dict()` → `model_dump()`
- `@validator` → `@field_validator`

### 3. Dependency Injection for Loose Coupling
**Use FastAPI's dependency injection for reusable components**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Database session dependency
async_engine = create_async_engine("postgresql+asyncpg://...")
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Authentication dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    user = await db.get(User, payload.get("sub"))
    if user is None:
        raise credentials_exception
    return user

# Use dependencies in route
@app.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

**Benefits**: Automatic injection, easy testing with override_dependency, shared logic across routes.

### 4. Structured Error Handling
**Always use HTTPException with proper status codes**

```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Item, item_id)

    # CORRECT: Specific HTTP exception
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )

    if not item.is_public and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return item

# Custom exception handler for domain errors
class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request, exc: ItemNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item {exc.item_id} not found"}
    )
```

### 5. ML/AI Endpoint Design Patterns
**Optimize endpoints for ML model serving**

```python
from fastapi import BackgroundTasks
from functools import lru_cache
import asyncio

# Singleton pattern for model loading
@lru_cache()
def get_ml_model():
    """Load model once, cache for all requests"""
    import torch
    model = torch.load("model.pth")
    model.eval()
    return model

class PredictionRequest(BaseModel):
    text: str = Field(..., max_length=10000)
    temperature: float = Field(0.7, ge=0.0, le=2.0)

class PredictionResponse(BaseModel):
    prediction: str
    confidence: float
    processing_time_ms: float

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    model = get_ml_model()

    start_time = asyncio.get_event_loop().time()

    # Run CPU-intensive model inference in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,  # Uses default ThreadPoolExecutor
        model.predict,
        request.text
    )

    elapsed = (asyncio.get_event_loop().time() - start_time) * 1000

    return PredictionResponse(
        prediction=result["text"],
        confidence=result["score"],
        processing_time_ms=elapsed
    )

# Background task for async processing
@app.post("/predict-async")
async def predict_async(
    request: PredictionRequest,
    background_tasks: BackgroundTasks
):
    task_id = generate_task_id()
    background_tasks.add_task(process_prediction, task_id, request)
    return {"task_id": task_id, "status": "processing"}
```

## Best Practices

### Application Structure
```
fastapi-project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, startup/shutdown events
│   ├── config.py            # Pydantic Settings management
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/             # Pydantic models (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   └── items.py
│   │   └── deps.py          # Shared dependencies
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── ml_service.py
│   ├── core/                # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── database.py
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       └── test_users.py
├── alembic/                 # Database migrations
├── .env
├── pyproject.toml
└── README.md
```

### Configuration Management
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://localhost/dbname"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "My FastAPI Project"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# Use in dependencies
@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {"project_name": settings.PROJECT_NAME}
```

### Request Lifecycle & Middleware
```python
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time
import logging

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logging.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s "
        f"with status {response.status_code}"
    )

    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Common Patterns

### Pagination
```python
from typing import Generic, TypeVar, Sequence
from pydantic import BaseModel

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int

async def paginate(
    query,
    page: int = 1,
    size: int = 50
) -> Page[T]:
    total = await db.scalar(select(func.count()).select_from(query))
    items = await db.scalars(
        query.offset((page - 1) * size).limit(size)
    )

    return Page(
        items=items.all(),
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )

@app.get("/users", response_model=Page[UserResponse])
async def list_users(
    page: int = 1,
    size: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(User).order_by(User.created_at.desc())
    return await paginate(query, page, size)
```

### File Upload with Validation
```python
from fastapi import File, UploadFile
from PIL import Image
import aiofiles

@app.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    # Validate file size (10MB limit)
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")

    # Validate image can be opened
    try:
        image = Image.open(BytesIO(contents))
        image.verify()
    except Exception:
        raise HTTPException(400, "Invalid image file")

    # Save file asynchronously
    file_path = f"uploads/{file.filename}"
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(contents)

    return {"filename": file.filename, "size": len(contents)}
```

### WebSocket for Real-Time Updates
```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

## Anti-Patterns to Avoid

### ❌ DON'T: Mix sync and async incorrectly
```python
# WRONG: Sync function in async route
@app.get("/bad")
async def bad_endpoint():
    result = sync_database_call()  # Blocks event loop!
    return result

# CORRECT: Use run_in_executor for sync calls
@app.get("/good")
async def good_endpoint():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, sync_database_call)
    return result
```

### ❌ DON'T: Return ORM models directly
```python
# WRONG: Exposes internal fields, risks lazy loading
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await db.get(User, user_id)  # Returns ORM model!

# CORRECT: Use Pydantic response model
@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    return user  # FastAPI converts to UserResponse
```

### ❌ DON'T: Hardcode configuration
```python
# WRONG: Hardcoded values
DATABASE_URL = "postgresql://localhost/db"

# CORRECT: Use Pydantic Settings
settings = get_settings()
DATABASE_URL = settings.DATABASE_URL
```

### ❌ DON'T: Ignore startup/shutdown events
```python
# CORRECT: Cleanup resources
@app.on_event("startup")
async def startup():
    # Initialize database pool, load ML models, etc.
    app.state.db = await create_db_pool()

@app.on_event("shutdown")
async def shutdown():
    # Close connections, cleanup
    await app.state.db.close()
```

## Testing Strategy

```python
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

# Sync tests with TestClient
def test_create_user():
    client = TestClient(app)
    response = client.post(
        "/users",
        json={"username": "testuser", "email": "test@example.com"}
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

# Async tests with httpx
@pytest.mark.asyncio
async def test_async_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/1")
        assert response.status_code == 200

# Override dependencies for testing
def override_get_db():
    return test_database_session

app.dependency_overrides[get_db] = override_get_db
```

## Performance Optimization

1. **Connection Pooling**: Use SQLAlchemy async engine with pool_size=20, max_overflow=0
2. **Response Caching**: Use Redis with `@lru_cache()` for expensive computations
3. **Background Tasks**: Offload non-critical work to BackgroundTasks
4. **Async Libraries**: Use httpx (not requests), asyncpg (not psycopg2)
5. **Profiling**: Use `uvicorn --log-level debug` and timing middleware

## Security Checklist

- ✅ Use HTTPS in production (via reverse proxy)
- ✅ Implement rate limiting (slowapi library)
- ✅ Validate all inputs with Pydantic models
- ✅ Use OAuth2 with JWT for authentication
- ✅ Never expose internal error details in production
- ✅ Set proper CORS origins (not `["*"]` in production)
- ✅ Hash passwords with bcrypt or argon2
- ✅ Use `SECRET_KEY` from environment, never hardcode

## Related Skills

- **test-driven-development**: Write tests before implementing endpoints
- **systematic-debugging**: Debug async issues and race conditions
- **postgresql-optimization**: Optimize database queries for FastAPI
- **security-testing**: Perform security audits on API endpoints

## Additional Resources

- FastAPI Official Docs: https://fastapi.tiangolo.com
- Pydantic v2 Migration: https://docs.pydantic.dev/latest/migration/
- SQLAlchemy 2.0 Async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Production Deployment: https://fastapi.tiangolo.com/deployment/

## Example Questions to Ask

- "How do I implement JWT authentication in FastAPI?"
- "What's the best way to handle file uploads asynchronously?"
- "How do I optimize this endpoint for ML model inference?"
- "Show me how to add pagination to this query"
- "How do I write async tests for FastAPI endpoints?"
- "What's the correct way to handle database transactions?"
