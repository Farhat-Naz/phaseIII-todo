# Quickstart: MCP-Based Chatbot System

**Feature**: 008-mcp-chatbot
**Date**: 2026-01-20
**Prerequisites**: Phase II complete (Better Auth + Todo API)

---

## Prerequisites

Before starting, ensure you have:

✅ **Node.js 18+** (for frontend)
✅ **Python 3.13+** (for backend)
✅ **PostgreSQL database** (Neon recommended)
✅ **UV package manager** installed
✅ **Existing Phase II setup** (Better Auth, Todo API)
✅ **LLM API Key** (OpenAI or Anthropic)

---

## Setup Steps

### 1. Backend Setup

#### 1.1 Install Dependencies

```bash
cd backend

# Add MCP SDK and LLM client
uv add mcp anthropic  # OR: uv add mcp openai

# Verify installation
uv run python -c "import mcp; print('MCP SDK installed successfully')"
```

#### 1.2 Environment Variables

Add to `backend/.env`:

```env
# Existing variables (from Phase II)...

# MCP Configuration
MCP_TRANSPORT=stdio  # or 'rest' for distributed setup
ANTHROPIC_API_KEY=sk-ant-...  # OR OPENAI_API_KEY=sk-...

# Chatbot Configuration (optional)
CHATBOT_MAX_CONTEXT_MESSAGES=50
CHATBOT_MAX_MESSAGE_LENGTH=5000
```

**Get your API key**:
- **Anthropic**: https://console.anthropic.com/
- **OpenAI**: https://platform.openai.com/api-keys

#### 1.3 Database Migrations

```bash
cd backend

# Generate migration for new tables
uv run alembic revision --autogenerate -m "Add session and message tables"

# Review the generated migration file in alembic/versions/
# Verify it contains: Session table, Message table, User.language_preference

# Apply migration
uv run alembic upgrade head

# Verify tables created
uv run python -c "
from app.database import engine
from sqlmodel import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT table_name FROM information_schema.tables WHERE table_schema = \\'public\\''))
    tables = [row[0] for row in result]
    print('Tables:', tables)
    assert 'session' in tables, 'Session table not created'
    assert 'message' in tables, 'Message table not created'
    print('✅ Database migration successful!')
"
```

#### 1.4 Start Backend

```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output**:
```
INFO:     Will watch for changes in these directories: ['D:\\phaseIII-todoapp\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify backend**:
- Open http://localhost:8000/docs (FastAPI interactive API docs)
- Check for new endpoints: `/api/chat`, `/api/chat/sessions`

---

### 2. Frontend Setup

#### 2.1 Install Dependencies

```bash
cd frontend

# Add i18n dependencies for multilingual support
pnpm add @formatjs/intl-localematcher negotiator

# Add Google Fonts integration (for Urdu font)
# Note: next/font/google is built-in with Next.js 13+

# Verify installation
pnpm list | grep intl
```

#### 2.2 Add Urdu Translations

Create `frontend/messages/ur.json`:

```json
{
  "nav": {
    "home": "ہوم",
    "todos": "کام",
    "chat": "چیٹ",
    "profile": "پروفائل",
    "logout": "لاگ آؤٹ"
  },
  "chat": {
    "title": "چیٹ",
    "new_session": "نیا چیٹ",
    "sessions": "چیٹ سیشنز",
    "input_placeholder": "پیغام لکھیں...",
    "send": "بھیجیں",
    "typing": "ٹائپ کر رہا ہے...",
    "no_sessions": "کوئی چیٹ سیشن نہیں ملا",
    "error": "خرابی",
    "retry": "دوبارہ کوشش کریں"
  },
  "tasks": {
    "add": "کام شامل کریں",
    "complete": "مکمل",
    "delete": "حذف",
    "completed": "مکمل شدہ",
    "pending": "باقی"
  }
}
```

Update `frontend/messages/en.json` (extend existing):

```json
{
  "nav": {
    ...existing nav items,
    "chat": "Chat"
  },
  "chat": {
    "title": "Chat",
    "new_session": "New Chat",
    "sessions": "Chat Sessions",
    "input_placeholder": "Type a message...",
    "send": "Send",
    "typing": "Typing...",
    "no_sessions": "No chat sessions found",
    "error": "Error",
    "retry": "Retry"
  }
}
```

#### 2.3 Configure i18n

Update `frontend/i18n.ts` to include 'ur' locale:

```typescript
// frontend/i18n.ts
import {getRequestConfig} from 'next-intl/server';

export const locales = ['en', 'ur'] as const;  // Add 'ur'
export type Locale = typeof locales[number];

export default getRequestConfig(async ({locale}) => ({
  messages: (await import(`./messages/${locale}.json`)).default
}));
```

#### 2.4 Start Frontend

```bash
cd frontend
pnpm dev
```

**Expected output**:
```
   ▲ Next.js 16.x.x
   - Local:        http://localhost:3000
   - Environments: .env.local

 ✓ Ready in 2.3s
```

**Verify frontend**:
- Open http://localhost:3000
- Check existing pages still work (login, todos)

---

### 3. Test the Chatbot

#### 3.1 Authentication

1. Navigate to http://localhost:3000/login
2. Login with existing user (or register new user)
3. Verify JWT token in browser cookies (dev tools → Application → Cookies)

#### 3.2 Basic Chat Flow

1. Navigate to http://localhost:3000/chat (or create this page first)
2. Send message: **"Hello!"**
3. **Expected response**: Chatbot greeting with capabilities overview

**Example response**:
```
Hello! I'm your task management assistant. I can help you:
- Add tasks: "Add buy groceries"
- List tasks: "Show my tasks"
- Complete tasks: "Mark groceries as done"
- Delete tasks: "Delete buy milk"

How can I help you today?
```

#### 3.3 Task Management via Chat

**Test Case 1: Add Task**

1. Send: **"Add buy groceries to my tasks"**
2. **Expected response**: "I've added 'buy groceries' to your tasks."
3. **Verification**: Check /api/todos endpoint → should show new task

**Test Case 2: List Tasks**

1. Send: **"Show my tasks"** or **"What are my todos?"**
2. **Expected response**: List of all tasks with numbers
   ```
   You have 1 task:
   1. Buy groceries
   ```

**Test Case 3: Complete Task**

1. Send: **"Mark groceries as done"** or **"Complete buy groceries"**
2. **Expected response**: "I've marked 'buy groceries' as completed. Great job!"
3. **Verification**: Check /api/todos → task.completed should be true

**Test Case 4: Delete Task**

1. Send: **"Delete the groceries task"**
2. **Expected response**: "I've deleted 'buy groceries'."
3. **Verification**: Check /api/todos → task should be removed

---

### 4. Test Urdu Support

#### 4.1 Switch Language

1. Click language toggle in navbar
2. Select **Urdu (اردو)**
3. Verify UI flips to RTL (right-to-left)
4. Verify Urdu translations appear

#### 4.2 Urdu Chat Interaction

**Test Case 1: Add Task in Urdu**

1. Send: **"نیا کام: دودھ خریدنا"** (New task: buy milk)
2. **Expected response** (in Urdu): "میں نے 'دودھ خریدنا' آپ کے کاموں میں شامل کر دیا ہے۔"
3. **Verification**: RTL text rendering, Noto Nastaliq Urdu font applied

**Test Case 2: List Tasks in Urdu**

1. Send: **"میرے کام دکھائیں"** (Show my tasks)
2. **Expected response** (in Urdu):
   ```
   آپ کا ایک کام ہے:
   ۱۔ دودھ خریدنا
   ```
3. **Verification**: Urdu numerals (۱، ۲، ۳), RTL layout

**Test Case 3: Complete Task in Urdu**

1. Send: **"دودھ مکمل کریں"** (Complete milk)
2. **Expected response**: "میں نے 'دودھ خریدنا' مکمل کر دیا ہے۔ بہت اچھا!"
3. **Verification**: Proper Urdu grammar and tone

**Test Case 4: Mixed Language (Code-Switching)**

1. Send: **"Add buy milk aur bread"** (English + Urdu)
2. **Expected response**: Chatbot handles mixed language gracefully
3. **Verification**: Intent detected correctly despite code-switching

---

## Architecture Overview

### Request Flow Diagram

```
┌─────────────┐
│   User      │
│  (Browser)  │
└──────┬──────┘
       │ 1. POST /api/chat
       │    { message: "Add buy milk", session_id: "..." }
       │    Authorization: Bearer <JWT>
       ▼
┌─────────────────────────────────────┐
│   Next.js Frontend                  │
│   - Validates input                 │
│   - Sends request with JWT          │
└──────┬──────────────────────────────┘
       │ 2. Forward to FastAPI
       ▼
┌─────────────────────────────────────┐
│   FastAPI Backend (/api/chat)       │
│   - Validate JWT                    │
│   - Extract user_id from token      │
│   - Verify session ownership        │
└──────┬──────────────────────────────┘
       │ 3. Fetch conversation history
       ▼
┌─────────────────────────────────────┐
│   PostgreSQL (Neon)                 │
│   SELECT * FROM messages            │
│   WHERE session_id = ?              │
│   ORDER BY created_at DESC LIMIT 50 │
└──────┬──────────────────────────────┘
       │ 4. Return last 50 messages
       ▼
┌─────────────────────────────────────┐
│   Chatbot Service                   │
│   - Build context array             │
│   - Format for MCP                  │
└──────┬──────────────────────────────┘
       │ 5. Send context + new message
       ▼
┌─────────────────────────────────────┐
│   MCP Client                        │
│   - Initialize MCP session          │
│   - Send request to MCP server      │
└──────┬──────────────────────────────┘
       │ 6. Process with LLM + tools
       ▼
┌─────────────────────────────────────┐
│   MCP Server                        │
│   - LLM analyzes intent             │
│   - Calls add_task tool             │
│   - Executes tool (DB operation)    │
│   - Returns result to client        │
└──────┬──────────────────────────────┘
       │ 7. Return AI response
       ▼
┌─────────────────────────────────────┐
│   Chatbot Service                   │
│   - Store user message in DB        │
│   - Store assistant response in DB  │
│   - Update session.last_activity_at │
└──────┬──────────────────────────────┘
       │ 8. Return response to frontend
       ▼
┌─────────────────────────────────────┐
│   Next.js Frontend                  │
│   - Display assistant message       │
│   - Update UI                       │
└──────┬──────────────────────────────┘
       │ 9. Show response to user
       ▼
┌─────────────┐
│   User      │
│  (Browser)  │
└─────────────┘
```

### Stateless Architecture Verification

To verify the server is truly stateless:

1. **Send message 1**: "Add buy milk"
2. **Restart backend** (Ctrl+C, then `uv run uvicorn...`)
3. **Send message 2**: "Show my tasks"
4. **Expected**: Chatbot remembers context (fetched from DB)

If conversation continues seamlessly after restart, the stateless architecture is working correctly!

---

## Troubleshooting

### Issue 1: "Session not found" Error

**Symptom**: 404 error when sending chat message

**Causes**:
- Session doesn't exist in database
- User doesn't own the session (user_id mismatch)

**Solution**:
```bash
# Option 1: Create session via API
curl -X POST http://localhost:8000/api/chat/sessions \
  -H "Authorization: Bearer <your-jwt>" \
  -H "Content-Type: application/json" \
  -d '{"title": "My first chat", "language": "en"}'

# Option 2: Frontend should auto-create session on first message
# Check frontend code implements lazy session creation
```

### Issue 2: "MCP server timeout"

**Symptom**: 500 error, backend logs show "MCP request timed out"

**Causes**:
- LLM API key invalid or missing
- Network issues reaching LLM provider
- MCP server crashed

**Solution**:
```bash
# Verify API key
echo $ANTHROPIC_API_KEY  # or OPENAI_API_KEY

# Test MCP server manually
uv run python -c "
import anthropic
client = anthropic.Anthropic(api_key='sk-ant-...')
response = client.messages.create(
    model='claude-3-5-sonnet-20241022',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'Hello'}]
)
print(response.content)
"

# If test works, check MCP server logs for errors
# Increase timeout in backend code if needed
```

### Issue 3: "Urdu text not rendering"

**Symptom**: Urdu text shows as boxes or question marks

**Causes**:
- Noto Nastaliq Urdu font not loaded
- CSS `dir="rtl"` not applied

**Solution**:
```tsx
// Verify font import in layout.tsx
import { Noto_Nastaliq_Urdu } from 'next/font/google'

// Check font variable in HTML
<html className={urduFont.variable}>

// Verify CSS is applied
// Inspect element → should see:
// font-family: var(--font-urdu), serif;
// direction: rtl;
```

**Browser compatibility test**:
- Chrome: ✅ Should work
- Firefox: ✅ Should work
- Safari: ⚠️ May have rendering issues (test on Mac)
- Edge: ✅ Should work

### Issue 4: "Tool call failed" (Task operations not working)

**Symptom**: Chatbot says "I'm having trouble adding that task"

**Causes**:
- MCP tools not registered correctly
- Database connection issues
- User_id not passed to MCP tools

**Solution**:
```python
# Check MCP tool registration (backend/app/mcp/tools.py)
# Verify all tools are registered:
# - add_task
# - list_tasks
# - complete_task
# - delete_task

# Check database connection
uv run python -c "
from app.database import engine
from app.models import Task
from sqlmodel import Session, select

with Session(engine) as db:
    tasks = db.exec(select(Task)).all()
    print(f'Found {len(tasks)} tasks in database')
"

# Verify user_id is passed to MCP context
# Check backend logs for: "MCP request with user_id: ..."
```

### Issue 5: "Empty response from chatbot"

**Symptom**: User sends message, gets empty response

**Causes**:
- LLM returned empty content
- Response parsing failed
- System prompt not configured correctly

**Solution**:
```bash
# Check backend logs for actual LLM response
# Look for: "MCP response: ..."

# Verify system prompt is loaded
# Check contracts/mcp-tools.yaml file exists
# Verify system_prompt field is not empty

# Test with simple message
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": "<session-id>"}'

# Should return non-empty response
```

---

## Performance Benchmarks

### Expected Performance (Local Development)

| Operation | Target | Acceptable | Notes |
|-----------|--------|------------|-------|
| Database query (50 msgs) | <50ms | <100ms | With indexes |
| MCP request (simple) | <1s | <2s | No tool calls |
| MCP request (with tool) | <2s | <3s | Includes DB operation |
| Total chat response | <2s | <3s | End-to-end |
| Session list query | <30ms | <50ms | Paginated |

### Performance Testing

```bash
# Backend response time
curl -w "Total time: %{time_total}s\n" \
  -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer <jwt>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks", "session_id": "<session-id>"}'

# Should see: Total time: 2.xxxs (under 3 seconds)
```

---

## Next Steps

After quickstart setup is complete:

1. ✅ Run `/sp.tasks` to generate implementation tasks
2. ✅ Run `/sp.implement` to execute tasks with specialized agents:
   - `database-architect`: Create Session/Message models and migrations
   - `backend-api-guardian`: Implement /api/chat endpoint and MCP integration
   - `frontend-builder`: Build chat UI components with RTL support
   - `urdu-translator`: Validate Urdu translations and RTL rendering
3. ✅ Run tests: `pytest backend/tests/` and `pnpm test`
4. ✅ Review and commit changes
5. ✅ Create PHR (Prompt History Record) documenting the feature

---

## Additional Resources

- **MCP Documentation**: https://modelcontextprotocol.io/
- **Anthropic Claude API**: https://docs.anthropic.com/
- **OpenAI API**: https://platform.openai.com/docs/
- **Next.js i18n**: https://next-intl-docs.vercel.app/
- **Noto Nastaliq Urdu Font**: https://fonts.google.com/noto/specimen/Noto+Nastaliq+Urdu
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **Neon Serverless PostgreSQL**: https://neon.tech/docs

---

**Quickstart Status**: ✅ COMPLETE

Ready to begin implementation with `/sp.tasks`!
