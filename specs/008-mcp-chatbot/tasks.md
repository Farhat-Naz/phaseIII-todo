# Tasks: MCP-Based Chatbot System

**Input**: Design documents from `/specs/008-mcp-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included following TDD approach (constitution requirement: test-driven development with 80%+ coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/app/`, `frontend/app/`, `frontend/components/`
- Paths follow plan.md structure (frontend + backend + MCP server)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and environment configuration

- [ ] T001 Install UV package manager and verify installation (backend environment)
- [ ] T002 Add MCP SDK and dependencies to backend/pyproject.toml using `uv add mcp anthropic`
- [ ] T003 [P] Add next-intl and i18n dependencies to frontend using `pnpm add @formatjs/intl-localematcher negotiator`
- [ ] T004 [P] Configure environment variables in backend/.env (MCP_TRANSPORT, ANTHROPIC_API_KEY or OPENAI_API_KEY)
- [ ] T005 [P] Load Noto Nastaliq Urdu font in frontend/app/layout.tsx via next/font/google
- [ ] T006 [P] Create Urdu translation file frontend/messages/ur.json with chat-specific keys
- [ ] T007 [P] Update frontend i18n configuration to include 'ur' locale in frontend/i18n.ts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core database schema and MCP infrastructure that MUST be complete before ANY user story

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema (Session & Message Tables)

- [ ] T008 Create Session SQLModel in backend/app/models.py (session_id, user_id, title, language, timestamps)
- [ ] T009 Create Message SQLModel in backend/app/models.py (message_id, session_id, role, content, language, created_at)
- [ ] T010 Add language_preference field to User model in backend/app/models.py
- [ ] T011 Generate Alembic migration for Session and Message tables using `uv run alembic revision --autogenerate -m "Add session and message tables"`
- [ ] T012 Run migration to create tables using `uv run alembic upgrade head`
- [ ] T013 [P] Write unit test for Session model validation in backend/tests/unit/test_models.py
- [ ] T014 [P] Write unit test for Message model validation in backend/tests/unit/test_models.py

### MCP Server Infrastructure

- [ ] T015 Create MCP server entry point in backend/app/mcp/server.py with STDIO transport setup
- [ ] T016 [P] Implement add_task MCP tool in backend/app/mcp/tools.py (with user_id filtering)
- [ ] T017 [P] Implement list_tasks MCP tool in backend/app/mcp/tools.py (with optional completed filter)
- [ ] T018 [P] Implement complete_task MCP tool in backend/app/mcp/tools.py (with ownership verification)
- [ ] T019 [P] Implement delete_task MCP tool in backend/app/mcp/tools.py (with ownership verification)
- [ ] T020 Load system prompt from contracts/mcp-tools.yaml and configure in MCP server
- [ ] T021 [P] Write unit tests for MCP tools with mock database in backend/tests/unit/test_mcp_tools.py

### MCP Client Infrastructure

- [ ] T022 Create MCP client initialization in backend/app/mcp/client.py with STDIO transport
- [ ] T023 Implement context builder in backend/app/mcp/context.py (fetch last 50 messages, format for MCP)
- [ ] T024 [P] Write unit test for context builder logic in backend/tests/unit/test_mcp_context.py
- [ ] T025 [P] Write unit test for MCP client initialization in backend/tests/unit/test_mcp_client.py

### Business Logic Services

- [ ] T026 Create SessionService in backend/app/services/session_service.py (create, get, list, update last_activity)
- [ ] T027 Create MessageService in backend/app/services/message_service.py (create, get history, pagination)
- [ ] T028 Create ChatbotService in backend/app/services/chatbot_service.py (orchestrate stateless chat flow)
- [ ] T029 [P] Write unit tests for SessionService in backend/tests/unit/test_session_service.py
- [ ] T030 [P] Write unit tests for MessageService in backend/tests/unit/test_message_service.py
- [ ] T031 [P] Write unit tests for ChatbotService in backend/tests/unit/test_chatbot_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic Chat Conversation (Priority: P1) 🎯 MVP

**Goal**: Enable users to have simple text conversations with AI assistant, demonstrating stateless conversation flow

**Independent Test**: Open chat interface, send "Hello, what can you do?", receive intelligent response. Refresh page, conversation history restored. Restart server between messages, conversation continues seamlessly.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T032 [P] [US1] Contract test for POST /api/chat endpoint in backend/tests/integration/test_chat_api.py (verify stateless flow)
- [ ] T033 [P] [US1] Integration test for conversation persistence in backend/tests/integration/test_chat_api.py (refresh page scenario)
- [ ] T034 [P] [US1] Integration test for server restart scenario in backend/tests/integration/test_chat_api.py (stateless verification)
- [ ] T035 [P] [US1] Unit test for ChatMessage component in frontend/__tests__/unit/ChatMessage.test.tsx (message rendering)
- [ ] T036 [P] [US1] Unit test for ChatInput component in frontend/__tests__/unit/ChatInput.test.tsx (message sending)

### Backend Implementation for User Story 1

- [ ] T037 [US1] Create POST /api/chat endpoint in backend/app/routers/chat.py (validates JWT, session ownership, calls ChatbotService)
- [ ] T038 [US1] Implement stateless request flow in ChatbotService.process_message() (fetch history → build context → call MCP → store messages)
- [ ] T039 [US1] Add error handling for MCP failures in ChatbotService with user-friendly messages
- [ ] T040 [US1] Add structured logging for chat requests in chat.py router (user_id, session_id, message_length, history_count)

### Frontend Implementation for User Story 1

- [ ] T041 [P] [US1] Create ChatWindow component in frontend/components/chat/ChatWindow.tsx (main chat container)
- [ ] T042 [P] [US1] Create ChatMessage component in frontend/components/chat/ChatMessage.tsx (displays individual messages)
- [ ] T043 [P] [US1] Create ChatInput component in frontend/components/chat/ChatInput.tsx (message input field)
- [ ] T044 [P] [US1] Create TypingIndicator component in frontend/components/chat/TypingIndicator.tsx (loading state during MCP processing)
- [ ] T045 [US1] Create chat API client in frontend/lib/chat-api.ts (sendMessage, getHistory functions with JWT)
- [ ] T046 [US1] Create useChat custom hook in frontend/hooks/useChat.ts (manages chat state, sends messages)
- [ ] T047 [US1] Create chat page in frontend/app/(dashboard)/chat/page.tsx (renders ChatWindow)
- [ ] T048 [US1] Create session-specific chat page in frontend/app/(dashboard)/chat/[sessionId]/page.tsx (loads specific session)

### Integration for User Story 1

- [ ] T049 [US1] Integrate ChatWindow with useChat hook and display conversation history
- [ ] T050 [US1] Add optimistic UI updates (show user message immediately, wait for assistant response)
- [ ] T051 [US1] Handle error states (MCP timeout, network failure) with retry button
- [ ] T052 [US1] Add loading indicators during message processing (TypingIndicator visible)

### E2E Tests for User Story 1

- [ ] T053 [US1] E2E test for full chat flow in frontend/__tests__/e2e/chat.spec.ts (send message → receive response → history persisted)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently. Users can have basic conversations with the chatbot, and conversation history persists across page refreshes and server restarts.

---

## Phase 4: User Story 2 - Natural Language Task Management (Priority: P2)

**Goal**: Enable users to manage todo tasks through natural conversation without learning command syntax

**Independent Test**: In chat, say "Add buy groceries to my tasks", verify task created. Say "Show my tasks", verify list displayed. Say "Mark groceries as done", verify task completed. Say "Delete groceries", verify task removed.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T054 [P] [US2] Integration test for add task via chat in backend/tests/integration/test_mcp_integration.py (natural language → tool call)
- [ ] T055 [P] [US2] Integration test for list tasks via chat in backend/tests/integration/test_mcp_integration.py (verify formatting)
- [ ] T056 [P] [US2] Integration test for complete task via chat in backend/tests/integration/test_mcp_integration.py (partial title matching)
- [ ] T057 [P] [US2] Integration test for delete task via chat in backend/tests/integration/test_mcp_integration.py (ownership verification)
- [ ] T058 [P] [US2] Integration test for ambiguous intent in backend/tests/integration/test_mcp_integration.py (chatbot asks for clarification)

### Implementation for User Story 2

**Note**: MCP tools already implemented in Phase 2 (T016-T019), this phase focuses on chatbot integration and UX

- [ ] T059 [US2] Verify add_task MCP tool correctly filters by user_id from JWT (security check)
- [ ] T060 [US2] Verify list_tasks MCP tool returns tasks sorted by created_at DESC
- [ ] T061 [US2] Verify complete_task MCP tool finds tasks by partial title match (e.g., "groceries" matches "buy groceries")
- [ ] T062 [US2] Verify delete_task MCP tool returns 404 for non-existent or unauthorized tasks
- [ ] T063 [US2] Test chatbot's natural language understanding with various phrasings (informal, formal, typos)
- [ ] T064 [US2] Test chatbot's clarification flow when intent is ambiguous (e.g., "add it" → asks "What task?")
- [ ] T065 [US2] Test chatbot's error handling when tool calls fail (database error → user-friendly message)

### Frontend Integration for User Story 2

- [ ] T066 [US2] Update ChatMessage component to format task lists (numbered, completion status icons)
- [ ] T067 [US2] Add visual confirmation when tasks are created/completed/deleted (success message styling)
- [ ] T068 [US2] Test task management flow in chat UI (verify responses formatted correctly)

### Integration Tests for User Story 2

- [ ] T069 [US2] Integration test for full task management flow in chat in frontend/__tests__/integration/ChatFlow.test.tsx (add → list → complete → delete)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently. Users can chat AND manage tasks via natural language.

---

## Phase 5: User Story 3 - Urdu Language Support (Priority: P3)

**Goal**: Enable Urdu-speaking users to interact with chatbot in Urdu with proper RTL rendering

**Independent Test**: Switch language to Urdu, send "سلام، میری مدد کریں", verify Urdu response with RTL rendering. Send "نیا کام: دودھ خریدنا", verify task created and Urdu confirmation.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T070 [P] [US3] Unit test for RTL rendering in ChatMessage component in frontend/__tests__/unit/ChatMessage.test.tsx (dir="rtl" applied)
- [ ] T071 [P] [US3] Integration test for Urdu intent detection in backend/tests/integration/test_mcp_integration.py (Urdu commands → correct tools)
- [ ] T072 [P] [US3] Integration test for Urdu response generation in backend/tests/integration/test_mcp_integration.py (responses in Urdu)
- [ ] T073 [P] [US3] E2E test for Urdu chat flow in frontend/__tests__/e2e/chat.spec.ts (full Urdu conversation)

### Frontend Implementation for User Story 3

- [ ] T074 [P] [US3] Create LanguageToggle component in frontend/components/chat/LanguageToggle.tsx (English/Urdu switcher)
- [ ] T075 [US3] Update ChatMessage component to apply RTL CSS when language is 'ur' (dir="rtl", font-urdu class)
- [ ] T076 [US3] Update ChatInput component to apply RTL CSS when language is 'ur' and set placeholder text accordingly
- [ ] T077 [US3] Create useLanguage custom hook in frontend/hooks/useLanguage.ts (manages language preference)
- [ ] T078 [US3] Add language detection logic in useChat hook (detect Urdu from message content)
- [ ] T079 [US3] Update chat page to include LanguageToggle component in header

### Backend Implementation for User Story 3

- [ ] T080 [US3] Verify MCP system prompt includes Urdu command examples (already in contracts/mcp-tools.yaml)
- [ ] T081 [US3] Test LLM's Urdu understanding with sample queries (intent detection accuracy)
- [ ] T082 [US3] Test LLM's Urdu response generation (grammatically correct, proper tone)
- [ ] T083 [US3] Add language field to Message table entries (store 'en' or 'ur' per message)

### CSS and Styling for User Story 3

- [ ] T084 [P] [US3] Add Tailwind RTL utilities configuration in frontend/tailwind.config.ts
- [ ] T085 [P] [US3] Create Urdu font CSS class in frontend/app/globals.css (.font-urdu with Noto Nastaliq)
- [ ] T086 [P] [US3] Add LTR override styles for numbers and code blocks in Urdu messages in frontend/app/globals.css

### Integration for User Story 3

- [ ] T087 [US3] Test language switching (English → Urdu → English) preserves conversation context
- [ ] T088 [US3] Test code-switching support (mixed English + Urdu in same message)
- [ ] T089 [US3] Test Urdu numerals display in task lists (۱، ۲، ۳)
- [ ] T090 [US3] Verify font loading on different browsers (Chrome, Firefox, Safari, Edge)

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently. Users can chat in English or Urdu with proper RTL rendering.

---

## Phase 6: User Story 4 - Multi-Session Conversation Continuity (Priority: P4)

**Goal**: Enable users to manage multiple concurrent chat sessions with independent conversation contexts

**Independent Test**: Open two browser tabs with different session IDs, have different conversations in each, refresh both, verify each session maintains its own history independently.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T091 [P] [US4] Contract test for GET /api/chat/sessions endpoint in backend/tests/integration/test_chat_api.py (list user sessions)
- [ ] T092 [P] [US4] Contract test for POST /api/chat/sessions endpoint in backend/tests/integration/test_chat_api.py (create new session)
- [ ] T093 [P] [US4] Contract test for GET /api/chat/sessions/{session_id}/messages endpoint in backend/tests/integration/test_chat_api.py (get conversation history)
- [ ] T094 [P] [US4] Integration test for session isolation in backend/tests/integration/test_chat_api.py (two sessions, different histories)
- [ ] T095 [P] [US4] Integration test for session cleanup in backend/tests/unit/test_session_service.py (30-day inactive session deletion)

### Backend Implementation for User Story 4

- [ ] T096 [P] [US4] Create GET /api/chat/sessions endpoint in backend/app/routers/chat.py (list user's sessions with pagination)
- [ ] T097 [P] [US4] Create POST /api/chat/sessions endpoint in backend/app/routers/chat.py (create new session)
- [ ] T098 [P] [US4] Create GET /api/chat/sessions/{session_id}/messages endpoint in backend/app/routers/chat.py (get conversation history)
- [ ] T099 [US4] Implement lazy session creation in ChatbotService (create session on first message if not exists)
- [ ] T100 [US4] Implement session title generation from first user message in SessionService (truncate to 50 chars)
- [ ] T101 [US4] Implement session cleanup background job in backend/app/services/session_service.py (delete sessions inactive > 30 days)

### Frontend Implementation for User Story 4

- [ ] T102 [P] [US4] Create SessionList component in frontend/components/chat/SessionList.tsx (displays user's sessions)
- [ ] T103 [US4] Create useSession custom hook in frontend/hooks/useSession.ts (manages session state, creates/switches sessions)
- [ ] T104 [US4] Update chat page to show SessionList in sidebar with "New Chat" button
- [ ] T105 [US4] Add session switching logic (click session → load that session's history)
- [ ] T106 [US4] Add "New Chat" button functionality (creates new session, navigates to it)
- [ ] T107 [US4] Update UI to show current session title in header

### Integration for User Story 4

- [ ] T108 [US4] Test multiple concurrent sessions (open 2 tabs, verify independence)
- [ ] T109 [US4] Test session persistence (refresh page, verify session restored)
- [ ] T110 [US4] Test session cleanup job (manually set last_activity_at > 30 days, run job, verify deletion)
- [ ] T111 [US4] Test session title auto-generation (send first message, verify title created)

**Checkpoint**: All user stories should now be independently functional. Users can manage multiple chat sessions with independent conversation histories.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

### Security Hardening

- [ ] T112 [P] Verify all endpoints validate JWT and extract user_id correctly (security audit)
- [ ] T113 [P] Verify session ownership checks in all chat endpoints (prevent unauthorized access)
- [ ] T114 [P] Verify MCP tools filter all database queries by user_id (prevent data leakage)
- [ ] T115 [P] Add rate limiting to /api/chat endpoint (prevent abuse)
- [ ] T116 [P] Add input sanitization for message content (prevent XSS)

### Performance Optimization

- [ ] T117 [P] Add database connection pooling configuration in backend/app/database.py (max 20 connections)
- [ ] T118 [P] Verify indexes are created on session(user_id), message(session_id, created_at) for query performance
- [ ] T119 [P] Add response time logging for chat requests (monitor p95 < 3 seconds)
- [ ] T120 [P] Optimize frontend bundle size with code splitting for chat components

### Error Handling and Observability

- [ ] T121 [P] Add comprehensive error logging with stack traces in backend (sanitized in production responses)
- [ ] T122 [P] Add frontend error boundary for chat components (graceful error display)
- [ ] T123 [P] Add monitoring for MCP server health (detect crashes, auto-restart)
- [ ] T124 [P] Create error recovery UI (retry button, clear error state)

### Documentation and Testing

- [ ] T125 [P] Run quickstart.md validation (follow all setup steps, verify they work)
- [ ] T126 [P] Update API documentation in contracts/chat-api.yaml if any endpoints changed
- [ ] T127 [P] Verify test coverage meets 80% target using `pytest --cov=app backend/tests/` and `pnpm test --coverage`
- [ ] T128 [P] Add missing unit tests for any uncovered code paths

### Deployment Preparation

- [ ] T129 [P] Create production environment configuration in backend/.env.production
- [ ] T130 [P] Add Docker configuration for backend deployment (Render/Railway)
- [ ] T131 [P] Configure Vercel deployment for frontend
- [ ] T132 [P] Set up database backups on Neon (daily automatic)
- [ ] T133 [P] Create deployment checklist in docs/deployment.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) - MVP starts here
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) - Can run in parallel with US1 if staffed
- **User Story 3 (Phase 5)**: Depends on Foundational (Phase 2) - Can run in parallel with US1/US2 if staffed
- **User Story 4 (Phase 6)**: Depends on Foundational (Phase 2) - Can run in parallel with other stories
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies on other stories - Foundation for chat interface
- **User Story 2 (P2)**: Depends on US1 (needs chat UI) - But MCP tools can be developed in parallel
- **User Story 3 (P3)**: Depends on US1 (needs chat UI) - Independent from US2
- **User Story 4 (P4)**: Depends on US1 (needs chat UI) - Independent from US2/US3

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Backend services before API endpoints
- Frontend components before integration
- Core implementation before integration with other stories
- Story complete and tested before moving to next priority

### Parallel Opportunities

#### Phase 1 (Setup)
All tasks marked [P] can run in parallel: T003, T004, T005, T006, T007

#### Phase 2 (Foundational)
- Database models: T008, T009, T010 can run in parallel
- Tests: T013, T014 can run in parallel after models complete
- MCP tools: T016, T017, T018, T019 can run in parallel
- Tool tests: T021 after tools complete
- MCP client tests: T024, T025 can run in parallel
- Service tests: T029, T030, T031 can run in parallel after services complete

#### User Story 1
- Backend tests: T032, T033, T034 can run in parallel (all test files)
- Frontend tests: T035, T036 can run in parallel (all test files)
- Frontend components: T041, T042, T043, T044 can run in parallel (different files)

#### User Story 2
- All integration tests: T054, T055, T056, T057, T058 can run in parallel

#### User Story 3
- All unit tests: T070, T071, T072, T073 can run in parallel
- Frontend components: T074 and CSS tasks: T084, T085, T086 can run in parallel

#### User Story 4
- All contract tests: T091, T092, T093, T094, T095 can run in parallel
- Backend endpoints: T096, T097, T098 can run in parallel (different endpoints)
- Frontend components: T102 can be developed while backend APIs are being built

#### Phase 7 (Polish)
- All security tasks: T112, T113, T114, T115, T116 can run in parallel
- All performance tasks: T117, T118, T119, T120 can run in parallel
- All error handling tasks: T121, T122, T123, T124 can run in parallel
- All documentation tasks: T125, T126, T127, T128 can run in parallel
- All deployment tasks: T129, T130, T131, T132, T133 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all User Story 1 tests together (after Foundational phase):
Task T032: "Contract test for POST /api/chat endpoint in backend/tests/integration/test_chat_api.py"
Task T033: "Integration test for conversation persistence in backend/tests/integration/test_chat_api.py"
Task T034: "Integration test for server restart scenario in backend/tests/integration/test_chat_api.py"
Task T035: "Unit test for ChatMessage component in frontend/__tests__/unit/ChatMessage.test.tsx"
Task T036: "Unit test for ChatInput component in frontend/__tests__/unit/ChatInput.test.tsx"

# After tests fail, launch all frontend components together:
Task T041: "Create ChatWindow component in frontend/components/chat/ChatWindow.tsx"
Task T042: "Create ChatMessage component in frontend/components/chat/ChatMessage.tsx"
Task T043: "Create ChatInput component in frontend/components/chat/ChatInput.tsx"
Task T044: "Create TypingIndicator component in frontend/components/chat/TypingIndicator.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T031) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T032-T053)
4. **STOP and VALIDATE**: Test User Story 1 independently using acceptance scenarios
5. Deploy/demo basic chat conversation if ready

**Estimated MVP Scope**: ~53 tasks (Phase 1 + Phase 2 + Phase 3)

### Incremental Delivery

1. **Foundation** (Phases 1-2): Setup + Database + MCP Infrastructure → Foundation ready
2. **MVP** (Phase 3): User Story 1 → Test independently → Deploy/Demo (Basic chat working!)
3. **Enhanced** (Phase 4): Add User Story 2 → Test independently → Deploy/Demo (Task management via chat!)
4. **Multilingual** (Phase 5): Add User Story 3 → Test independently → Deploy/Demo (Urdu support!)
5. **Power User** (Phase 6): Add User Story 4 → Test independently → Deploy/Demo (Multi-session management!)
6. **Production Ready** (Phase 7): Polish & Cross-Cutting → Final testing → Production deployment

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers after Foundational phase completes:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational is done:
   - **Developer A**: User Story 1 (Basic Chat) - Priority P1
   - **Developer B**: User Story 2 (Task Management) - Priority P2
   - **Developer C**: User Story 3 (Urdu Support) - Priority P3
   - **Developer D**: User Story 4 (Multi-Session) - Priority P4
3. Stories complete and integrate independently
4. Team converges on Phase 7 (Polish) together

---

## Task Execution Checklist

For each task, ensure:

- [ ] Task ID is sequential and matches format (T001, T002, etc.)
- [ ] [P] marker is present if task can run in parallel
- [ ] [Story] label is present for user story tasks (US1, US2, US3, US4)
- [ ] File path is specific and complete
- [ ] If test task: Verify test FAILS before implementation
- [ ] If implementation task: Verify related tests PASS after completion
- [ ] Code follows constitution requirements (stateless, security, TDD)
- [ ] Commit after task completion with meaningful message

---

## Notes

- **[P] tasks**: Different files, no dependencies on incomplete tasks
- **[Story] label**: Maps task to specific user story for traceability and independent testing
- **Each user story**: Should be independently completable and testable against acceptance scenarios
- **Stateless architecture**: Verify at every step - no in-memory conversation state
- **Security**: ALWAYS filter by user_id, validate JWT, verify session ownership
- **TDD**: Tests written first, verify they FAIL, then implement to make them PASS
- **80% coverage target**: Monitor with pytest-cov and jest --coverage
- **Stop at checkpoints**: Validate each story independently before proceeding

---

## Success Criteria

✅ User Story 1 complete when:
- User can send "Hello", receive response within 2 seconds
- Conversation history persists across page refresh
- Conversation continues after server restart (stateless verified)

✅ User Story 2 complete when:
- User can say "Add buy groceries" → task created
- User can say "Show my tasks" → tasks listed with formatting
- User can say "Mark groceries done" → task completed
- User can say "Delete groceries" → task removed
- Chatbot asks for clarification when intent ambiguous

✅ User Story 3 complete when:
- User can switch to Urdu, send "سلام", receive Urdu response
- RTL rendering works correctly in all browsers
- Urdu task commands work ("نیا کام: دودھ خریدنا")
- Urdu numerals display in task lists (۱، ۲، ۳)

✅ User Story 4 complete when:
- User can create multiple sessions
- Each session maintains independent conversation history
- User can switch between sessions seamlessly
- Inactive sessions (>30 days) are cleaned up automatically

✅ MVP ready when User Story 1 passes all acceptance scenarios
✅ Production ready when all 4 user stories pass and Phase 7 complete
