-- 留言板建表脚本
-- 用法：Supabase 控制台 → 左侧 SQL Editor → New query → 粘贴整段 → Run

create table if not exists public.messages (
  id         bigint generated always as identity primary key,
  nick       text        not null default '匿名',
  body       text        not null,
  created_at timestamptz not null default now(),
  constraint nick_len check (char_length(nick) between 1 and 20),
  constraint body_len check (char_length(body) between 1 and 200)
);

create index if not exists messages_created_at_idx
  on public.messages (created_at desc);

-- 开启行级安全：匿名用户只能读、只能插入，不能改也不能删
alter table public.messages enable row level security;

drop policy if exists "anon can read messages" on public.messages;
create policy "anon can read messages"
  on public.messages for select
  to anon
  using (true);

drop policy if exists "anon can post messages" on public.messages;
create policy "anon can post messages"
  on public.messages for insert
  to anon
  with check (
    char_length(nick) between 1 and 20
    and char_length(body) between 1 and 200
  );

-- 表级授权：Supabase 新项目不会自动把新建表的权限给 anon，
-- 少了这三行会报 permission denied for table messages
grant usage on schema public to anon, authenticated;
grant select, insert on public.messages to anon, authenticated;
grant usage, select on all sequences in schema public to anon, authenticated;

-- 没有 update / delete 策略，所以前端拿到 anon key 也删不掉别人的留言。
-- 删留言：控制台 → Table Editor → messages → 勾选行 → Delete。
