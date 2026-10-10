"""Headless Chrome tests.  Run: python3 tests/browser_test.py
Part 1: no config (how the live site ships): apps behave as before, offline works, no errors.
Part 2: cloud mode against an in-memory mock of Supabase using the REAL supabase-js from the CDN."""
import asyncio, json, os, sys, subprocess, socket, time, re
sys.path.insert(0, os.path.dirname(__file__))
from playwright.async_api import async_playwright
from mock_supabase import MockSupabase
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 8765; BASE = f'http://127.0.0.1:{PORT}/'
MOCK = 'https://mock-project.supabase.co'
CFG = f'window.JC_CONFIG={{SUPABASE_URL:"{MOCK}",SUPABASE_ANON_KEY:"test-anon-key-1234567890abcdef"}};'
SHOTS = '/tmp/jc_shots/'; os.makedirs(SHOTS, exist_ok=True)
results = []
def check(cond, msg):
    results.append((bool(cond), msg)); print(('PASS ' if cond else 'FAIL ') + msg)

def watch(page, errs, ext):
    page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
    page.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
    page.on('request', lambda r: ext.append(r.url) if not r.url.startswith(BASE) and not r.url.startswith('data:') else None)
    page.on('dialog', lambda d: asyncio.ensure_future(d.accept()))

async def part1(b):
    print('--- Part 1: no config (device-only mode)')
    ctx = await b.new_context(viewport={'width': 1280, 'height': 860})
    errs, ext = [], []
    p = await ctx.new_page(); watch(p, errs, ext)
    await p.goto(BASE); await p.wait_for_load_state('networkidle')
    check(await p.title() == "Jmal C's Digital Literacy Class", 'landing title')
    check(await p.locator('#jcs-chip').count() == 0, 'landing: no sign-in chip without config')
    check(await p.locator('#cloud-note').is_hidden(), 'landing: cloud note hidden without config')
    check(await p.locator('footer a[href="teacher.html"]').count() == 1, 'landing: discreet teacher link in footer')
    await p.evaluate("navigator.serviceWorker.ready")
    await p.screenshot(path=SHOTS + 'p1_landing.png', full_page=True)
    # Quest
    await p.goto(BASE + 'quest.html'); await p.wait_for_load_state('networkidle')
    check(await p.evaluate('window.JCSync && JCSync.enabled === false'), 'quest: sync module loaded and disabled')
    check(await p.locator('#jcs-chip').count() == 0, 'quest: no chip without config')
    await p.fill('#nm', 'Ana'); await p.click('#nmgo')
    await p.click('.lvl[data-id="security"]'); await p.wait_for_timeout(200)
    st = await p.evaluate("JSON.parse(localStorage.getItem('ic3quest_v1'))")
    check(st and st['name'] == 'Ana' and st['xp'] >= 5, f'quest: progress saves to localStorage (xp={st and st["xp"]})')
    await p.reload(); await p.wait_for_load_state('networkidle')
    check(await p.locator('#xp').inner_text() == str(st['xp']), 'quest: progress survives reload')
    # Practice
    await p.goto(BASE + 'practice.html'); await p.wait_for_load_state('networkidle')
    check(await p.locator('#jcs-chip').count() == 0, 'practice: no chip without config')
    await p.click('#nav button[data-v="final"]'); await p.click('#fx'); await p.evaluate('__lab.finish()')
    lab = await p.evaluate("JSON.parse(localStorage.getItem('ic3lab_v1'))")
    check(lab and len(lab['history']) == 1 and lab['history'][0]['test'] == 'final', 'practice: Final Exam Review result saved locally')
    # Teacher page without config
    await p.goto(BASE + 'teacher.html'); await p.wait_for_load_state('networkidle')
    check('not turned on yet' in await p.inner_text('#app'), 'teacher: explains cloud is not set up')
    check(not ext, 'no requests leave the site in no-config mode ' + str(ext[:3]))
    check(not errs, 'no console errors in no-config mode ' + str(errs[:3]))
    # Offline
    await ctx.set_offline(True)
    off_errs = []
    for page in ['', 'quest.html', 'practice.html', 'teacher.html']:
        await p.goto(BASE + page)
        ok = await p.evaluate("document.title")
        check(ok and 'Offline' not in ok, f'offline: {page or "index"} loads from cache ({ok})')
    await p.goto(BASE + 'quest.html'); check(await p.locator('#xp').inner_text() == str(st['xp']), 'offline: quest progress still there')
    await ctx.close()

async def cloud_ctx(b, mock, **kw):
    ctx = await b.new_context(viewport=kw.get('viewport', {'width': 1280, 'height': 860}), service_workers='block', accept_downloads=True)
    await ctx.route('**/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=CFG))
    await ctx.route(MOCK + '/**', mock.handle)
    return ctx

async def signup(p, name, code, email, pw='secret123'):
    await p.click('#jcs-chip'); await p.click('#jcs-tup')
    await p.fill('#jcs-name', name); await p.fill('#jcs-code', code); await p.fill('#jcs-email', email); await p.fill('#jcs-pw', pw)
    await p.click('#jcs-go'); await p.wait_for_selector('.jcs-ov', state='detached', timeout=8000)

async def signin(p, email, pw='secret123'):
    await p.click('#jcs-chip'); await p.fill('#jcs-email', email); await p.fill('#jcs-pw', pw)
    await p.click('#jcs-go')

async def part2(b):
    print('--- Part 2: cloud mode with mock Supabase + real supabase-js')
    mock = MockSupabase(); errs, ext = [], []
    # Device 1: has local progress before making an account
    A = await cloud_ctx(b, mock); p = await A.new_page(); watch(p, errs, ext)
    await p.goto(BASE + 'quest.html')
    await p.evaluate("""localStorage.setItem('ic3quest_v1',JSON.stringify({name:'',xp:120,seen:{mobile:[0,1]},quiz:{mobile:85},qok:{},games:{},sims:{},mission:{},badges:['lvl_mobile'],flips:3,days:[],boss:0}))""")
    await p.reload(); await p.wait_for_selector('#jcs-chip')
    check('Sign in' in await p.inner_text('#jcs-chip'), 'quest: chip shows "Sign in" when config is set')
    await p.click('#jcs-chip'); await p.click('#jcs-tup'); await p.screenshot(path=SHOTS + 'p2_signup.png')
    await p.click('#jcs-x')
    # validation messages
    await p.click('#jcs-chip'); await p.click('#jcs-tup'); await p.fill('#jcs-email', 'ana@school.org'); await p.fill('#jcs-pw', 'secret123'); await p.click('#jcs-go')
    await p.wait_for_selector('#jcs-err:not([hidden])'); check('first name' in (await p.inner_text('#jcs-err')), 'signup: asks for first name')
    await p.click('#jcs-x')
    await signup(p, 'Ana', 'dl 2026', 'ana@school.org')
    await p.wait_for_function("document.querySelector('#jcs-chip').textContent.indexOf('Ana')>=0")
    check('✅' in await p.inner_text('#jcs-chip'), 'quest: chip shows signed in name')
    uid = mock.users['ana@school.org']['id']
    check(mock.profiles[uid]['class_code'] == 'DL2026' and mock.profiles[uid]['display_name'] == 'Ana', 'profile created with display name + normalized class code')
    await p.wait_for_timeout(300)
    row = mock.progress.get((uid, 'quest'))
    check(row and row['xp'] == 120 and row['data']['quiz']['mobile'] == 85, 'local progress uploaded on sign up')
    check(await p.evaluate("__quest.state().name") == 'Ana', 'quest: display name fills the empty Quest name')
    await p.screenshot(path=SHOTS + 'p2_quest_signedin.png')
    await p.click('.lvl[data-id="security"]'); await p.wait_for_timeout(2300)
    row = mock.progress.get((uid, 'quest'))
    check(row['xp'] == 125 and 'security' in row['data']['seen'], f'save is debounced and synced (cloud xp={row["xp"]})')
    # Practice on same device: shared session
    await p.goto(BASE + 'practice.html'); await p.wait_for_function("document.querySelector('#jcs-chip')&&document.querySelector('#jcs-chip').textContent.indexOf('Ana')>=0")
    check(True, 'practice: already signed in (shared session)')
    await p.click('#nav button[data-v="final"]'); await p.click('#fx'); await p.evaluate('__lab.finish()'); await p.wait_for_timeout(2300)
    fin = [a for a in mock.attempts if a['user_id'] == uid and a['test_id'] == 'final']
    check(len(fin) == 1 and fin[0]['total'] == 45 and isinstance(fin[0]['by_domain'], dict) and fin[0]['by_domain'], 'Final Exam Review attempt saved to attempts table with by_domain')
    check(mock.progress.get((uid, 'practice')) and mock.progress[(uid, 'practice')]['best_scores'].get('final:test') == 0, 'practice best_scores synced')
    await p.screenshot(path=SHOTS + 'p2_practice_signedin.png')
    # Mobile header layout
    m = await A.new_page(); await m.set_viewport_size({'width': 390, 'height': 800}); await m.goto(BASE + 'quest.html'); await m.wait_for_selector('#jcs-chip')
    await m.wait_for_timeout(500); await m.screenshot(path=SHOTS + 'p2_quest_mobile.png'); await m.goto(BASE + 'practice.html'); await m.wait_for_timeout(800); await m.screenshot(path=SHOTS + 'p2_practice_mobile.png'); await m.close()

    # Device 2: different local progress, signs in -> merge (union / higher)
    Bc = await cloud_ctx(b, mock); q = await Bc.new_page(); watch(q, errs, ext)
    await q.goto(BASE + 'quest.html')
    await q.evaluate("""localStorage.setItem('ic3quest_v1',JSON.stringify({name:'Annie',xp:40,seen:{cloud:[0]},quiz:{mobile:60,cloud:90},qok:{},games:{},sims:{'cloud:0':1},mission:{},badges:['scam'],flips:50,days:['2026-10-09'],boss:70}))""")
    await q.reload(); await q.wait_for_selector('#jcs-chip')
    await signin(q, 'ana@school.org', 'wrongpass'); await q.wait_for_selector('#jcs-err:not([hidden])')
    check('not right' in await q.inner_text('#jcs-err'), 'wrong password shows friendly message')
    await q.fill('#jcs-pw', 'secret123'); await q.click('#jcs-go'); await q.wait_for_selector('.jcs-ov', state='detached')
    await q.wait_for_function("__quest.state().xp===125"); await q.wait_for_timeout(400)
    s = await q.evaluate('__quest.state()')
    check(s['xp'] == 125 and s['quiz'] == {'mobile': 85, 'cloud': 90} and sorted(s['badges']) == ['lvl_mobile', 'scam'] and s['boss'] == 70 and s['name'] == 'Annie',
          'device 2 merge: higher XP/quiz/boss, union of badges, local name kept')
    check(await q.inner_text('#xp') == '125', 'device 2 header refreshed after merge')
    c = mock.progress[(uid, 'quest')]['data']
    check(sorted(c['badges']) == ['lvl_mobile', 'scam'] and c['sims'] == {'cloud:0': 1}, 'merged progress pushed back to cloud')
    await q.goto(BASE + 'practice.html'); await q.wait_for_selector('#jcs-chip')
    await q.wait_for_function("__lab.state().history.length===1")
    check(True, 'device 2 practice pulled cloud history (Final Exam Review attempt)')
    # sign out clears device
    await q.click('#jcs-chip'); await q.click('#jcs-out'); await q.wait_for_load_state('load'); await q.wait_for_selector('#jcs-chip')
    await q.wait_for_function("document.querySelector('#jcs-chip').textContent.indexOf('Sign in')>=0")
    left = await q.evaluate("[localStorage.getItem('ic3quest_v1'),localStorage.getItem('ic3lab_v1')]")
    check(left[0] is None and left[1] is None, 'sign out removes progress from this device (it is in the cloud)')
    check(await q.evaluate('__lab.state().history.length') == 0, 'after sign out the app starts fresh')

    # Other students
    for nm, code, em in [('Ben', 'DL2026', 'ben@school.org'), ('Xo', 'OTHER1', 'xo@school.org')]:
        cx = await cloud_ctx(b, mock); pg = await cx.new_page(); watch(pg, errs, ext)
        await pg.goto(BASE + 'practice.html'); await pg.wait_for_selector('#jcs-chip'); await signup(pg, nm, code, em)
        await pg.wait_for_function(f"document.querySelector('#jcs-chip').textContent.indexOf('{nm}')>=0")
        await pg.click('#nav button[data-v="final"]'); await pg.click('#fx'); await pg.evaluate('__lab.finish()'); await pg.wait_for_timeout(2000); await cx.close()
    # duplicate account message
    cx = await cloud_ctx(b, mock); pg = await cx.new_page(); watch(pg, errs, ext); await pg.goto(BASE); await pg.wait_for_selector('#jcs-chip')
    check(await pg.locator('#cloud-note').is_visible(), 'landing: optional account note shown when config is set')
    await pg.click('#jcs-chip'); await pg.click('#jcs-tup'); await pg.fill('#jcs-name', 'Ana'); await pg.fill('#jcs-code', 'DL2026'); await pg.fill('#jcs-email', 'ana@school.org'); await pg.fill('#jcs-pw', 'secret123'); await pg.click('#jcs-go')
    await pg.wait_for_selector('#jcs-err:not([hidden])'); check('already has an account' in await pg.inner_text('#jcs-err'), 'duplicate email shows friendly message'); await cx.close()

    # Teacher
    T = await cloud_ctx(b, mock); t = await T.new_page(); watch(t, errs, ext)
    await t.goto(BASE); await t.wait_for_selector('#jcs-chip'); await signup(t, 'Jmal', 'DL2026', 'jmal@school.org')
    await t.goto(BASE + 'teacher.html'); await t.wait_for_selector('#app h2')
    check('not a teacher account' in await t.inner_text('#app'), 'teacher page: blocks non-teacher accounts')
    mock.promote('jmal@school.org')
    await t.reload(); await t.wait_for_selector('#tb')
    names = await t.locator('#tb tbody tr[data-id] td:first-child b').all_inner_texts()
    check(sorted(names) == ['Ana', 'Ben'], f'teacher sees only students in class DL2026 ({names})')
    txt = await t.inner_text('#tb')
    check('125' in txt and 'Button Pusher' in txt, 'teacher table shows Quest XP and rank')
    await t.screenshot(path=SHOTS + 'p2_teacher.png', full_page=True)
    await t.click('th[data-k="xp"]'); first = await t.locator('#tb tbody tr[data-id] td:first-child b').first.inner_text()
    check(first == 'Ana', 'sort by XP (highest first)')
    await t.click('th[data-k="xp"]'); first = await t.locator('#tb tbody tr[data-id] td:first-child b').first.inner_text()
    check(first == 'Ben', 'sort toggles direction')
    await t.click('#tb tbody tr[data-id]:has-text("Ana")'); await t.wait_for_selector('tr.det')
    det = await t.inner_text('tr.det'); check('Final Exam Review by domain' in det and 'Mobile Devices' in det, 'row expands with per-level, per-domain and per-test details')
    await t.screenshot(path=SHOTS + 'p2_teacher_detail.png', full_page=True)
    async with t.expect_download() as dl: await t.click('#csv')
    d = await dl.value; path = await d.path(); csv = open(path, encoding='utf-8-sig', newline='').read()
    lines = csv.strip().split('\r\n')
    check(len(lines) == 3 and lines[0].startswith('"Student","Last active","Quest XP"') and 'Final D1' in lines[0], f'CSV export has header + 2 students ({d.suggested_filename})')
    mt = await T.new_page(); await mt.set_viewport_size({'width': 390, 'height': 800}); await mt.goto(BASE + 'teacher.html'); await mt.wait_for_selector('#tb'); await mt.screenshot(path=SHOTS + 'p2_teacher_mobile.png', full_page=True); await mt.close()

    # Supabase down: app keeps working locally
    mock.down = True
    D = await cloud_ctx(b, mock); r = await D.new_page(); derrs = []; watch(r, derrs, [])
    await r.goto(BASE + 'quest.html'); await r.wait_for_selector('#jcs-chip')
    await r.click('#jcs-chip'); await r.fill('#jcs-email', 'ana@school.org'); await r.fill('#jcs-pw', 'secret123'); await r.click('#jcs-go')
    await r.wait_for_selector('#jcs-err:not([hidden])'); e = await r.inner_text('#jcs-err'); await r.click('#jcs-x')
    check(len(e) > 5, f'Supabase down: sign in shows a message ({e[:60]})')
    await r.fill('#nm', 'Zed'); await r.click('#nmgo'); await r.click('.lvl[data-id="cloud"]')
    check((await r.evaluate("JSON.parse(localStorage.getItem('ic3quest_v1')).xp")) >= 5, 'Supabase down: progress still saves on the device')
    check(not [x for x in derrs if 'pageerror' in x], 'Supabase down: no page errors ' + str(derrs[:2]))
    mock.down = False; await D.close()

    # Unreachable host (real network failure), signed-out: no errors, app works
    E = await b.new_context(service_workers='block')
    await E.route('**/config.js', lambda rt: rt.fulfill(status=200, content_type='application/javascript', body='window.JC_CONFIG={SUPABASE_URL:"https://127.0.0.1:9",SUPABASE_ANON_KEY:"test-anon-key-1234567890abcdef"};'))
    s2 = await E.new_page(); e2 = []; watch(s2, e2, [])
    await s2.goto(BASE + 'practice.html'); await s2.wait_for_selector('#jcs-chip'); await s2.wait_for_timeout(800)
    check(not e2, 'unreachable Supabase + signed out: no console errors ' + str(e2[:2]))
    await E.close()
    # CDN blocked (e.g. school filter): falls back to device-only, no chip errors
    F = await b.new_context(service_workers='block')
    await F.route('**/config.js', lambda rt: rt.fulfill(status=200, content_type='application/javascript', body=CFG))
    await F.route('https://cdn.jsdelivr.net/**', lambda rt: rt.abort())
    s3 = await F.new_page(); e3 = []; watch(s3, e3, [])
    await s3.goto(BASE + 'quest.html'); await s3.wait_for_timeout(800)
    await s3.fill('#nm', 'Kai'); await s3.click('#nmgo')
    check(await s3.evaluate("JSON.parse(localStorage.getItem('ic3quest_v1')).name") == 'Kai', 'CDN blocked: app still works and saves locally')
    check(await s3.evaluate("JCSync._state()") == 'offline', 'CDN blocked: sync goes quiet (offline state)')
    await F.close()
    bad = [x for x in errs if 'pageerror' in x]
    check(not bad, 'no page errors in cloud flows ' + str(bad[:3]))
    other = [x for x in errs if 'pageerror' not in x and 'status of 4' not in x]
    check(not other, 'no unexpected console errors in cloud flows ' + str(other[:3]))
    stray = [u for u in ext if not (u.startswith(MOCK) or u.startswith('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/'))]
    check(not stray, 'only the Supabase project and the pinned library are contacted ' + str(stray[:3]))

async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try: socket.create_connection(('127.0.0.1', PORT), .2).close(); break
        except OSError: time.sleep(.1)
    try:
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome')
            await part1(b); await part2(b); await b.close()
    finally: srv.terminate()
    f = [m for ok, m in results if not ok]
    print(f'\n{len(results) - len(f)}/{len(results)} checks passed'); sys.exit(1 if f else 0)
asyncio.run(main())
