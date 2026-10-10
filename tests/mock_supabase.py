"""A tiny in-memory stand-in for the Supabase Auth + REST API, used with Playwright's
page routing so the REAL supabase-js library can be tested without a real project.
It mirrors the Row Level Security rules in supabase/schema.sql."""
import json, base64, time, uuid, re
from urllib.parse import urlparse, parse_qs

def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip('=')

class MockSupabase:
    def __init__(self):
        self.users = {}      # email -> {id,email,password,meta}
        self.tokens = {}     # token -> uid
        self.profiles, self.progress, self.attempts = {}, {}, []
        self.down = False
        self.log = []
    # ---- helpers
    def token_for(self, uid):
        tok = 'h.' + b64({'sub': uid, 'role': 'authenticated', 'exp': int(time.time()) + 3600, 'aud': 'authenticated'}) + '.s'
        self.tokens[tok] = uid; return tok
    def session(self, u):
        return {'access_token': self.token_for(u['id']), 'token_type': 'bearer', 'expires_in': 3600, 'expires_at': int(time.time()) + 3600,
                'refresh_token': uuid.uuid4().hex, 'user': self.user_obj(u)}
    def user_obj(self, u):
        return {'id': u['id'], 'aud': 'authenticated', 'role': 'authenticated', 'email': u['email'], 'user_metadata': u['meta'],
                'app_metadata': {'provider': 'email'}, 'created_at': '2026-10-10T00:00:00Z', 'email_confirmed_at': '2026-10-10T00:00:00Z'}
    def teacher_class(self, uid):
        p = self.profiles.get(uid)
        return p['class_code'] if p and p['role'] == 'teacher' and p['class_code'] else None
    def is_my_student(self, me, uid):
        tc = self.teacher_class(me); p = self.profiles.get(uid)
        return bool(tc and p and p['class_code'] == tc)
    def promote(self, email):
        self.profiles[self.users[email]['id']]['role'] = 'teacher'
    # ---- routing
    def handle(self, route, request):
        u = urlparse(request.url); path = u.path; q = parse_qs(u.query)
        self.log.append((request.method, path + ('?' + u.query if u.query else '')))
        hdrs = {'access-control-allow-origin': '*', 'access-control-allow-headers': '*', 'access-control-allow-methods': '*', 'access-control-expose-headers': '*'}
        if request.method == 'OPTIONS': return route.fulfill(status=204, headers=hdrs)
        if self.down: return route.fulfill(status=503, headers=hdrs, body='{"message":"Service unavailable"}', content_type='application/json')
        def out(status, body=None, extra=None):
            h = dict(hdrs); h.update(extra or {})
            return route.fulfill(status=status, headers=h, content_type='application/json', body='' if body is None else json.dumps(body))
        if request.headers.get('apikey') != 'test-anon-key-1234567890abcdef': return out(401, {'message': 'Invalid API key'})
        body = request.post_data_json if request.post_data else None
        if path == '/auth/v1/signup':
            if body['email'] in self.users: return out(422, {'code': 422, 'error_code': 'user_already_exists', 'msg': 'User already registered'})
            usr = {'id': str(uuid.uuid4()), 'email': body['email'], 'password': body['password'], 'meta': body.get('data') or {}}
            self.users[body['email']] = usr
            md = usr['meta']  # trigger handle_new_user
            self.profiles[usr['id']] = {'id': usr['id'], 'display_name': (md.get('display_name') or '').strip()[:40] or usr['email'].split('@')[0],
                                        'class_code': re.sub(r'\s', '', md.get('class_code') or '').upper()[:20], 'role': 'student', 'created_at': '2026-10-10T05:00:00+00:00'}
            return out(200, self.session(usr))
        if path == '/auth/v1/token':
            usr = self.users.get(body.get('email'))
            if not usr or usr['password'] != body.get('password'):
                return out(400, {'code': 400, 'error_code': 'invalid_credentials', 'msg': 'Invalid login credentials'})
            return out(200, self.session(usr))
        if path == '/auth/v1/logout': return out(204)
        auth = request.headers.get('authorization', '')[7:]
        uid = self.tokens.get(auth)
        if path == '/auth/v1/user':
            usr = next((x for x in self.users.values() if x['id'] == uid), None)
            return out(200, self.user_obj(usr)) if usr else out(401, {'msg': 'no'})
        m = re.match(r'/rest/v1/(\w+)$', path)
        if not m: return out(404, {'message': 'not found'})
        if not uid: return out(401, {'message': 'permission denied'})
        table = m.group(1)
        filters = {k: v[0][3:] for k, v in q.items() if v[0].startswith('eq.')}
        prefer = request.headers.get('prefer', '')
        if request.method == 'GET':
            if table == 'profiles': rows = [p for p in self.profiles.values() if p['id'] == uid or p['class_code'] == self.teacher_class(uid)]
            elif table == 'progress': rows = [r for r in self.progress.values() if r['user_id'] == uid or self.is_my_student(uid, r['user_id'])]
            else: rows = [r for r in self.attempts if r['user_id'] == uid or self.is_my_student(uid, r['user_id'])]
            rows = [r for r in rows if all(str(r.get(k)) == v for k, v in filters.items())]
            if 'order' in q:
                col = q['order'][0].split('.')[0]; rows = sorted(rows, key=lambda r: r[col])
            if 'select' in q and q['select'][0] != '*':
                cols = q['select'][0].split(','); rows = [{c: r.get(c) for c in cols} for r in rows]
            if 'vnd.pgrst.object' in request.headers.get('accept', ''):
                if len(rows) != 1: return out(406, {'code': 'PGRST116', 'message': 'JSON object requested, multiple (or no) rows returned'})
                return out(200, rows[0])
            return out(200, rows)
        if request.method == 'POST':
            rows = body if isinstance(body, list) else [body]
            if table == 'profiles':
                for r in rows:
                    if r.get('id') != uid or r.get('role', 'student') != 'student': return out(403, {'code': '42501', 'message': 'new row violates row-level security policy'})
                    if r['id'] in self.profiles: return out(409, {'code': '23505', 'message': 'duplicate key'})
                    self.profiles[r['id']] = dict({'role': 'student', 'created_at': '2026-10-10T05:00:00+00:00'}, **r)
                return out(201)
            if table == 'progress':
                assert q.get('on_conflict', [''])[0] == 'user_id,app', q
                assert 'resolution=merge-duplicates' in prefer, prefer
                for r in rows:
                    if r['user_id'] != uid: return out(403, {'code': '42501', 'message': 'new row violates row-level security policy'})
                    self.progress[(r['user_id'], r['app'])] = dict(r, updated_at=time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime()))
                return out(201)
            if table == 'attempts':
                assert q.get('on_conflict', [''])[0] == 'user_id,test_id,taken_at', q
                assert 'resolution=ignore-duplicates' in prefer, prefer
                for r in rows:
                    if r['user_id'] != uid: return out(403, {'code': '42501', 'message': 'new row violates row-level security policy'})
                    if not any(a['user_id'] == uid and a['test_id'] == r['test_id'] and a['taken_at'] == r['taken_at'] for a in self.attempts):
                        self.attempts.append(dict(r))
                return out(201)
        return out(405, {'message': 'method not allowed'})
