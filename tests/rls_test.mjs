// RLS tests for supabase/schema.sql in real Postgres (PGlite). Setup: npm i @electric-sql/pglite@0.2  Run: node tests/rls_test.mjs
import { PGlite } from '@electric-sql/pglite';
import fs from 'fs';
const db = new PGlite();
const pre = `
create role anon nologin; create role authenticated nologin;
create schema auth;
create table auth.users(id uuid primary key, email text, raw_user_meta_data jsonb default '{}');
create function auth.uid() returns uuid language sql stable as $$ select nullif(current_setting('request.jwt.claim.sub', true),'')::uuid $$;
grant usage on schema auth to anon, authenticated; grant execute on function auth.uid() to anon, authenticated;
grant usage on schema public to anon, authenticated;
`;
await db.exec(pre);
const schema = fs.readFileSync(new URL('../supabase/schema.sql', import.meta.url),'utf8');
await db.exec(schema); await db.exec(schema); // idempotent
const T='11111111-1111-1111-1111-111111111111', A='22222222-2222-2222-2222-222222222222', B='33333333-3333-3333-3333-333333333333', X='44444444-4444-4444-4444-444444444444';
await db.exec(`insert into auth.users values
 ('${T}','teach@x.com','{"display_name":"Jmal","class_code":" dl 2026 "}'),
 ('${A}','a@x.com','{"display_name":"Ana","class_code":"DL2026"}'),
 ('${B}','b@x.com','{"display_name":"Ben","class_code":"dl2026"}'),
 ('${X}','x@x.com','{"display_name":"Xo","class_code":"OTHER"}');`);
let ok=0, fail=0; const t=(c,m)=>{ if(c){ok++} else {fail++; console.log('FAIL',m)} };
const P = await db.query('select id,display_name,class_code,role from public.profiles order by display_name');
t(P.rows.length===4 && P.rows.every(r=>r.role==='student') && P.rows.find(r=>r.display_name==='Jmal').class_code==='DL2026', 'trigger profiles '+JSON.stringify(P.rows));
async function as(uid, sql, params){ await db.exec(`set role authenticated; select set_config('request.jwt.claim.sub','${uid}',false);`); try { return await db.query(sql, params||[]); } finally { await db.exec('reset role;'); } }
async function err(uid, sql){ try{ await as(uid, sql); return null } catch(e){ return e.message } }
// students write own progress
await as(A, `insert into public.progress(user_id,app,data,xp,best_scores) values('${A}','quest','{"xp":50}',50,'{}') on conflict (user_id,app) do update set data=excluded.data, xp=excluded.xp`);
await as(A, `insert into public.progress(user_id,app,data,xp,best_scores) values('${A}','quest','{"xp":70}',70,'{}') on conflict (user_id,app) do update set data=excluded.data, xp=excluded.xp`);
await as(B, `insert into public.progress(user_id,app,data,xp) values('${B}','practice','{}',0)`);
await as(X, `insert into public.progress(user_id,app,data,xp) values('${X}','quest','{}',5)`);
await as(A, `insert into public.attempts(user_id,test_id,mode,score,total,by_domain,taken_at) values('${A}','final','test',40,45,'{"1":{"c":5,"n":6}}','2026-10-10T05:00:00Z') on conflict do nothing`);
await as(A, `insert into public.attempts(user_id,test_id,mode,score,total,by_domain,taken_at) values('${A}','final','test',40,45,'{"1":{"c":5,"n":6}}','2026-10-10T05:00:00Z') on conflict do nothing`);
t((await as(A,'select * from public.attempts')).rows.length===1,'attempt dedupe');
t((await as(A,'select xp from public.progress')).rows[0].xp===70,'upsert updated');
// isolation
t((await as(A,'select * from public.progress')).rows.length===1,'student sees only own progress');
t((await as(A,'select * from public.profiles')).rows.length===1,'student sees only own profile');
t((await as(B,'select * from public.attempts')).rows.length===0,'B cannot see A attempts');
t(!!(await err(A, `insert into public.progress(user_id,app,data) values('${B}','quest','{}')`)),'cannot write others progress');
const upd = await as(A, `update public.progress set xp=9999 where user_id='${B}'`); t(upd.affectedRows===0,'cannot update others');
t(!!(await err(A, `update public.profiles set role='teacher' where id='${A}'`)),'student cannot self-promote');
t(!!(await err(A, `insert into public.attempts(user_id,test_id,score,total) values('${B}','final',1,1)`)),'cannot add attempts for others');
t(!!(await err(A, `update public.attempts set score=45`)),'attempts not updatable');
// anon
t(!!(await (async()=>{ await db.exec('set role anon'); try{ await db.query('select * from public.progress'); return null}catch(e){return e.message} finally{ await db.exec('reset role') } })()),'anon blocked');
// teacher before promote
t((await as(T,'select * from public.progress')).rows.length===0,'unpromoted teacher sees nothing');
// promote (one-liner from file)
const line = schema.split('\n').find(l=>l.startsWith('-- update public.profiles set role')).slice(3).replace('YOUR-EMAIL@example.com','teach@x.com');
await db.exec(line);
const tp=(await as(T,'select display_name from public.profiles order by 1')).rows.map(r=>r.display_name);
t(JSON.stringify(tp)==='["Ana","Ben","Jmal"]','teacher sees class profiles '+JSON.stringify(tp));
t((await as(T,'select * from public.progress')).rows.length===2,'teacher sees class progress, not OTHER');
t((await as(T,'select * from public.attempts')).rows.length===1,'teacher sees class attempts');
t((await as(T, `update public.progress set xp=1 where user_id='${A}'`)).affectedRows===0,'teacher cannot edit student progress');
t((await as(A,'select * from public.profiles')).rows.length===1,'student still isolated after teacher promote');
// change class code allowed, role column not
await as(A, `update public.profiles set class_code='NEW' where id='${A}'`);
t((await as(T,'select * from public.progress')).rows.length===1,'student moved class -> teacher no longer sees');
// updated_at touched
console.log(`RLS tests: ${ok} passed, ${fail} failed`); process.exit(fail?1:0);
