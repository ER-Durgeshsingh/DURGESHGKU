-- CSEClass AI Attendance System - Full Supabase SQL Setup

create table if not exists teachers (
  teacher_id bigserial primary key,
  username text unique,
  email text unique,
  password text not null,
  name text not null,
  role text default 'teacher',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists students (
  student_id bigserial primary key,
  name text not null,
  face_embedding jsonb,
  voice_embedding jsonb,
  created_at timestamptz default now(),
  university_roll_number text,
  parent_email text,
  profile_update_count int default 0,
  profile_photo_url text,
  photo_uploaded boolean default false
);

create table if not exists subjects (
  subject_id bigserial primary key,
  subject_code text unique not null,
  name text not null,
  section text,
  teacher_id bigint references teachers(teacher_id) on delete cascade,
  created_at timestamptz default now()
);

create table if not exists subject_students (
  id bigserial primary key,
  subject_id bigint references subjects(subject_id) on delete cascade,
  student_id bigint references students(student_id) on delete cascade,
  created_at timestamptz default now(),
  unique(subject_id, student_id)
);

create table if not exists attendance_logs (
  attendance_id bigserial primary key,
  subject_id bigint references subjects(subject_id) on delete cascade,
  student_id bigint references students(student_id) on delete cascade,
  timestamp timestamptz not null default now(),
  is_present boolean not null default false,
  created_at timestamptz default now()
);

create table if not exists teacher_otps (
  otp_id bigserial primary key,
  teacher_id bigint references teachers(teacher_id) on delete cascade,
  otp_code text not null,
  purpose text not null check (purpose in ('login', 'reset_password')),
  expires_at timestamptz not null,
  used boolean default false,
  created_at timestamptz default now()
);

-- Missing columns safe update
alter table teachers add column if not exists username text unique;
alter table teachers add column if not exists email text unique;
alter table teachers add column if not exists role text default 'teacher';
alter table teachers add column if not exists updated_at timestamptz default now();

alter table students add column if not exists university_roll_number text;
alter table students add column if not exists parent_email text;
alter table students add column if not exists profile_update_count int default 0;
alter table students add column if not exists profile_photo_url text;
alter table students add column if not exists photo_uploaded boolean default false;

-- Indexes
create index if not exists idx_subjects_teacher_id on subjects(teacher_id);
create index if not exists idx_subject_students_subject_id on subject_students(subject_id);
create index if not exists idx_subject_students_student_id on subject_students(student_id);
create index if not exists idx_attendance_subject_id on attendance_logs(subject_id);
create index if not exists idx_attendance_student_id on attendance_logs(student_id);
create index if not exists idx_attendance_timestamp on attendance_logs(timestamp);
create index if not exists idx_teacher_otps_teacher_id on teacher_otps(teacher_id);

