"""'Currently on' + heartbeat + teacher Status/auto-refresh tests (mock Supabase, real supabase-js).
Run: python3 tests/now_test.py"""
import asyncio, os, sys, time, socket, subprocess, json
sys.path.insert(0, os.path.dirname(__file__))
import browser_test as bt
from browser_test import cloud_ctx, signup, watch, check, results, BASE, SITE, PORT, SHOTS
from mock_supabase import MockSupabase
from playwright.async_api import async_playwright
FAST = 'window.JC_HEARTBEAT_MS=2500;window.JC_REFRESH_MS=3000;'

def now_of(mock, uid, app):
    r = mock.progress.get((uid, app)); return (r or {}).get('data', {}).get('now')
def iso(sec_ago): return time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime(time.time() - sec_ago))
def posts(mock): return sum(1 for m, p in mock.log if m == 'POST' and p.startswith('/rest/v1/progress'))

async def wait_where(mock, uid, app, text, t=8):
    end = time.time() + t
    while time.time() < end:
        n = now_of(mock, uid, app)
        if n and text in n['where']: return n
        await asyncio.sleep(.2)
    return now_of(mock, uid, app)

async def run(b):
    mock = MockSupabase(); errs, ext = [], []
    A = await cloud_ctx(b, mock); await A.add_init_script(FAST); p = await A.new_page(); watch(p, errs, ext)
    await p.goto(BASE + 'quest.html'); await p.wait_for_selector('#jcs-chip')
    # Signed out: navigation sends nothing
    await p.fill('#nm', 'Ana'); await p.click('#nmgo'); await p.click('.lvl[data-id="software"]'); await p.wait_for_timeout(3000)
    check(posts(mock) == 0 and not mock.log, 'signed out: moving around sends nothing')
    await p.click('#back')
    await signup(p, 'Ana', 'DL100', 'ana@school.org'); uid = mock.users['ana@school.org']['id']
    n = await wait_where(mock, uid, 'quest', 'Level Map'); check(n and n['where'] == 'Level Map' and n['app'] == 'quest', f'after sign in: now = Level Map ({n})')
    await p.click('.lvl[data-id="software"]')
    n = await wait_where(mock, uid, 'quest', 'Lesson 1'); check(n and n['where'].startswith('Level 3: Computer Software Architecture, Lesson 1 of'), f'quest lesson label ({n and n["where"]})')
    await p.click('#nx'); n = await wait_where(mock, uid, 'quest', 'Lesson 2'); check(n and 'Lesson 2 of' in n['where'], 'next lesson updates label')
    await p.click('.tabs button[data-t="quiz"]'); await p.click('#go')
    n = await wait_where(mock, uid, 'quest', 'Q1 of'); check(n and n['where'] == 'Computer Software Architecture Quiz, Q1 of 10', f'quest quiz label ({n and n["where"]})')
    await p.click('.tabs button[data-t="sims"]'); await p.click('#pane .lvl >> nth=0')
    n = await wait_where(mock, uid, 'quest', 'Sim:'); check(n and n['where'].startswith('Level 3: Computer Software Architecture, Sim: '), 'quest sim label')
    check('now' not in (await p.evaluate("JSON.parse(localStorage.getItem('ic3quest_v1'))")), '"now" is never stored on the device')
    # heartbeat while visible
    t0 = now_of(mock, uid, 'quest')['at']; u0 = mock.progress[(uid, 'quest')]['updated_at']; await p.wait_for_timeout(3600)
    n = now_of(mock, uid, 'quest'); check(n['at'] > t0 and 'Sim:' in n['where'], f'heartbeat refreshes "at" while visible ({t0} -> {n["at"]})')
    # pause when hidden
    await p.evaluate("Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'hidden'});document.dispatchEvent(new Event('visibilitychange'))")
    await p.wait_for_timeout(1800); c0 = posts(mock); await p.wait_for_timeout(6000)
    check(posts(mock) == c0, f'heartbeat pauses while the tab is hidden ({c0} -> {posts(mock)})')
    await p.evaluate("Object.defineProperty(document,'visibilityState',{configurable:true,get:()=>'visible'});document.dispatchEvent(new Event('visibilitychange'))")
    await p.wait_for_timeout(2200); check(posts(mock) > c0, 'heartbeat resumes right away when visible again')
    # Practice labels
    await p.goto(BASE + 'practice.html'); await p.wait_for_selector('#jcs-chip')
    n = await wait_where(mock, uid, 'practice', 'Home'); check(n and n['where'] == 'Home', 'practice: Home label')
    await p.click('#nav button[data-v="library"]'); n = await wait_where(mock, uid, 'practice', 'Test library'); check(n and n['where'] == 'Test library', 'practice: Test library label')
    await p.click('[data-t="o16_pe2"][data-m="test"]')
    n = await wait_where(mock, uid, 'practice', 'Q1 of'); check(n and n['where'] == 'Practice Exam 2 (Office 2016), Q1 of 50 (Testing Mode)', f'practice exam label ({n and n["where"]})')
    await p.evaluate("__lab.run().i=16;__lab.go('run')"); n = await wait_where(mock, uid, 'practice', 'Q17'); check(n and 'Q17 of 50 (Testing Mode)' in n['where'], 'practice: question number updates (Q17)')
    await p.evaluate("__lab.finish()"); n = await wait_where(mock, uid, 'practice', 'score report'); check(n and n['where'].startswith('Practice Exam 2 (Office 2016): score report'), 'practice: score report label')
    await p.click('#nav button[data-v="library"]'); await p.click('[data-t="tt_sec"][data-m="train"]')
    n = await wait_where(mock, uid, 'practice', 'Topic test'); check(n and n['where'].startswith('Topic test: Security, Q1 of') and 'Training Mode' in n['where'], f'topic test label ({n and n["where"]})')
    await p.evaluate("__lab.finish()")
    await p.click('#nav button[data-v="final"]'); await p.click('#fx')
    n = await wait_where(mock, uid, 'practice', 'Final Exam Review, Q1'); check(n and n['where'] == 'Final Exam Review, Q1 of 45 (Testing Mode)', f'final label ({n and n["where"]})')
    await p.evaluate("__lab.run().i=11;__lab.go('run')"); n = await wait_where(mock, uid, 'practice', 'Q12'); check(n and n['where'] == 'Final Exam Review, Q12 of 45 (Testing Mode)', 'final: Q12 of 45')
    check('now' not in (await p.evaluate("JSON.parse(localStorage.getItem('ic3lab_v1'))")), 'practice: "now" not stored on the device')

    # More students with different ages
    others = [('Ben', 'ben@s.org', 300), ('Cy', 'cy@s.org', 3 * 3600), ('Di', 'di@s.org', 2 * 86400), ('Ed', 'ed@s.org', None)]
    for nm, em, _ in others:
        cx = await cloud_ctx(b, mock); pg = await cx.new_page(); watch(pg, errs, ext)
        await pg.goto(BASE + ('quest.html' if nm != 'Ed' else '')); await pg.wait_for_selector('#jcs-chip'); await signup(pg, nm, 'DL100', em)
        await pg.wait_for_timeout(2200); await cx.close()
    for nm, em, ago in others:
        u = mock.users[em]['id']
        if ago is None: continue
        r = mock.progress[(u, 'quest')]; r['updated_at'] = iso(ago); r['data']['now'] = {'app': 'quest', 'where': 'Level Map', 'at': iso(ago)}
    # teacher
    T = await cloud_ctx(b, mock); await T.add_init_script(FAST); t = await T.new_page(); watch(t, errs, ext)
    await t.goto(BASE); await t.wait_for_selector('#jcs-chip'); await signup(t, 'Jmal', 'DL100', 'jmal@school.org'); mock.promote('jmal@school.org')
    await t.goto(BASE + 'teacher.html'); await t.wait_for_selector('#tb')
    names = await t.locator('#tb tbody tr[data-id] td:first-child b').all_inner_texts()
    check(names == ['Ana', 'Ben', 'Cy', 'Di', 'Ed'], f'default sort: active first, then most recent ({names})')
    st = await t.locator('#tb tbody tr[data-id] td:nth-child(2)').all_inner_texts()
    check(st == ['Active now', 'Last seen 5 min ago', 'Last seen 3 hours ago', 'Last seen 2 days ago', 'Not active yet'], f'status thresholds ({st})')
    on = await t.locator('#tb tbody tr[data-id] td:nth-child(3)').all_inner_texts()
    check(on[0] == 'Practice Lab: Final Exam Review, Q12 of 45 (Testing Mode)', f'currently on = latest of both apps ({on[0]})')
    check(on[1] == 'Quest: Level Map' and on[4] == '–', 'currently on shows app name, dash when unknown')
    check('1' == (await t.locator('.stat.now b').inner_text()), '"active right now" count')
    check('Updated just now' in await t.inner_text('#upd'), '"Updated just now" note')
    rn = await t.inner_text('#rightnow'); check('Ana' in rn and 'Final Exam Review, Q12 of 45' in rn and 'Ben' not in rn, 'Right now card lists active students and where they are')
    await t.screenshot(path=SHOTS + 'now_teacher.png', full_page=True)
    # 2-minute threshold edges
    ben = mock.users['ben@s.org']['id']; mock.progress[(ben, 'quest')]['updated_at'] = iso(110)
    await t.click('#rf'); await t.wait_for_timeout(800)
    check((await t.locator('#tb tbody tr[data-id]:has-text("Ben") td:nth-child(2)').inner_text()) == 'Active now', '110 seconds ago counts as active')
    mock.progress[(ben, 'quest')]['updated_at'] = iso(130)
    await t.click('#rf'); await t.wait_for_timeout(800)
    check((await t.locator('#tb tbody tr[data-id]:has-text("Ben") td:nth-child(2)').inner_text()) == 'Last seen 2 min ago', '130 seconds ago is "Last seen 2 min ago"')
    # auto refresh (no click)
    cy = mock.users['cy@s.org']['id']; mock.progress[(cy, 'quest')]['updated_at'] = iso(0); mock.progress[(cy, 'quest')]['data']['now'] = {'app': 'quest', 'where': 'Boss Level', 'at': iso(0)}
    g0 = sum(1 for m, pth in mock.log if m == 'GET' and pth.startswith('/rest/v1/progress'))
    await t.wait_for_function("document.querySelector('#tb tbody tr[data-id]:nth-child(2) td:nth-child(3)') && [...document.querySelectorAll('#tb tbody tr[data-id]')].some(r=>r.textContent.includes('Cy')&&r.textContent.includes('Boss Level')&&r.textContent.includes('Active now'))", timeout=8000)
    g1 = sum(1 for m, pth in mock.log if m == 'GET' and pth.startswith('/rest/v1/progress'))
    check(g1 > g0, f'auto-refresh reloads the table without a click ({g0} -> {g1} loads)')
    names = await t.locator('#tb tbody tr[data-id] td:first-child b').all_inner_texts()
    check(names[:2] == ['Ana', 'Cy'] or names[:2] == ['Cy', 'Ana'], f'newly active student moves to the top ({names})')
    # expanded row survives refresh
    await t.click('#tb tbody tr[data-id]:has-text("Ana")'); await t.wait_for_timeout(3600)
    check(await t.locator('tr.det').count() == 1, 'opened student details stay open through auto-refresh')
    # refresh failure keeps the table
    mock.down = True
    try: await t.wait_for_function("document.querySelector('#upd').textContent.indexOf('refresh')>=0", timeout=20000)
    except Exception: pass
    check(await t.locator('#tb').count() == 1 and "Couldn't refresh" in await t.inner_text('#upd'), 'refresh failure keeps the table and shows a note')
    mock.down = False; await t.click('#rf'); await t.wait_for_timeout(800)
    check('Updated just now' in await t.inner_text('#upd'), 'manual Refresh recovers')
    # CSV
    async with t.expect_download() as dl: await t.click('#csv')
    csv = open(await (await dl.value).path(), encoding='utf-8-sig', newline='').read().split('\r\n')
    check(csv[0].startswith('"Student","Status","Currently on","Last seen","Last active"'), 'CSV has Status, Currently on, Last seen columns')
    row = [l for l in csv if l.startswith('"Ana"')][0]
    check('"Active now","Practice Lab: Final Exam Review, Q12 of 45 (Testing Mode)"' in row, 'CSV row includes status and location')
    # phone
    m = await T.new_page(); await m.set_viewport_size({'width': 390, 'height': 800}); watch(m, errs, ext)
    await m.goto(BASE + 'teacher.html'); await m.wait_for_selector('#tb')
    sw = await m.evaluate('document.documentElement.scrollWidth'); check(sw <= 390, f'teacher page fits a 390px phone (scrollWidth {sw}; table scrolls inside its box)')
    await m.screenshot(path=SHOTS + 'now_teacher_mobile.png', full_page=True)
    for pg in ['quest.html', 'practice.html']:
        await m.goto(BASE + pg); await m.wait_for_selector('#jcs-chip'); await m.wait_for_timeout(600)
        sw = await m.evaluate('document.documentElement.scrollWidth'); check(sw <= 390, f'{pg} at 390px (scrollWidth {sw})')
    bad = [x for x in errs if 'status of 4' not in x and 'status of 503' not in x]
    check(not bad, 'no console/page errors (desktop + 390px) ' + str(bad[:3]))
    stray = [u for u in ext if not (u.startswith(bt.MOCK) or u.startswith('https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/'))]
    check(not stray, 'no other hosts contacted ' + str(stray[:3]))

async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try: socket.create_connection(('127.0.0.1', PORT), .2).close(); break
        except OSError: time.sleep(.1)
    try:
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome'); await run(b); await b.close()
    finally: srv.terminate()
    f = [m for ok, m in results if not ok]; print(f'\n{len(results) - len(f)}/{len(results)} checks passed'); sys.exit(1 if f else 0)
asyncio.run(main())
