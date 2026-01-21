# Implementation Plan: MCP-Based Chatbot System

**Branch**: `008-mcp-chatbot` | **Date**: 2026-01-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-mcp-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a stateless MCP-based chatbot system with natural language task management supporting English and Urdu. The system maintains NO server-side conversation state—all context is rebuilt from the database on each request. The chatbot communicates with an MCP (Model Context Protocol) server to access AI intelligence and execute tools (task CRUD operations). Users can interact via text chat with proper RTL rendering for Urdu, and the system maintains multiple independent sessions per user with conversation persistence for 30+ days.

## Technical Context

**Language/Version**:
- Frontend: TypeScript 5+ with Next.js 16+ (App Router)
- Backend: Python 3.13+ with FastAPI
- MCP Server: Python 3.13+ with MCP SDK

**Primary Dependencies**:
- Frontend: Next.js 16+, Better Auth (JWT), next-intl (i18n), Tailwind CSS 3.4+, Framer Motion 10+
- Backend: FastAPI, SQLModel (Pydantic + SQLAlchemy), python-jose (JWT), Uvicorn (ASGI server)
- MCP: anthropic-mcp-sdk, openai/anthropic client libraries
- Database: Neon Serverless PostgreSQL (via SQLModel)

**Storage**:
- PostgreSQL with 4 tables: User, Session, Message, Task
- All conversation history persisted in Message table with session_id + user_id
- Tasks stored globally per user (not session-scoped)
- Indexes on: user_id, session_id, created_at for performance

**Testing**:
- Frontend: Jest + React Testing Library (component, integration)
- Backend: pytest with fixtures (unit, integration, security)
- E2E: Playwright for critical user flows
- MCP: pytest with mock MCP client
- Target: 80%+ coverage

**Target Platform**:
- Frontend: Vercel (Node.js 18+, serverless deployment)
- Backend: Render/Railway (Python 3.13+, Docker container)
- Database: Neon Serverless PostgreSQL (cloud-native, SSL required)
- MCP Server: Same backend infrastructure (STDIO or REST transport)

**Project Type**: web (frontend + backend + MCP server)

**Performance Goals**:
- API response time: <3 seconds (95th percentile) for chatbot messages
- Database query: <100ms for conversation history fetch (50 messages)
- MCP tool execution: <2 seconds for task operations
- Frontend TTI: <3 seconds on 3G network
- Support 100 concurrent users without degradation

**Constraints**:
- Stateless architecture: NO in-memory conversation state between requests
- Conversation context: Maximum 50 message pairs to maintain performance
- Message length: Maximum 5,000 characters per message
- Session retention: Minimum 30 days from last activity
- Language detection: Automatic switching between English and Urdu
- RTL rendering: Proper right-to-left text for Urdu (Noto Nastaliq Urdu font)
- JWT expiration: Access token 30min, refresh token 7 days
- User isolation: Complete data separation per user_id
- Security: All endpoints validate JWT and enforce user scoping

**Scale/Scope**:
- MVP: 100 concurrent users
- Conversation history: 50 message pairs (100 messages) per session
- Multiple sessions per user (unlimited)
- Task count: Unlimited per user
- Expected avg session length: 10-20 message pairs
- Database connection pool: Max 20 connections
- API rate limiting: Future consideration (not in MVP)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Stateless Server Architecture (MANDATORY)
**Compliance**: FULL COMPLIANCE
- Server holds NO conversation state in memory ✅
- Every request rebuilds context from database ✅
- All messages persisted before responding ✅
- MCP server stateless communication ✅

**Implementation**:
```python
# Every chatbot request follows this flow:
1. Receive user message with session_id + user_id (from JWT)
2. Fetch conversation history from DB (SELECT * FROM messages WHERE session_id=...)
3. Build context array: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
4. Send context + new message to MCP server
5. Receive MCP response (with tool calls if needed)
6. Store user message AND assistant response in DB
7. Return response to frontend
8. Server memory is cleared (no state retained)
```

### ✅ II. Spec-Driven Development (MANDATORY)
**Compliance**: FULL COMPLIANCE
- Workflow: Specification (✅ spec.md exists) → Plan (✅ this document) → Tasks (next: /sp.tasks) → Implementation (/sp.implement) ✅
- All features begin with `/sp.specify` ✅
- Changes require spec amendment via `/sp.clarify` ✅

### ✅ III. Agent-First Design (MANDATORY)
**Compliance**: FULL COMPLIANCE
- MCP tools are ONLY way agents interact with data ✅
- No direct database access bypassing MCP ✅
- Sub-agents isolated and composable ✅

**Agent Delegation Plan**:
1. **database-architect**: Session, Message table schema design + migrations
2. **backend-api-guardian**: Chatbot API endpoint (/api/chat), MCP client integration, stateless request flow
3. **frontend-builder**: Chat UI components, RTL support, language toggle, message rendering
4. **auth-config-specialist**: JWT validation in chatbot context (reuse existing Better Auth)
5. **urdu-translator**: Urdu language detection, RTL rendering verification, translation validation

### ✅ IV. Reusable Intelligence (SKILLS-FIRST)
**Compliance**: FULL COMPLIANCE

**Skills to Consult**:
- **API Skill**: JWT attachment for chatbot requests, error handling for MCP failures
- **Database Skill**: Message CRUD with user_id filtering, pagination for history loading
- **Auth Skill**: JWT validation for /api/chat endpoint
- **UI Skill**: Chat message components, loading indicators, RTL layouts

**New Skills to Create** (during implementation):
- **MCP Skill** (`.claude/skills/mcp.skill.md`): MCP client initialization, tool registration, request formatting, error handling, stateless context building
- **Chatbot Skill** (`.claude/skills/chatbot.skill.md`): Conversation history fetching, context window management, natural language intent detection, response formatting

### ✅ V. Multilingual Support (English + Urdu)
**Compliance**: FULL COMPLIANCE
- next-intl for frontend localization ✅
- RTL rendering with Noto Nastaliq Urdu font ✅
- Language detection and switching ✅
- Urdu intent recognition in MCP system prompts ✅

**Implementation**:
- Language preference stored in User table
- Message table has `language` field (en/ur)
- Frontend detects language and applies RTL CSS dynamically
- MCP system prompt includes Urdu command examples

### ✅ VI. Security-First Development (CRITICAL)
**Compliance**: FULL COMPLIANCE

**Authentication Flow**:
```
User sends chat message (JWT in Authorization header)
        ↓
/api/chat validates JWT signature
        ↓
Extract user_id from 'sub' claim
        ↓
Fetch session (WHERE session_id=... AND user_id=current_user_id)
        ↓
If session not found or user_id mismatch → 404
        ↓
Fetch messages (WHERE session_id=... ORDER BY created_at)
        ↓
Send to MCP with user_id context
        ↓
MCP tools filter by user_id (e.g., list tasks WHERE user_id=...)
        ↓
Store response with session_id + user_id
        ↓
Return to frontend
```

**Security Rules Enforced**:
- JWT validation on /api/chat endpoint ✅
- Session ownership verification (session.user_id == current_user_id) ✅
- Message queries filtered by session_id (already scoped to user) ✅
- Task MCP tools filter by user_id from JWT ✅
- Return 404 for unauthorized session access ✅

### ✅ VII. Test-Driven Development (TDD)
**Compliance**: FULL COMPLIANCE
- Tests written BEFORE implementation ✅
- Red-Green-Refactor cycle ✅
- 80%+ coverage target ✅

**Test Suites**:
1. **Backend Unit Tests** (`backend/tests/unit/`):
   - test_chatbot_service.py: Conversation history fetching, context building
   - test_mcp_client.py: MCP request formatting, tool call handling
   - test_message_repository.py: Message CRUD with user scoping

2. **Backend Integration Tests** (`backend/tests/integration/`):
   - test_chat_api.py: /api/chat endpoint with JWT, stateless verification
   - test_mcp_integration.py: End-to-end MCP communication

3. **Frontend Unit Tests** (`frontend/__tests__/unit/`):
   - ChatMessage.test.tsx: Message rendering, RTL verification
   - ChatInput.test.tsx: Message sending, language detection

4. **Frontend Integration Tests** (`frontend/__tests__/integration/`):
   - ChatFlow.test.tsx: Full conversation flow with mock API

5. **E2E Tests** (`frontend/__tests__/e2e/`):
   - chat.spec.ts: User sends message → receives response → history persisted

### ✅ VIII. Observability and Debugging
**Compliance**: FULL COMPLIANCE
- Structured logging for all API requests ✅
- MCP tool calls logged ✅
- Database queries logged ✅
- Error tracking with stack traces (sanitized in prod) ✅

**Logging Strategy**:
```python
logger.info("Chat request", extra={
    "user_id": current_user_id,
    "session_id": session_id,
    "message_length": len(user_message),
    "conversation_history_count": len(history)
})

logger.info("MCP request", extra={
    "user_id": current_user_id,
    "context_messages": len(context),
    "tools_available": ["add_task", "list_tasks", ...]
})

logger.info("MCP response", extra={
    "user_id": current_user_id,
    "response_length": len(response),
    "tool_calls": [call.name for call in tool_calls]
})
```

### 🟡 Additional Constitution Checks

**Package Management**: UV (MANDATORY) ✅
- All Python dependencies via `uv` ✅
- Frontend via `pnpm` ✅

**API Architecture**: REST Standards ✅
- /api/chat endpoint follows constitution patterns ✅
- Proper status codes, error responses ✅

**Database Schema**: Multi-Tenant Isolation ✅
- Session table: user_id foreign key ✅
- Message table: session_id foreign key (inherits user_id isolation) ✅
- Indexes on user_id, session_id ✅

### Constitution Check Summary

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Stateless Architecture | ✅ PASS | Core design principle—all state in DB |
| II. Spec-Driven Development | ✅ PASS | Following workflow: spec → plan → tasks → implement |
| III. Agent-First Design | ✅ PASS | MCP tools enforce data access patterns |
| IV. Reusable Intelligence | ✅ PASS | Consulting existing skills + creating new MCP/Chatbot skills |
| V. Multilingual Support | ✅ PASS | English + Urdu with RTL rendering |
| VI. Security-First | ✅ PASS | JWT validation, user scoping, session ownership verification |
| VII. Test-Driven Development | ✅ PASS | Tests before implementation, 80%+ coverage |
| VIII. Observability | ✅ PASS | Structured logging for all MCP interactions |

**GATE DECISION**: ✅ **PROCEED TO PHASE 0**

## Project Structure

### Documentation (this feature)

```text
specs/008-mcp-chatbot/
├── spec.md              # ✅ Created by /sp.specify
├── plan.md              # ✅ This file (created by /sp.plan)
├── research.md          # Phase 0 output (created by /sp.plan) - NEXT
├── data-model.md        # Phase 1 output (created by /sp.plan)
├── quickstart.md        # Phase 1 output (created by /sp.plan)
├── contracts/           # Phase 1 output (created by /sp.plan)
│   ├── chat-api.yaml    # OpenAPI spec for /api/chat endpoint
│   └── mcp-tools.yaml   # MCP tool definitions (task management)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (frontend + backend + MCP server)

backend/
├── app/
│   ├── main.py                    # FastAPI app entry point
│   ├── models.py                  # SQLModel database models (User, Task, Session, Message)
│   ├── schemas.py                 # Pydantic request/response models
│   ├── database.py                # Database connection and session management
│   ├── auth.py                    # JWT validation utilities (reused from Phase II)
│   ├── dependencies.py            # FastAPI dependencies (get_current_user, get_db)
│   ├── mcp/                       # NEW: MCP integration
│   │   ├── __init__.py
│   │   ├── client.py              # MCP client initialization and communication
│   │   ├── tools.py               # MCP tool definitions (add_task, list_tasks, etc.)
│   │   ├── context.py             # Context building from conversation history
│   │   └── server.py              # MCP server setup (STDIO or REST transport)
│   ├── services/                  # NEW: Business logic layer
│   │   ├── __init__.py
│   │   ├── chatbot_service.py     # Chatbot request orchestration (stateless flow)
│   │   ├── message_service.py     # Message CRUD operations
│   │   └── session_service.py     # Session management
│   └── routers/
│       ├── auth.py                # Auth endpoints (existing from Phase II)
│       ├── todos.py               # Todo endpoints (existing from Phase II)
│       └── chat.py                # NEW: Chatbot endpoint (/api/chat)
├── alembic/                       # Database migrations
│   ├── versions/
│   │   └── 003_add_session_message_tables.py  # NEW migration
├── tests/
│   ├── unit/
│   │   ├── test_chatbot_service.py
│   │   ├── test_mcp_client.py
│   │   ├── test_message_service.py
│   │   └── test_session_service.py
│   ├── integration/
│   │   ├── test_chat_api.py
│   │   └── test_mcp_integration.py
│   └── conftest.py                # pytest fixtures
├── pyproject.toml                 # UV dependencies
└── .env.example                   # Environment variable template

frontend/
├── app/
│   ├── (auth)/                    # Auth pages (existing)
│   ├── (dashboard)/
│   │   ├── layout.tsx             # Dashboard layout (existing)
│   │   ├── page.tsx               # Todo list page (existing)
│   │   └── chat/                  # NEW: Chat interface
│   │       ├── page.tsx           # Main chat page
│   │       └── [sessionId]/
│   │           └── page.tsx       # Session-specific chat view
│   ├── api/
│   │   └── chat/
│   │       └── route.ts           # NEW: Next.js API route proxy to backend
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/                        # Reusable UI components (existing)
│   ├── layouts/                   # Layout components (existing)
│   └── chat/                      # NEW: Chat-specific components
│       ├── ChatWindow.tsx         # Main chat container
│       ├── ChatMessage.tsx        # Individual message display (supports RTL)
│       ├── ChatInput.tsx          # Message input field with language detection
│       ├── SessionList.tsx        # List of user's chat sessions
│       ├── LanguageToggle.tsx     # English/Urdu switcher
│       └── TypingIndicator.tsx    # Loading state during MCP processing
├── lib/
│   ├── api.ts                     # API client (existing)
│   ├── auth.ts                    # Auth utilities (existing)
│   ├── chat-api.ts                # NEW: Chat-specific API client
│   └── utils.ts
├── hooks/
│   ├── useChat.ts                 # NEW: Chat state management hook
│   ├── useSession.ts              # NEW: Session management hook
│   └── useLanguage.ts             # NEW: Language preference hook
├── types/
│   ├── todo.ts                    # Existing
│   └── chat.ts                    # NEW: Chat types (Message, Session, ChatRequest, ChatResponse)
├── messages/
│   ├── en.json                    # English translations (extended)
│   └── ur.json                    # NEW: Urdu translations
└── __tests__/
    ├── unit/
    │   ├── ChatMessage.test.tsx
    │   └── ChatInput.test.tsx
    ├── integration/
    │   └── ChatFlow.test.tsx
    └── e2e/
        └── chat.spec.ts

.claude/
└── skills/
    ├── api.skill.md               # Existing
    ├── database.skill.md          # Existing
    ├── auth.skill.md              # Existing
    ├── ui.skill.md                # Existing
    ├── mcp.skill.md               # NEW: MCP client patterns, tool registration, error handling
    └── chatbot.skill.md           # NEW: Conversation history, context management, intent detection
```

**Structure Decision**: Selected **Web application** structure (Option 2 from template) because this feature extends the existing Next.js frontend + FastAPI backend architecture with MCP server integration. The MCP server runs within the same backend infrastructure (as a Python module) and communicates via STDIO or REST transport. This maintains architectural consistency with Phase II while adding the chatbot layer.

## Complexity Tracking

> **This section is intentionally empty** because there are NO constitution violations requiring justification. All design decisions comply with the 8 core principles and additional standards.

---

## Phase 0: Outline & Research

**Objective**: Resolve all "NEEDS CLARIFICATION" items from Technical Context and research MCP integration patterns.

### Research Tasks

1. **MCP SDK Integration Research**
   - **Question**: How to initialize MCP client in FastAPI backend?
   - **Research**: Review anthropic-mcp-sdk documentation, client initialization patterns, transport options (STDIO vs REST)
   - **Output**: MCP client setup guide with code examples

2. **Stateless Context Building Research**
   - **Question**: How to efficiently rebuild conversation context from database on each request?
   - **Research**: Context window management strategies, message truncation patterns, performance optimization
   - **Output**: Context building algorithm with performance benchmarks

3. **MCP Tool Definition Research**
   - **Question**: How to define task management tools in MCP server?
   - **Research**: MCP tool schema format, parameter validation, error handling patterns
   - **Output**: Tool definition template with validation rules

4. **Urdu Language Support in MCP Research**
   - **Question**: How to ensure MCP server handles Urdu text correctly?
   - **Research**: LLM Urdu capabilities, system prompt patterns for multilingual support, intent detection accuracy
   - **Output**: Urdu system prompt template with command examples

5. **Session Management Research**
   - **Question**: How to manage multiple concurrent sessions per user efficiently?
   - **Research**: Session creation strategies, session title generation, session cleanup policies
   - **Output**: Session lifecycle management guide

6. **RTL Rendering Best Practices Research**
   - **Question**: How to implement proper RTL support in Next.js?
   - **Research**: CSS RTL patterns, next-intl RTL configuration, Urdu font loading
   - **Output**: RTL implementation checklist with CSS snippets

### Expected Outputs (research.md)

After research, `specs/008-mcp-chatbot/research.md` will contain:

- **MCP Integration Decision**: STDIO transport (simpler for same-server deployment) vs REST transport (better for distributed systems)
- **Context Management Strategy**: Fetch last 50 messages, reverse chronological order, truncate older messages with summary
- **Tool Definition Pattern**: JSON schema with strict parameter validation, error codes for failures
- **Urdu Support Strategy**: Include Urdu command examples in system prompt, test with Claude/GPT-4 Urdu capabilities
- **Session Management**: Auto-generate titles from first user message, 30-day retention, lazy session creation
- **RTL Rendering**: CSS `dir="rtl"` attribute, Tailwind RTL utilities, Noto Nastaliq Urdu via Google Fonts

---

## Phase 1: Design & Contracts

**Prerequisites**: research.md complete with all decisions documented

### 1.1 Data Model (`data-model.md`)

#### Entity: Session
- **Purpose**: Independent conversation instance per user
- **Fields**:
  - `session_id` (UUID, PRIMARY KEY): Unique session identifier
  - `user_id` (UUID, FOREIGN KEY → User.id, NOT NULL): Session owner
  - `title` (VARCHAR(255), NOT NULL): Auto-generated from first message
  - `language` (VARCHAR(2), DEFAULT 'en'): Preferred language (en/ur)
  - `created_at` (TIMESTAMP, DEFAULT NOW())
  - `last_activity_at` (TIMESTAMP, DEFAULT NOW()): Updated on each message
- **Indexes**:
  - `idx_session_user_id` ON (user_id)
  - `idx_session_last_activity` ON (last_activity_at DESC)
- **Relationships**:
  - One-to-Many with Message (one session has many messages)
  - Many-to-One with User (many sessions belong to one user)
- **Validation**:
  - title: 1-255 characters
  - language: enum ['en', 'ur']
  - user_id: Must reference existing User

#### Entity: Message
- **Purpose**: Individual chat message in a conversation
- **Fields**:
  - `message_id` (UUID, PRIMARY KEY): Unique message identifier
  - `session_id` (UUID, FOREIGN KEY → Session.session_id, NOT NULL, ON DELETE CASCADE): Parent session
  - `role` (VARCHAR(10), NOT NULL): 'user' or 'assistant'
  - `content` (TEXT, NOT NULL): Message text (max 5000 chars enforced at app level)
  - `language` (VARCHAR(2), DEFAULT 'en'): Message language (en/ur)
  - `created_at` (TIMESTAMP, DEFAULT NOW())
- **Indexes**:
  - `idx_message_session_id` ON (session_id)
  - `idx_message_created_at` ON (created_at DESC)
- **Relationships**:
  - Many-to-One with Session (many messages belong to one session)
- **Validation**:
  - role: enum ['user', 'assistant']
  - content: 1-5000 characters
  - language: enum ['en', 'ur']
  - session_id: Must reference existing Session

#### Entity Updates: User (Existing)
- **New Field**: `language_preference` (VARCHAR(2), DEFAULT 'en'): User's preferred UI language
- **Rationale**: Store user preference for persistent language selection across sessions

#### Entity: Task (Existing - No Changes)
- Task entity remains unchanged from Phase II
- MCP tools will query tasks with user_id filtering

### 1.2 API Contracts (`contracts/`)

#### File: `contracts/chat-api.yaml` (OpenAPI 3.0)

```yaml
openapi: 3.0.0
info:
  title: Chatbot API
  version: 1.0.0
paths:
  /api/chat:
    post:
      summary: Send a chat message and receive AI response
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - message
                - session_id
              properties:
                message:
                  type: string
                  maxLength: 5000
                  example: "Add buy groceries to my tasks"
                session_id:
                  type: string
                  format: uuid
                  example: "123e4567-e89b-12d3-a456-426614174000"
                language:
                  type: string
                  enum: [en, ur]
                  default: en
      responses:
        200:
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  response:
                    type: string
                    example: "I've added 'buy groceries' to your tasks."
                  tool_calls:
                    type: array
                    items:
                      type: object
                      properties:
                        tool:
                          type: string
                        result:
                          type: object
        400:
          description: Invalid input (message too long, invalid session_id)
        401:
          description: Missing or invalid JWT
        404:
          description: Session not found or user does not own session
        500:
          description: MCP server error or database failure

  /api/chat/sessions:
    get:
      summary: List all sessions for authenticated user
      security:
        - BearerAuth: []
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: page_size
          in: query
          schema:
            type: integer
            default: 20
            maximum: 100
      responses:
        200:
          description: Session list
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      $ref: '#/components/schemas/Session'
                  total:
                    type: integer
                  page:
                    type: integer
                  page_size:
                    type: integer

    post:
      summary: Create a new chat session
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                title:
                  type: string
                  maxLength: 255
                  example: "Shopping List Planning"
                language:
                  type: string
                  enum: [en, ur]
                  default: en
      responses:
        201:
          description: Session created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Session'

  /api/chat/sessions/{session_id}/messages:
    get:
      summary: Get conversation history for a session
      security:
        - BearerAuth: []
      parameters:
        - name: session_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
        - name: limit
          in: query
          schema:
            type: integer
            default: 50
            maximum: 100
        - name: before
          in: query
          description: Fetch messages before this message_id (pagination)
          schema:
            type: string
            format: uuid
      responses:
        200:
          description: Message list
          content:
            application/json:
              schema:
                type: object
                properties:
                  messages:
                    type: array
                    items:
                      $ref: '#/components/schemas/Message'
                  has_more:
                    type: boolean
        404:
          description: Session not found or unauthorized

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    Session:
      type: object
      properties:
        session_id:
          type: string
          format: uuid
        user_id:
          type: string
          format: uuid
        title:
          type: string
        language:
          type: string
          enum: [en, ur]
        created_at:
          type: string
          format: date-time
        last_activity_at:
          type: string
          format: date-time

    Message:
      type: object
      properties:
        message_id:
          type: string
          format: uuid
        session_id:
          type: string
          format: uuid
        role:
          type: string
          enum: [user, assistant]
        content:
          type: string
        language:
          type: string
          enum: [en, ur]
        created_at:
          type: string
          format: date-time
```

#### File: `contracts/mcp-tools.yaml` (MCP Tool Definitions)

```yaml
mcp_tools:
  - name: add_task
    description: Create a new task for the user
    input_schema:
      type: object
      required:
        - title
      properties:
        title:
          type: string
          description: Task title
          maxLength: 255
        description:
          type: string
          description: Optional task description
          maxLength: 1000
    output_schema:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
        title:
          type: string
        completed:
          type: boolean
        created_at:
          type: string
          format: date-time

  - name: list_tasks
    description: List all tasks for the user with optional filtering
    input_schema:
      type: object
      properties:
        completed:
          type: boolean
          description: Filter by completion status (optional)
    output_schema:
      type: object
      properties:
        tasks:
          type: array
          items:
            type: object
            properties:
              task_id:
                type: string
                format: uuid
              title:
                type: string
              description:
                type: string
              completed:
                type: boolean
              created_at:
                type: string
                format: date-time

  - name: complete_task
    description: Mark a task as completed
    input_schema:
      type: object
      required:
        - task_id
      properties:
        task_id:
          type: string
          format: uuid
          description: ID of the task to complete
    output_schema:
      type: object
      properties:
        task_id:
          type: string
          format: uuid
        completed:
          type: boolean

  - name: delete_task
    description: Delete a task permanently
    input_schema:
      type: object
      required:
        - task_id
      properties:
        task_id:
          type: string
          format: uuid
          description: ID of the task to delete
    output_schema:
      type: object
      properties:
        success:
          type: boolean
        deleted_task_id:
          type: string
          format: uuid

system_prompt: |
  You are a helpful task management assistant supporting both English and Urdu languages.

  Your capabilities:
  - Add tasks: "Add buy groceries" or "نیا کام: دودھ خریدنا"
  - List tasks: "Show my tasks" or "میرے کام دکھائیں"
  - Complete tasks: "Complete groceries task" or "مکمل کریں: دودھ"
  - Delete tasks: "Delete groceries" or "حذف کریں: دودھ"

  Guidelines:
  - Detect user intent from natural language
  - Ask for clarification when intent is ambiguous
  - Provide friendly, concise responses
  - Support both English and Urdu seamlessly
  - When user mentions a task by title (partial match ok), infer the task_id
  - Confirm actions after executing tools

  Error handling:
  - If tool call fails, explain to user in simple language
  - Suggest alternatives when tasks not found
  - Don't expose technical error details
```

### 1.3 Quickstart Guide (`quickstart.md`)

```markdown
# Quickstart: MCP-Based Chatbot System

## Prerequisites
- Node.js 18+ (frontend)
- Python 3.13+ (backend)
- PostgreSQL database (Neon recommended)
- UV package manager installed
- Existing Phase II setup (Better Auth, Todo API)

## Setup Steps

### 1. Backend Setup

#### Install Dependencies
```bash
cd backend
uv add anthropic-mcp-sdk openai  # or anthropic for Claude
```

#### Environment Variables
Add to `backend/.env`:
```env
# Existing variables...
MCP_TRANSPORT=stdio  # or 'rest' for distributed setup
OPENAI_API_KEY=sk-...  # or ANTHROPIC_API_KEY
```

#### Run Migrations
```bash
uv run alembic revision --autogenerate -m "Add session and message tables"
uv run alembic upgrade head
```

#### Start Backend
```bash
uv run uvicorn app.main:app --reload
```

### 2. Frontend Setup

#### Install Dependencies
```bash
cd frontend
pnpm add @formatjs/intl-localematcher negotiator
```

#### Add Urdu Translations
Create `frontend/messages/ur.json`:
```json
{
  "chat": {
    "title": "چیٹ",
    "input_placeholder": "پیغام لکھیں...",
    "send": "بھیجیں"
  }
}
```

#### Configure i18n
Update `frontend/i18n.ts` to include 'ur' locale.

#### Start Frontend
```bash
pnpm dev
```

### 3. Test the Chatbot

1. Navigate to `http://localhost:3000/chat`
2. Send: "Add buy groceries to my tasks"
3. Verify response: "I've added 'buy groceries' to your tasks."
4. Send: "Show my tasks"
5. Verify task list is displayed

### 4. Test Urdu Support

1. Click language toggle → Select Urdu
2. Send: "نیا کام: دودھ خریدنا"
3. Verify RTL rendering and Urdu response
4. Send: "میرے کام دکھائیں"
5. Verify tasks displayed in Urdu

## Architecture Overview

```
User → Frontend (Next.js) → /api/chat endpoint → Backend (FastAPI)
                                                       ↓
                                         Fetch conversation history (DB)
                                                       ↓
                                         Build context array
                                                       ↓
                                         MCP Client → MCP Server → LLM
                                                       ↓
                                         Execute tools (add_task, list_tasks...)
                                                       ↓
                                         Store user + assistant messages (DB)
                                                       ↓
                                         Return response → Frontend
```

## Troubleshooting

**Issue**: "Session not found"
- **Solution**: Ensure session_id is created before sending messages. Use POST /api/chat/sessions first.

**Issue**: "MCP server timeout"
- **Solution**: Check LLM API key is valid. Increase timeout in MCP client config.

**Issue**: "Urdu text not rendering"
- **Solution**: Verify Noto Nastaliq Urdu font loaded. Check `dir="rtl"` attribute applied.

## Next Steps

- Run `/sp.tasks` to generate implementation tasks
- Run `/sp.implement` to execute tasks with specialized agents
- Review tests with `pytest backend/tests/` and `pnpm test`
```

### 1.4 Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Expected Result**:
- Adds "MCP SDK integration", "Stateless chatbot architecture", "Urdu RTL rendering" to Claude's technology context
- Preserves existing manual additions
- Updates context file with new capabilities

---

## Constitution Check Re-Evaluation (Post-Design)

### Phase 1 Design Compliance Review

| Principle | Pre-Design | Post-Design | Changes |
|-----------|------------|-------------|---------|
| I. Stateless Architecture | ✅ PASS | ✅ PASS | Design enforces: fetch history → build context → call MCP → store messages |
| II. Spec-Driven | ✅ PASS | ✅ PASS | All artifacts created per spec (data-model, contracts, quickstart) |
| III. Agent-First | ✅ PASS | ✅ PASS | MCP tools defined; no direct DB access in chatbot logic |
| IV. Reusable Intelligence | ✅ PASS | ✅ PASS | MCP Skill and Chatbot Skill planned for creation |
| V. Multilingual | ✅ PASS | ✅ PASS | RTL CSS, Urdu system prompt, language field in Session/Message tables |
| VI. Security-First | ✅ PASS | ✅ PASS | JWT validation on /api/chat, session ownership verification, user_id filtering in MCP tools |
| VII. TDD | ✅ PASS | ✅ PASS | Test suites defined for all layers (unit, integration, E2E) |
| VIII. Observability | ✅ PASS | ✅ PASS | Logging strategy defined for MCP requests/responses, conversation history fetches |

**FINAL GATE DECISION**: ✅ **PROCEED TO PHASE 2 (TASKS)**

No violations introduced. All design decisions strengthen constitutional compliance.

---

## Summary & Next Steps

### What Was Delivered

**Phase 0** (Research - To Be Generated):
- `research.md` with MCP integration decisions, context management strategy, Urdu support plan

**Phase 1** (Design - To Be Generated):
- ✅ `data-model.md`: Session + Message entities with validation rules
- ✅ `contracts/chat-api.yaml`: OpenAPI spec for /api/chat endpoint
- ✅ `contracts/mcp-tools.yaml`: MCP tool definitions with system prompt
- ✅ `quickstart.md`: Setup guide with troubleshooting

**Phase 1 Execution**:
- Agent context updated with new technologies

### Architectural Decisions

1. **Stateless Request Flow**: Every /api/chat request rebuilds full context from database (no in-memory state)
2. **MCP STDIO Transport**: Simpler for same-server deployment; MCP server runs as Python module in backend
3. **Session Scoping**: Messages scoped to session_id; tasks scoped to user_id (global across sessions)
4. **Context Truncation**: Fetch last 50 messages for performance; older messages summarized if needed
5. **Urdu Support**: Language field in Session/Message; RTL via CSS `dir` attribute; Urdu commands in system prompt
6. **Tool Execution**: MCP server executes tools synchronously; results embedded in assistant response
7. **Error Handling**: MCP failures return user-friendly messages; technical errors logged but not exposed

### Risk Mitigation

| Risk | Mitigation |
|------|------------|
| MCP latency > 2s | Optimize context size; implement streaming responses in future |
| Urdu NLP accuracy | Include extensive Urdu examples in system prompt; test with Claude/GPT-4 |
| Database load (frequent writes) | Use connection pooling; batch message inserts if needed |
| Context window limits | Truncate to 50 messages; implement smart summarization for older context |
| Session isolation bugs | Comprehensive security tests; verify session ownership on every request |

### Command to Execute Next

```bash
/sp.tasks
```

This will generate `specs/008-mcp-chatbot/tasks.md` with:
- Story-based task organization (matching user stories from spec)
- TDD tasks (write tests first)
- Parallel execution where possible
- Acceptance criteria linked to spec scenarios
- Agent delegation (database-architect, backend-api-guardian, frontend-builder, etc.)

---

**Branch**: `008-mcp-chatbot`
**Plan Status**: ✅ COMPLETE
**Ready for**: `/sp.tasks` command
