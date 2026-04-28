# Battry

Battry turns messy daily experiences into structured energy data.

The current loop is simple:

```text
write a log -> parse events -> update battery -> show recent patterns
```

It's not tryna to be a journal, habit tracker, or therapy tool. Right now it is a small logging and scoring system with a mobile shell around it.

## What Works Now

- Submit a text log from the Expo app.
- Parse simple phrases like `bad sleep`, `small talk`, `doomscroll`, `quiet time`, and `music`.
- Convert those phrases into structured `up` / `down` events.
- Calculate `battery_before` and `battery_after`.
- Keep logs in memory when no database is configured.
- Store logs and parsed events in Supabase Postgres when `SUPABASE_DATABASE_URL` is set.
- Fetch recent logs for a user.
- Build a basic weekly report with average/min/max battery, top drainer, top recharger, and a simple risk label.

## Current Stack

- Mobile: Expo, React Native, TypeScript
- Backend: Python, FastAPI, Pydantic
- Persistence: in-memory fallback or Supabase Postgres
- Local server: Uvicorn

## Backend Setup

Create a virtualenv:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the API from the repo root:

```bash
python -m uvicorn backend.app.main:app --reload
```

The backend defaults to:

```text
http://127.0.0.1:8000
```

## Backend Endpoints

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Create a log:

```bash
curl -X POST http://127.0.0.1:8000/logs \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "demo-user",
    "text": "bad sleep and small talk",
    "logged_at": "2026-04-27T09:00:00Z"
  }'
```

List logs:

```bash
curl 'http://127.0.0.1:8000/logs?user_id=demo-user'
```

Get the weekly report:

```bash
curl 'http://127.0.0.1:8000/report/weekly?user_id=demo-user'
```

## Database Mode

The backend has two storage modes:

- No `SUPABASE_DATABASE_URL`: logs live in memory and reset when the server restarts.
- With `SUPABASE_DATABASE_URL`: logs and parsed events are written to Supabase Postgres.

Copy the env template when you want persistence:

```bash
cp .env.example .env
```

Then fill in:

```text
SUPABASE_DATABASE_URL=postgresql://...
```

Run the SQL migration in:

```text
supabase/migrations/202604260001_initial_battry_schema.sql
```

Auth is not wired yet. The app currently uses `demo-user`, and user isolation is handled by backend filtering. That is fine for this stage, but it is not the final security model.

## Mobile Setup

Install the mobile dependencies:

```bash
cd mobile
npm install
```

Run Expo:

```bash
npm run ios
```

or:

```bash
npm start
```

The mobile app uses:

```text
http://127.0.0.1:8000
```

by default. Override it with:

```bash
EXPO_PUBLIC_API_URL=http://127.0.0.1:8000 npm start
```

## Future Plans

This is still pretty early and plain

What needs to be done:

- real auth
- proper user accounts
- production-grade RLS flow
- vector parsing
- ML forecasting
- polished charts
- the final Mercury Cell UI

I think making sure the core is tight is the priority then adding the ML features and UX buffs
