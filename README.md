# Battry

Battry is an app for turning messy daily stuff into energy data.

The basic idea:

```text
log what happened -> parse it -> update your battery -> show patterns
```

It is not supposed to be a notes app or habit tracker. The goal is more like a personal energy signal system.

## Stack

- Mobile: Expo / React Native / TypeScript
- Backend: FastAPI / Python
- Database: Supabase Postgres

## What Works Right Now

- submit a text log from the mobile app
- parse simple events like `bad sleep`, `small talk`, `quiet time`, `music`
- calculate `battery_before` and `battery_after`
- store logs in Supabase
- view recent logs
- view a basic weekly report
- show average/min/max battery
- show top drainer and top recharger
- simple risk placeholder

## Current State

This is still early, but the core loop pretty much works now.

Still missing:

- real auth
- real user ownership
- better reports
- forecasting / ML later

