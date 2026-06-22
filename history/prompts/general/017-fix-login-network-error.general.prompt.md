---
id: 017
title: Fix Login Network Error on Vercel
stage: general
date: 2026-06-23
surface: agent
model: claude-sonnet-4-6
feature: none
branch: 008-mcp-chatbot
user: Asif Iqbal
command: debug network error on login
labels: ["debugging","vercel","env-vars","network-error","login","frontend"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/lib/api.ts
  - frontend/hooks/useAuth.ts
tests:
  - manual: login flow on Vercel production
---

## Prompt

ya link hai is project ka ya work kar rahi thi ab network error araha hai is folder ka project hai vercel par uploaded bhi hai aur github main bhi

(Follow-up): login par hi

## Response snapshot

Diagnosed that login network error was caused by `NEXT_PUBLIC_API_URL` being undefined in Vercel environment variables. The env variable name was previously changed to `NEXT_PUBLIC_API_URL1` and then reverted in code, but Vercel dashboard still had the old variable name — causing `fetch("undefined/api/auth/login")` → network error.

**Root cause:** `useAuth.ts` line 104 used `process.env.NEXT_PUBLIC_API_URL` directly without fallback. When variable is undefined, URL becomes `"undefined/api/auth/login"`.

**Two fixes applied:**
1. Vercel Dashboard: Add `NEXT_PUBLIC_API_URL = https://phaseii-todo-backend.onrender.com` and redeploy
2. Code fix: Export `API_BASE_URL` from `api.ts` and import it in `useAuth.ts` to use centralized value with fallback

## Outcome

- ✅ Impact: Login works on Vercel production after setting correct env variable name
- 🧪 Tests: Manual login test on production URL
- 📁 Files: api.ts (exported API_BASE_URL), useAuth.ts (use imported API_BASE_URL)
- 🔁 Next prompts: Push code fix to GitHub so Vercel redeploys with safe fallback
- 🧠 Reflection: Always use centralized API_BASE_URL instead of process.env directly; env variable name changes require Vercel dashboard update + redeploy

## Evaluation notes (flywheel)

- Failure modes observed: Direct `process.env.NEXT_PUBLIC_API_URL` usage without fallback; Vercel env var name mismatch after code revert
- Graders run and results (PASS/FAIL): Manual login — PASS after Vercel env fix
- Prompt variant (if applicable): null
- Next experiment: Add env var validation on app startup to catch missing vars early
