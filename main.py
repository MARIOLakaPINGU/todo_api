from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="To-Do List API",
    version="1.0.0",
    description="A simple demo REST API for managing to-dos. Uses in-memory storage."
)

# ---------- Pydantic models ----------
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None

class Todo(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    completed: bool = False

# ---------- In-memory "DB" ----------
todos: Dict[int, Todo] = {}

def _next_id() -> int:
    return (max(todos.keys()) + 1) if todos else 1

# ---------- Routes ----------
@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.post(
    "/todos",
    response_model=Todo,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new to-do",
    tags=["todos"]
)
def create_todo(payload: TodoCreate):
    todo_id = _next_id()
    todo = Todo(id=todo_id, **payload.dict())
    todos[todo_id] = todo
    return todo

@app.get(
    "/todos",
    response_model=List[Todo],
    summary="List all to-dos",
    tags=["todos"]
)
def list_todos():
    return list(todos.values())

@app.get(
    "/todos/{todo_id}",
    response_model=Todo,
    summary="Get a single to-do",
    tags=["todos"]
)
def get_todo(todo_id: int):
    todo = todos.get(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="To-do not found")
    return todo

@app.put(
    "/todos/{todo_id}",
    response_model=Todo,
    summary="Update a to-do (partial allowed)",
    tags=["todos"]
)
def update_todo(todo_id: int, updates: TodoUpdate):
    existing = todos.get(todo_id)
    if not existing:
        raise HTTPException(status_code=404, detail="To-do not found")
    data = existing.dict()
    data.update(updates.dict(exclude_unset=True))
    updated = Todo(**data)
    todos[todo_id] = updated
    return updated

@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a to-do",
    tags=["todos"]
)
def delete_todo(todo_id: int):
    if todo_id not in todos:
        raise HTTPException(status_code=404, detail="To-do not found")
    del todos[todo_id]
    return None
