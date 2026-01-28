# Feature Specification: AI-Powered Chatbot (MCP Chatbot)

**Feature Branch**: `008-mcp-chatbot`
**Created**: 2026-01-28
**Status**: Implemented

## Executive Summary

AI-powered chatbot integrated into the TodoApp using OpenAI GPT-4o. Authenticated users can send messages and receive contextual responses. Supports English and Urdu languages. Conversation history is maintained per session for context continuity.

## User Scenarios

### User Story 1 - Send and Receive Chat Messages (Priority: P1)

Authenticated users can type messages in the chat interface and receive AI-generated responses from GPT-4o.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I navigate to `/chat`, **Then** I see a chat interface with input box and send button
2. **Given** I type a message and click Send, **When** the request is processed, **Then** I receive an AI response within the chat UI
3. **Given** I am not authenticated, **When** I try to access `/chat`, **Then** I am redirected to login page
4. **Given** I send multiple messages, **When** I continue the conversation, **Then** the AI maintains context from previous messages in the session

### User Story 2 - Language Support (Priority: P2)

Chatbot responds in the user's selected language (English or Urdu).

**Acceptance Scenarios**:

1. **Given** I am on the English locale (`/en/chat`), **When** I send a message, **Then** the AI responds in English
2. **Given** I am on the Urdu locale (`/ur/chat`), **When** I send a message, **Then** the AI responds in Urdu

### User Story 3 - Error Handling (Priority: P1)

Chat gracefully handles errors from the AI service.

**Acceptance Scenarios**:

1. **Given** the OpenAI API is unavailable, **When** I send a message, **Then** I see an error message in the chat UI (not a blank screen)
2. **Given** OPENAI_API_KEY is not configured, **When** I send a message, **Then** I receive a 500 error with clear message

## Requirements

### Functional Requirements

- **FR-CHAT-001**: POST `/api/chat/` accepts `{message, session_id?, language}` and returns `{assistant_message, session_id, timestamp}`
- **FR-CHAT-002**: Endpoint requires JWT authentication (Bearer token)
- **FR-CHAT-003**: Conversation history maintained per user session (last 20 messages)
- **FR-CHAT-004**: System prompt instructs GPT-4o to act as a TodoApp assistant
- **FR-CHAT-005**: Language parameter controls response language (en/ur)
- **FR-CHAT-006**: OpenAI API key loaded from `OPENAI_API_KEY` environment variable

### Non-Functional Requirements

- **NFR-CHAT-001**: Response time < 10 seconds (GPT-4o typical latency)
- **NFR-CHAT-002**: Max 1024 tokens per response
- **NFR-CHAT-003**: Session history capped at 20 messages to manage token usage

## Architecture

### Backend
- **Router**: `backend/app/routers/chat.py`
- **Model**: OpenAI GPT-4o via `openai` Python package
- **Session Storage**: In-memory dict (resets on cold start — acceptable for serverless)
- **Auth**: Uses existing `CurrentUser` dependency from `app/dependencies.py`

### Frontend
- **Page**: `frontend/app/[locale]/chat/page.tsx`
- **API Call**: `POST /api/chat/` (relative URL, proxied via Vercel rewrite)

## Dependencies

- `openai>=1.0.0` Python package (added to `requirements.txt`)
- `OPENAI_API_KEY` environment variable (set on Vercel dashboard for backend project)

## Out of Scope

- Streaming responses (currently returns full response at once)
- Persistent chat history across sessions (in-memory only)
- Tool/function calling for actual todo CRUD operations
- Voice-to-text integration
