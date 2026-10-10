-- Jmal C's Digital Literacy Class: student accounts, cloud progress, teacher dashboard.
-- Paste this whole file into Supabase > SQL Editor and click Run.
-- Safe to run again: it only creates what is missing and refreshes the rules.

-- ---------- tables ----------
create table if not exists public.profiles (
  id           uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default '',
  class_code   text not null default '',
  role         text not null default 'student' check (role in ('student','teacher')),
  created_at   timestamptz not null default now()
);

create table if not exists public.progress (
  user_id     uuid not null references auth.users(id) on delete cascade,
  app         text not null check (app in ('quest','practice')),
  data        jsonb not null default '{}'::jsonb,
  xp          integer not null default 0,
  best_scores jsonb not null default '{}'::jsonb,
  updated_at  timestamptz not null default now(),
  primary key (user_id, app)
);

create table if not exists public.attempts (
  id        bigint generated always as identity primary key,
  user_id   uuid not null default auth.uid() references auth.users(id) on delete cascade,
  test_id   text not null,
  test_name text,
  mode      text not null default 'test',
  score     integer not null default 0,
  total     integer not null default 0,
  by_domain jsonb not null default '{}'::jsonb,
  taken_at  timestamptz not null default now(),
  unique (user_id, test_id, taken_at)
);
alter table public.attempts add column if not exists test_name text;

create index if not exists profiles_class_code_idx on public.profiles (class_code);
create index if not exists attempts_user_idx on public.attempts (user_id, taken_at);

-- ---------- helpers ----------
-- The class code of the signed-in user, only if that user is a teacher. Otherwise null.
create or replace function public.teacher_class() returns text
language sql stable security definer set search_path = public as $$
  select class_code from public.profiles
  where id = auth.uid() and role = 'teacher' and class_code <> ''
$$;

-- True when uid is a student in the signed-in teacher's class.
create or replace function public.is_my_student(uid uuid) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (
    select 1 from public.profiles p
    where p.id = uid and p.class_code <> '' and p.class_code = public.teacher_class()
  )
$$;

revoke all on function public.teacher_class() from public, anon;
revoke all on function public.is_my_student(uuid) from public, anon;
grant execute on function public.teacher_class() to authenticated;
grant execute on function public.is_my_student(uuid) to authenticated;

-- Make a profile automatically when someone signs up (role is always 'student').
create or replace function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = public as $$
begin
  insert into public.profiles (id, display_name, class_code)
  values (
    new.id,
    left(coalesce(nullif(trim(new.raw_user_meta_data->>'display_name'), ''), split_part(coalesce(new.email, ''), '@', 1)), 40),
    upper(left(regexp_replace(coalesce(new.raw_user_meta_data->>'class_code', ''), '\s', '', 'g'), 20))
  )
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

-- Profiles for anyone who signed up before this file was run.
insert into public.profiles (id, display_name, class_code)
select u.id,
       left(coalesce(nullif(trim(u.raw_user_meta_data->>'display_name'), ''), split_part(coalesce(u.email, ''), '@', 1)), 40),
       upper(left(regexp_replace(coalesce(u.raw_user_meta_data->>'class_code', ''), '\s', '', 'g'), 20))
from auth.users u
on conflict (id) do nothing;

create or replace function public.touch_updated_at() returns trigger
language plpgsql as $$ begin new.updated_at = now(); return new; end $$;
drop trigger if exists progress_touch on public.progress;
create trigger progress_touch before insert or update on public.progress
  for each row execute function public.touch_updated_at();

-- ---------- permissions ----------
revoke all on public.profiles, public.progress, public.attempts from anon;
revoke all on public.profiles, public.progress, public.attempts from authenticated;
grant select, insert, delete on public.profiles to authenticated;
grant update (display_name, class_code) on public.profiles to authenticated;   -- nobody can change their own role
grant select, insert, update, delete on public.progress to authenticated;
grant select, insert, delete on public.attempts to authenticated;

alter table public.profiles enable row level security;
alter table public.progress enable row level security;
alter table public.attempts enable row level security;

-- profiles: you see yourself; a teacher also sees everyone with the same class code.
drop policy if exists "profiles read" on public.profiles;
create policy "profiles read" on public.profiles for select to authenticated
  using (id = auth.uid() or class_code = public.teacher_class());
drop policy if exists "profiles insert own" on public.profiles;
create policy "profiles insert own" on public.profiles for insert to authenticated
  with check (id = auth.uid() and role = 'student');
drop policy if exists "profiles update own" on public.profiles;
create policy "profiles update own" on public.profiles for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid());
drop policy if exists "profiles delete own" on public.profiles;
create policy "profiles delete own" on public.profiles for delete to authenticated
  using (id = auth.uid());

-- progress: read/write your own rows; a teacher can read rows of students in their class.
drop policy if exists "progress read" on public.progress;
create policy "progress read" on public.progress for select to authenticated
  using (user_id = auth.uid() or public.is_my_student(user_id));
drop policy if exists "progress insert own" on public.progress;
create policy "progress insert own" on public.progress for insert to authenticated
  with check (user_id = auth.uid());
drop policy if exists "progress update own" on public.progress;
create policy "progress update own" on public.progress for update to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());
drop policy if exists "progress delete own" on public.progress;
create policy "progress delete own" on public.progress for delete to authenticated
  using (user_id = auth.uid());

-- attempts: add your own results; a teacher can read results of students in their class.
drop policy if exists "attempts read" on public.attempts;
create policy "attempts read" on public.attempts for select to authenticated
  using (user_id = auth.uid() or public.is_my_student(user_id));
drop policy if exists "attempts insert own" on public.attempts;
create policy "attempts insert own" on public.attempts for insert to authenticated
  with check (user_id = auth.uid());
drop policy if exists "attempts delete own" on public.attempts;
create policy "attempts delete own" on public.attempts for delete to authenticated
  using (user_id = auth.uid());

-- ---------- make yourself the teacher (run AFTER you sign up in the app) ----------
-- Change the email, then run just this one line:
-- update public.profiles set role = 'teacher' where id = (select id from auth.users where email = 'YOUR-EMAIL@example.com');
