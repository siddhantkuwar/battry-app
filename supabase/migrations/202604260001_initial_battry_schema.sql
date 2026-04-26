create extension if not exists pgcrypto;

create table if not exists app_users (
  id text primary key,
  created_at timestamptz not null default now()
);

create table if not exists daily_logs (
  log_id uuid primary key default gen_random_uuid(),
  user_id text not null references app_users(id) on delete cascade,
  text text not null,
  normalized_text text not null,
  logged_at timestamptz not null,
  battery_before smallint not null,
  battery_after smallint not null,
  created_at timestamptz not null default now(),
  constraint daily_logs_text_not_blank check (length(btrim(text)) > 0),
  constraint daily_logs_text_max_length check (char_length(text) <= 500),
  constraint daily_logs_battery_before_range check (battery_before between 0 and 100),
  constraint daily_logs_battery_after_range check (battery_after between 0 and 100)
);

create table if not exists parsed_events (
  id bigint generated always as identity primary key,
  log_id uuid not null references daily_logs(log_id) on delete cascade,
  user_id text not null references app_users(id) on delete cascade,
  label text not null,
  direction text not null,
  weight smallint not null,
  event_order smallint not null,
  created_at timestamptz not null default now(),
  constraint parsed_events_direction_check check (direction in ('up', 'down')),
  constraint parsed_events_label_not_blank check (length(btrim(label)) > 0),
  constraint parsed_events_event_order_nonnegative check (event_order >= 0)
);

create index if not exists daily_logs_user_logged_at_idx
  on daily_logs (user_id, logged_at desc, created_at desc);

create index if not exists parsed_events_log_id_idx
  on parsed_events (log_id);

create index if not exists parsed_events_user_label_idx
  on parsed_events (user_id, label);

alter table app_users enable row level security;
alter table daily_logs enable row level security;
alter table parsed_events enable row level security;
