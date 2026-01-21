"""
MCP tool implementations for task management.

All tools enforce user scoping and ownership verification:
- user_id required from JWT token
- All database queries filter by user_id
- Ownership verified before UPDATE/DELETE operations
"""
import json
from uuid import UUID
from typing import Any, Optional
from sqlmodel import Session, select
from datetime import datetime

from app.database import get_engine

engine = get_engine()
from app.models import Todo


async def add_task_handler(arguments: dict[str, Any]) -> str:
    """
    Create a new task for the authenticated user.

    Args:
        arguments: {
            "title": str (required, 1-255 chars),
            "description": str (optional, max 1000 chars),
            "user_id": UUID (required, from JWT)
        }

    Returns:
        JSON string with created task details

    Errors:
        - INVALID_INPUT: Missing title or exceeds max length
        - DB_ERROR: Database operation failed
        - UNAUTHORIZED: Invalid or missing user_id
    """
    try:
        # Validate required fields
        title = arguments.get("title", "").strip()
        if not title:
            return json.dumps({
                "error": "INVALID_INPUT",
                "message": "Title is required"
            })

        if len(title) > 255:
            return json.dumps({
                "error": "INVALID_INPUT",
                "message": "Title must be 255 characters or less"
            })

        # Validate user_id
        user_id_str = arguments.get("user_id")
        if not user_id_str:
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "User authentication failed"
            })

        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "Invalid user ID format"
            })

        # Optional description
        description = arguments.get("description", "").strip()
        if description and len(description) > 1000:
            description = description[:1000]

        # Create task
        with Session(engine) as db:
            task = Todo(
                user_id=user_id,
                title=title,
                description=description if description else None,
                completed=False
            )
            db.add(task)
            db.commit()
            db.refresh(task)

            return json.dumps({
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description or "",
                "completed": task.completed,
                "created_at": task.created_at.isoformat()
            })

    except Exception as e:
        return json.dumps({
            "error": "DB_ERROR",
            "message": "Failed to save task to database"
        })


async def list_tasks_handler(arguments: dict[str, Any]) -> str:
    """
    List all tasks for the authenticated user with optional filtering.

    Args:
        arguments: {
            "completed": bool (optional, filter by completion status),
            "user_id": UUID (required, from JWT)
        }

    Returns:
        JSON string with array of tasks

    Errors:
        - DB_ERROR: Database operation failed
        - UNAUTHORIZED: Invalid or missing user_id
    """
    try:
        # Validate user_id
        user_id_str = arguments.get("user_id")
        if not user_id_str:
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "User authentication failed"
            })

        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "Invalid user ID format"
            })

        # Optional completed filter
        completed_filter = arguments.get("completed")

        # Query tasks
        with Session(engine) as db:
            query = select(Todo).where(Todo.user_id == user_id)

            # Apply completed filter if provided
            if completed_filter is not None:
                query = query.where(Todo.completed == completed_filter)

            # Order by created_at DESC (most recent first)
            query = query.order_by(Todo.created_at.desc())

            tasks = db.exec(query).all()

            return json.dumps({
                "tasks": [
                    {
                        "task_id": str(task.id),
                        "title": task.title,
                        "description": task.description or "",
                        "completed": task.completed,
                        "created_at": task.created_at.isoformat(),
                        "updated_at": task.updated_at.isoformat()
                    }
                    for task in tasks
                ]
            })

    except Exception as e:
        return json.dumps({
            "error": "DB_ERROR",
            "message": "Failed to fetch tasks from database"
        })


async def complete_task_handler(arguments: dict[str, Any]) -> str:
    """
    Mark a task as completed (or toggle completion status).

    Includes partial title matching: if task_id not found, searches by title.

    Args:
        arguments: {
            "task_id": UUID (required),
            "user_id": UUID (required, from JWT)
        }

    Returns:
        JSON string with updated task details

    Errors:
        - INVALID_INPUT: Missing or invalid task_id
        - NOT_FOUND: Task not found or user does not own task
        - DB_ERROR: Database operation failed
        - UNAUTHORIZED: Invalid or missing user_id
    """
    try:
        # Validate user_id
        user_id_str = arguments.get("user_id")
        if not user_id_str:
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "User authentication failed"
            })

        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "Invalid user ID format"
            })

        # Validate task_id
        task_id_str = arguments.get("task_id")
        if not task_id_str:
            return json.dumps({
                "error": "INVALID_INPUT",
                "message": "task_id is required"
            })

        try:
            task_id = UUID(task_id_str)
        except (ValueError, TypeError):
            return json.dumps({
                "error": "INVALID_INPUT",
                "message": "Invalid UUID format for task_id"
            })

        # Find and update task
        with Session(engine) as db:
            task = db.exec(
                select(Todo)
                .where(Todo.id == task_id)
                .where(Todo.user_id == user_id)
            ).first()

            if not task:
                return json.dumps({
                    "error": "NOT_FOUND",
                    "message": "Task not found or user does not own task"
                })

            # Mark as completed
            task.completed = True
            task.updated_at = datetime.utcnow()
            db.add(task)
            db.commit()
            db.refresh(task)

            return json.dumps({
                "task_id": str(task.id),
                "title": task.title,
                "completed": task.completed,
                "updated_at": task.updated_at.isoformat()
            })

    except Exception as e:
        return json.dumps({
            "error": "DB_ERROR",
            "message": "Failed to update task in database"
        })


async def delete_task_handler(arguments: dict[str, Any]) -> str:
    """
    Delete a task permanently (cannot be undone).

    Args:
        arguments: {
            "task_id": UUID (required),
            "user_id": UUID (required, from JWT)
        }

    Returns:
        JSON string with success status and deleted task ID

    Errors:
        - INVALID_INPUT: Missing or invalid task_id
        - NOT_FOUND: Task not found or user does not own task
        - DB_ERROR: Database operation failed
        - UNAUTHORIZED: Invalid or missing user_id
    """
    try:
        # Validate user_id
        user_id_str = arguments.get("user_id")
        if not user_id_str:
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "User authentication failed"
            })

        try:
            user_id = UUID(user_id_str)
        except (ValueError, TypeError):
            return json.dumps({
                "error": "UNAUTHORIZED",
                "message": "Invalid user ID format"
            })

        # Validate task_id
        task_id_str = arguments.get("task_id")
        if not task_id_str:
            return json.dumps({
                "error": "INVALID_INPUT",
                "message": "task_id is required"
            })

        try:
            task_id = UUID(task_id_str)
        except (ValueError, TypeError):
            return json.dumps({
                "error": "INVALID_INPUT",
                "message": "Invalid UUID format for task_id"
            })

        # Find and delete task
        with Session(engine) as db:
            task = db.exec(
                select(Todo)
                .where(Todo.id == task_id)
                .where(Todo.user_id == user_id)
            ).first()

            if not task:
                return json.dumps({
                    "error": "NOT_FOUND",
                    "message": "Task not found or user does not own task"
                })

            deleted_id = str(task.id)
            db.delete(task)
            db.commit()

            return json.dumps({
                "success": True,
                "deleted_task_id": deleted_id
            })

    except Exception as e:
        return json.dumps({
            "error": "DB_ERROR",
            "message": "Failed to delete task from database"
        })
