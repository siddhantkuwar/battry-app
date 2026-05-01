-- Harden Battry's public tables before enabling Supabase anonymous sign-ins.
--
-- Anonymous Supabase Auth users are still database role "authenticated". These
-- policies therefore check both ownership via auth.uid() and the JWT
-- is_anonymous claim so only private device identities can access app rows.

alter table public.app_users enable row level security;
alter table public.daily_logs enable row level security;
alter table public.parsed_events enable row level security;

-- Force policies for table-owner access too. Supabase's privileged internal
-- roles can still bypass RLS, but app-owned roles should not accidentally do so.
alter table public.app_users force row level security;
alter table public.daily_logs force row level security;
alter table public.parsed_events force row level security;

-- Keep unauthenticated requests away from every app table. Authenticated users
-- only receive the read/create privileges the current product needs.
revoke all on table public.app_users from anon, authenticated;
revoke all on table public.daily_logs from anon, authenticated;
revoke all on table public.parsed_events from anon, authenticated;
revoke all on sequence public.parsed_events_id_seq from anon, authenticated;

grant select, insert on table public.app_users to authenticated;
grant select, insert on table public.daily_logs to authenticated;
grant select, insert on table public.parsed_events to authenticated;
grant usage on sequence public.parsed_events_id_seq to authenticated;

drop policy if exists "anonymous devices can read own app user" on public.app_users;
drop policy if exists "anonymous devices can create own app user" on public.app_users;
drop policy if exists "anonymous devices can read own daily logs" on public.daily_logs;
drop policy if exists "anonymous devices can create own daily logs" on public.daily_logs;
drop policy if exists "anonymous devices can read own parsed events" on public.parsed_events;
drop policy if exists "anonymous devices can create own parsed events" on public.parsed_events;

create policy "anonymous devices can read own app user"
on public.app_users
for select
to authenticated
using (
  (select auth.uid()) is not null
  and id = (select auth.uid())::text
  and ((select auth.jwt()) ->> 'is_anonymous') = 'true'
);

create policy "anonymous devices can create own app user"
on public.app_users
for insert
to authenticated
with check (
  (select auth.uid()) is not null
  and id = (select auth.uid())::text
  and ((select auth.jwt()) ->> 'is_anonymous') = 'true'
);

create policy "anonymous devices can read own daily logs"
on public.daily_logs
for select
to authenticated
using (
  (select auth.uid()) is not null
  and user_id = (select auth.uid())::text
  and ((select auth.jwt()) ->> 'is_anonymous') = 'true'
);

create policy "anonymous devices can create own daily logs"
on public.daily_logs
for insert
to authenticated
with check (
  (select auth.uid()) is not null
  and user_id = (select auth.uid())::text
  and ((select auth.jwt()) ->> 'is_anonymous') = 'true'
);

create policy "anonymous devices can read own parsed events"
on public.parsed_events
for select
to authenticated
using (
  (select auth.uid()) is not null
  and user_id = (select auth.uid())::text
  and ((select auth.jwt()) ->> 'is_anonymous') = 'true'
);

create policy "anonymous devices can create own parsed events"
on public.parsed_events
for insert
to authenticated
with check (
  (select auth.uid()) is not null
  and user_id = (select auth.uid())::text
  and ((select auth.jwt()) ->> 'is_anonymous') = 'true'
  and exists (
    select 1
    from public.daily_logs
    where daily_logs.log_id = parsed_events.log_id
      and daily_logs.user_id = parsed_events.user_id
  )
);
