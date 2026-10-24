create table public.music_studio_projects (
 id uuid primary key default gen_random_uuid(), owner_id uuid not null references auth.users(id) on delete cascade,
 title text not null check(length(title) between 1 and 120), state jsonb not null,
 revision integer not null default 1 check(revision>0), updated_at timestamptz not null default now()
);
alter table public.music_studio_projects enable row level security;
create policy music_project_owner on public.music_studio_projects for all to authenticated using ((select auth.uid())=owner_id) with check ((select auth.uid())=owner_id);
grant select,insert,update,delete on public.music_studio_projects to authenticated;
revoke all on public.music_studio_projects from anon;
create index music_projects_owner_idx on public.music_studio_projects(owner_id);
create table public.music_studio_versions (
 id uuid primary key default gen_random_uuid(), project_id uuid not null references public.music_studio_projects(id) on delete cascade,
 owner_id uuid not null references auth.users(id) on delete cascade, label text not null, state jsonb not null, created_at timestamptz not null default now()
);
alter table public.music_studio_versions enable row level security;
create policy music_version_owner on public.music_studio_versions for all to authenticated using ((select auth.uid())=owner_id) with check ((select auth.uid())=owner_id and exists(select 1 from public.music_studio_projects p where p.id=project_id and p.owner_id=(select auth.uid())));
grant select,insert,delete on public.music_studio_versions to authenticated;
revoke all on public.music_studio_versions from anon;
create index music_versions_project_idx on public.music_studio_versions(project_id,created_at desc);
create index music_versions_owner_idx on public.music_studio_versions(owner_id);
insert into storage.buckets(id,name,public,file_size_limit,allowed_mime_types) values ('music-studio','music-studio',false,52428800,array['audio/wav','audio/x-wav','audio/mpeg','audio/ogg','application/json']);
create policy music_audio_read on storage.objects for select to authenticated using(bucket_id='music-studio' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy music_audio_insert on storage.objects for insert to authenticated with check(bucket_id='music-studio' and (storage.foldername(name))[1]=(select auth.uid())::text);
create policy music_audio_delete on storage.objects for delete to authenticated using(bucket_id='music-studio' and (storage.foldername(name))[1]=(select auth.uid())::text);
update storage.buckets set file_size_limit=104857600 where id='music-studio';
