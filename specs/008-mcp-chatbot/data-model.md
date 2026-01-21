# Data Model: MCP-Based Chatbot System

**Feature**: 008-mcp-chatbot
**Date**: 2026-01-20
**Status**: Phase 1 Complete

---

## Entity Relationship Diagram

```
User (existing)
  ├── 1:N → Session (new)
  │           ├── 1:N → Message (new)
  └── 1:N → Task (existing)
```

**Key Relationships**:
- One User has many Sessions (independent conversations)
- One Session has many Messages (chronological message history)
- One User has many Tasks (global across all sessions)
- Tasks are NOT scoped to sessions (user can manage tasks from any chat session)

---

## Entity: Session (NEW)

### Purpose
Represents an independent conversation instance between a user and the chatbot. Each session maintains its own message history and can have different language settings.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `session_id` | UUID | PRIMARY KEY, AUTO-GENERATED | Unique session identifier |
| `user_id` | UUID | FOREIGN KEY → User.id, NOT NULL | Session owner (for data isolation) |
| `title` | VARCHAR(255) | NOT NULL | Session title (auto-generated from first message) |
| `language` | VARCHAR(2) | NOT NULL, DEFAULT 'en', CHECK IN ('en', 'ur') | Preferred language for this session |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Session creation timestamp |
| `last_activity_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last message timestamp (for cleanup) |

### Indexes

```sql
CREATE INDEX idx_session_user_id ON session(user_id);
CREATE INDEX idx_session_last_activity ON session(last_activity_at DESC);
```

**Index Rationale**:
- `idx_session_user_id`: Fast lookup of user's sessions (list sessions endpoint)
- `idx_session_last_activity`: Efficient cleanup queries (delete inactive sessions)

### Relationships

- **User → Session**: One-to-Many (one user can have multiple sessions)
  - Foreign Key: `session.user_id → user.id`
  - Cascade: ON DELETE CASCADE (delete sessions when user is deleted)

- **Session → Message**: One-to-Many (one session contains many messages)
  - Foreign Key: `message.session_id → session.session_id`
  - Cascade: ON DELETE CASCADE (delete messages when session is deleted)

### Validation Rules

1. **title**: 1-255 characters (enforced at app and DB level)
2. **language**: Must be 'en' or 'ur' (CHECK constraint)
3. **user_id**: Must reference existing User (foreign key constraint)
4. **last_activity_at**: Must be >= created_at (application-level check)

### SQLModel Schema

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class Session(SQLModel, table=True):
    __tablename__ = "session"

    session_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    language: str = Field(default="en", max_length=2, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    last_activity_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Validation
    def __post_init__(self):
        if self.language not in ("en", "ur"):
            raise ValueError("Language must be 'en' or 'ur'")
        if len(self.title) < 1 or len(self.title) > 255:
            raise ValueError("Title must be 1-255 characters")
```

### Business Rules

1. **Session Creation**: Lazy creation on first message (see research.md)
2. **Title Generation**: Auto-generated from first user message (truncated to 50 chars, append "...")
3. **Language Detection**: Can be set explicitly or detected from first message
4. **Session Cleanup**: Sessions with last_activity_at > 30 days are deleted (background job)
5. **Ownership**: Users can ONLY access their own sessions (verified by user_id from JWT)

### Example Data

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": "u1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Shopping list planning",
  "language": "en",
  "created_at": "2026-01-20T14:30:00Z",
  "last_activity_at": "2026-01-20T15:45:00Z"
}
```

---

## Entity: Message (NEW)

### Purpose
Represents an individual chat message in a conversation. Messages are ordered chronologically within a session and can be from either the user or the AI assistant.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `message_id` | UUID | PRIMARY KEY, AUTO-GENERATED | Unique message identifier |
| `session_id` | UUID | FOREIGN KEY → Session.session_id, NOT NULL | Parent session |
| `role` | VARCHAR(10) | NOT NULL, CHECK IN ('user', 'assistant') | Message sender |
| `content` | TEXT | NOT NULL | Message text (max 5000 chars app-level) |
| `language` | VARCHAR(2) | NOT NULL, DEFAULT 'en', CHECK IN ('en', 'ur') | Message language |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Message creation timestamp |

### Indexes

```sql
CREATE INDEX idx_message_session_id ON message(session_id);
CREATE INDEX idx_message_created_at ON message(created_at DESC);
CREATE INDEX idx_message_session_created ON message(session_id, created_at DESC);
```

**Index Rationale**:
- `idx_message_session_id`: Fast lookup of messages by session
- `idx_message_created_at`: Efficient sorting for chronological order
- `idx_message_session_created`: Composite index for optimal conversation history queries

### Relationships

- **Session → Message**: Many-to-One (many messages belong to one session)
  - Foreign Key: `message.session_id → session.session_id`
  - Cascade: ON DELETE CASCADE (when session deleted, messages deleted)

### Validation Rules

1. **role**: Must be 'user' or 'assistant' (CHECK constraint)
2. **content**: 1-5000 characters (enforced at app level before insert)
3. **language**: Must be 'en' or 'ur' (CHECK constraint)
4. **session_id**: Must reference existing Session (foreign key constraint)

### SQLModel Schema

```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Literal

class Message(SQLModel, table=True):
    __tablename__ = "message"

    message_id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="session.session_id", nullable=False, index=True)
    role: Literal["user", "assistant"] = Field(nullable=False)
    content: str = Field(nullable=False)
    language: str = Field(default="en", max_length=2, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)

    # Validation
    def __post_init__(self):
        if self.role not in ("user", "assistant"):
            raise ValueError("Role must be 'user' or 'assistant'")
        if self.language not in ("en", "ur"):
            raise ValueError("Language must be 'en' or 'ur'")
        if len(self.content) < 1 or len(self.content) > 5000:
            raise ValueError("Content must be 1-5000 characters")
```

### Business Rules

1. **Message Insertion**: ALWAYS insert user message AND assistant message together (atomic transaction)
2. **Ordering**: Messages retrieved in chronological order (ORDER BY created_at ASC)
3. **Context Building**: Last 50 messages fetched for MCP context (see research.md)
4. **Language Inheritance**: If not specified, inherit from session.language
5. **User Isolation**: Messages only accessible via session (session already user-scoped)

### Example Data

```json
[
  {
    "message_id": "m1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "role": "user",
    "content": "Add buy groceries to my tasks",
    "language": "en",
    "created_at": "2026-01-20T14:30:00Z"
  },
  {
    "message_id": "m2b2c3d4-e5f6-7890-abcd-ef1234567890",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "role": "assistant",
    "content": "I've added 'buy groceries' to your tasks.",
    "language": "en",
    "created_at": "2026-01-20T14:30:02Z"
  },
  {
    "message_id": "m3b2c3d4-e5f6-7890-abcd-ef1234567890",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "role": "user",
    "content": "میرے کام دکھائیں",
    "language": "ur",
    "created_at": "2026-01-20T14:31:00Z"
  },
  {
    "message_id": "m4b2c3d4-e5f6-7890-abcd-ef1234567890",
    "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "role": "assistant",
    "content": "آپ کا ایک کام ہے: خریداری کریں",
    "language": "ur",
    "created_at": "2026-01-20T14:31:02Z"
  }
]
```

---

## Entity: User (EXISTING - UPDATED)

### Purpose
Represents an authenticated user of the application. This entity already exists from Phase II; we're adding a new field for language preference.

### New Field

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `language_preference` | VARCHAR(2) | DEFAULT 'en', CHECK IN ('en', 'ur') | User's preferred UI language |

### Migration SQL

```sql
ALTER TABLE "user"
ADD COLUMN language_preference VARCHAR(2) DEFAULT 'en' CHECK (language_preference IN ('en', 'ur'));
```

### Updated SQLModel Schema

```python
class User(SQLModel, table=True):
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, nullable=False, index=True)
    name: str = Field(max_length=255, nullable=True)
    hashed_password: str = Field(max_length=255, nullable=False)
    language_preference: str = Field(default="en", max_length=2, nullable=False)  # NEW
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Business Rules

1. **Default Language**: New users default to 'en' (English)
2. **Language Switching**: Users can change preference via settings (updates user.language_preference)
3. **Session Language**: New sessions inherit user.language_preference (but can be overridden per session)
4. **Persistence**: Language preference persists across sessions and devices

### Rationale

Storing language preference at the user level (in addition to session level) provides:
- **Convenience**: New sessions automatically use user's preferred language
- **Consistency**: UI language matches user preference across all pages
- **Flexibility**: Individual sessions can still use different languages (e.g., practicing Urdu)

---

## Entity: Task (EXISTING - NO CHANGES)

### Purpose
Represents a todo task. This entity already exists from Phase II and requires NO changes for the chatbot feature.

### Existing Schema

```python
class Task(SQLModel, table=True):
    __tablename__ = "todo"  # Note: table name is 'todo' not 'task'

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False, index=True)
    title: str = Field(max_length=255, nullable=False)
    description: str = Field(default="", nullable=True)
    completed: bool = Field(default=False, nullable=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False, index=True)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
```

### Integration with Chatbot

- **MCP Tools Access**: MCP tools (add_task, list_tasks, complete_task, delete_task) query this table with user_id filtering
- **User Isolation**: All task operations filtered by user_id extracted from JWT (security-critical)
- **Global Scope**: Tasks are NOT tied to specific chat sessions (user can manage all tasks from any session)

### Example MCP Tool Query

```python
# MCP tool: list_tasks
def list_tasks(user_id: UUID, completed: bool | None = None):
    query = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        query = query.where(Task.completed == completed)

    tasks = db.exec(query.order_by(Task.created_at.desc())).all()
    return tasks
```

---

## Database Migration Plan

### Migration Order

1. **Migration 003**: Add Session and Message tables
   - Create `session` table with indexes
   - Create `message` table with indexes
   - Add `language_preference` column to `user` table

### Migration 003 SQL

```sql
-- File: alembic/versions/003_add_session_message_tables.py

-- Add language_preference to user table
ALTER TABLE "user"
ADD COLUMN language_preference VARCHAR(2) DEFAULT 'en' CHECK (language_preference IN ('en', 'ur'));

-- Create session table
CREATE TABLE session (
  session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  language VARCHAR(2) NOT NULL DEFAULT 'en' CHECK (language IN ('en', 'ur')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  last_activity_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_session_user_id ON session(user_id);
CREATE INDEX idx_session_last_activity ON session(last_activity_at DESC);

-- Create message table
CREATE TABLE message (
  message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID NOT NULL REFERENCES session(session_id) ON DELETE CASCADE,
  role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  language VARCHAR(2) NOT NULL DEFAULT 'en' CHECK (language IN ('en', 'ur')),
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_message_session_id ON message(session_id);
CREATE INDEX idx_message_created_at ON message(created_at DESC);
CREATE INDEX idx_message_session_created ON message(session_id, created_at DESC);
```

### Rollback Strategy

```sql
-- Rollback Migration 003
DROP TABLE IF EXISTS message CASCADE;
DROP TABLE IF EXISTS session CASCADE;
ALTER TABLE "user" DROP COLUMN IF EXISTS language_preference;
```

---

## Performance Considerations

### Query Optimization

**Most Frequent Query** (fetch conversation history):
```sql
SELECT *
FROM message
WHERE session_id = $1
ORDER BY created_at DESC
LIMIT 50;
```

**Optimization**:
- Composite index on (session_id, created_at DESC) enables index-only scan
- LIMIT 50 keeps result set small
- Expected query time: <50ms for typical session

**Second Most Frequent Query** (list user sessions):
```sql
SELECT *
FROM session
WHERE user_id = $1
ORDER BY last_activity_at DESC
LIMIT 20;
```

**Optimization**:
- Index on user_id enables fast user filtering
- Index on last_activity_at enables efficient sorting
- Expected query time: <30ms for typical user

### Storage Estimates

**Assumptions**:
- 1,000 active users
- Average 5 sessions per user
- Average 20 messages per session
- Average message length: 200 characters

**Storage Calculation**:

| Entity | Count | Size per Row | Total Size |
|--------|-------|--------------|------------|
| User | 1,000 | ~500 bytes | ~500 KB |
| Session | 5,000 | ~300 bytes | ~1.5 MB |
| Message | 100,000 | ~400 bytes | ~40 MB |
| Task | ~5,000 | ~400 bytes | ~2 MB |
| **Total** | | | **~44 MB** |

**Conclusion**: Database storage is minimal even with 1,000 users. Neon Serverless PostgreSQL can handle this easily.

### Connection Pooling

```python
# Database connection pool configuration
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,  # Max 10 concurrent connections
    max_overflow=10,  # Allow 10 additional connections if pool exhausted
    pool_timeout=30,  # Wait max 30s for connection
    pool_recycle=3600  # Recycle connections every hour
)
```

**Rationale**:
- 10 concurrent connections sufficient for 100 users (each request < 200ms)
- Max overflow handles traffic spikes
- Pool recycle prevents stale connections

---

## Security Considerations

### Data Isolation

**Critical Principle**: EVERY query MUST filter by authenticated user_id

**Session Access Control**:
```python
def get_session(session_id: UUID, current_user_id: UUID, db: Session) -> Session:
    session = db.get(Session, session_id)

    # Security check: user owns session
    if not session or session.user_id != current_user_id:
        raise HTTPException(status_code=404, detail="Session not found")

    return session
```

**Message Access Control**:
```python
def get_messages(session_id: UUID, current_user_id: UUID, db: Session) -> list[Message]:
    # First verify session ownership
    session = get_session(session_id, current_user_id, db)

    # Then fetch messages (session ownership already verified)
    messages = db.exec(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(50)
    ).all()

    return messages
```

### SQL Injection Prevention

**SQLModel ORM** automatically parameterizes queries:
```python
# ✅ SAFE - SQLModel uses parameterized queries
db.exec(select(Message).where(Message.session_id == user_provided_id))

# ❌ UNSAFE - Never use string formatting
db.exec(f"SELECT * FROM message WHERE session_id = '{user_provided_id}'")
```

### Sensitive Data Handling

- **Message Content**: May contain sensitive information (task details, personal data)
  - NOT encrypted at rest (relies on PostgreSQL SSL and Neon security)
  - Encrypted in transit (SSL/TLS enforced)
  - Access controlled by user_id filtering

- **Session Titles**: Auto-generated from first message (may be sensitive)
  - User can manually update title to remove sensitive info (future feature)

---

## Validation Summary

### Database-Level Validation

| Field | Validation | Enforcement |
|-------|------------|-------------|
| Session.language | IN ('en', 'ur') | CHECK constraint |
| Message.role | IN ('user', 'assistant') | CHECK constraint |
| Message.language | IN ('en', 'ur') | CHECK constraint |
| Session.user_id | EXISTS in User | FOREIGN KEY |
| Message.session_id | EXISTS in Session | FOREIGN KEY |

### Application-Level Validation

| Field | Validation | Enforcement |
|-------|------------|-------------|
| Session.title | 1-255 chars | Pydantic model |
| Message.content | 1-5000 chars | Pydantic model |
| Session.last_activity_at | >= created_at | Business logic |

---

## Completion Checklist

- ✅ Entity: Session defined with all fields, indexes, relationships
- ✅ Entity: Message defined with all fields, indexes, relationships
- ✅ Entity: User updated with language_preference field
- ✅ Entity: Task reviewed (no changes needed)
- ✅ SQLModel schemas provided for all entities
- ✅ Migration SQL written for Session, Message tables
- ✅ Indexes optimized for common queries
- ✅ Security considerations documented
- ✅ Performance estimates calculated
- ✅ Validation rules defined at DB and app levels

**Status**: Phase 1 Data Model Complete ✅
