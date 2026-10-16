"""Student home (portal) tests: header greeting + next class, overall progress, 7 chapter cards with
Read / Play / Quiz, checklists and Chapter complete badge, Final Exam Review readiness (80% twice),
Class Tools, Calendar, collapsed Extra practice, Continue button, Mark as read on the reader page
(local + cloud sync), teacher dashboard 'Summary read', mobile 375px, and no em dashes.
Run: python3 tests/portal_test.py"""
import asyncio, os, sys, re, json, subprocess, socket, time
sys.path.insert(0, os.path.dirname(__file__))
from browser_test import cloud_ctx, signup, watch, check, results, BASE, SITE, PORT, SHOTS
from mock_supabase import MockSupabase
from playwright.async_api import async_playwright
EMPTY = 'window.JC_CONFIG={SUPABASE_URL:"",SUPABASE_ANON_KEY:""};'
def seed(quest, lab, now=None):
    s = f"if(!sessionStorage.seeded){{sessionStorage.seeded=1;localStorage.setItem('ic3quest_v1',{json.dumps(json.dumps(quest))});localStorage.setItem('ic3lab_v1',{json.dumps(json.dumps(lab))})}}"
    return s + (f"window.JC_NOW={json.dumps(now)};" if now else '')

async def dev(b, **kw):
    c = await b.new_context(service_workers='block', **kw)
    await c.route('**/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=EMPTY))
    return c

async def part_a(b):
    print('--- Portal: device-only mode')
    errs, ext = [], []
    c = await dev(b, viewport={'width': 1280, 'height': 900}); await c.add_init_script("window.JC_NOW='2026-10-15T22:00:00Z'")
    p = await c.new_page(); watch(p, errs, ext)
    await p.goto(BASE); await p.wait_for_load_state('networkidle')
    check(await p.title() == "Jmal C's Digital Literacy Class" and "Jmal C's Digital Literacy Class" in await p.inner_text('header'), 'home: Jmal C branding')
    check(await p.inner_text('#hi') == 'Welcome!', 'home: plain welcome when nobody is signed in')
    nx = await p.inner_text('#nextc')
    check('Monday, October 19, 6:00 to 9:00 PM ET' in nx and 'In person' in nx, f'home: next class is Mon Oct 19, in person ({nx!r})')
    cards = p.locator('main .card.ch'); check(await cards.count() == 7, 'home: 7 chapter cards')
    ids = await cards.evaluate_all('e=>e.map(x=>x.id)'); check(ids == [f'ch{n}' for n in range(1, 8)], 'home: chapter cards in order 1-7')
    for n in range(1, 8):
        bs = p.locator(f'#ch{n} .btns a'); hr = [await a.get_attribute('href') for a in await bs.all()]; lb = [(await a.inner_text()).split('\n') for a in await bs.all()]
        check(hr == [f'chapters.html#ch={n}', f'quest.html#ch={n}', f'practice.html#chapter={n}'] and [x[1] if len(x) > 1 else x[0] for x in lb][:3] and all(any(w in ' '.join(x) for x in lb) for w in ('Read', 'Play', 'Quiz')),
              f'chapter {n}: Read / Play / Quiz buttons')
        t = await p.inner_text(f'#ch{n} ul.chk')
        check('Summary: not read yet' in t and 'Quest lessons done: 0 of' in t and 'none yet' in t and not await p.locator(f'#ch{n} .badge').is_visible(), f'chapter {n}: empty checklist, no badge yet')
    check(await p.inner_text('#ovpct') == '0% done', 'home: progress bar at 0%')
    cont = p.locator('a.cont'); check(await cont.count() == 2 and (await cont.first.inner_text()).startswith('▶ Start here') and await cont.first.get_attribute('href') == 'chapters.html#ch=1', 'home: Start here goes to the Chapter 1 summary')
    # Final Exam Review, tools, calendar, extra practice
    f = p.locator('#final'); ft = await f.inner_text()
    check('80% or more on the Final Exam Review 2 times' in ft and '0 of 2' in ft and await f.locator('a[href="practice.html#final"]').count() == 1 and await f.locator('a[href*="gmetrix.net"]').count() == 1, 'final: readiness goal, Final Exam Review and GMetrix buttons')
    for host, nm in [('texidium.com', 'Texidium (optional)'), ('quizlet.com', 'Quizlet'), ('kahoot.it', 'Kahoot'), ('typingclub.com', 'Typing Club'), ('liveworksheets.com', 'Liveworksheets')]:
        a = p.locator(f'#resources ul.tools a[href*="{host}"]'); check(await a.count() == 1 and nm in await a.inner_text(), f'tools: {nm}')
    check(await p.locator('#resources a[href="resources/Class_Calendar.pdf"]').count() == 1, 'calendar link')
    ex = p.locator('details#extra'); check(await ex.count() == 1 and await ex.get_attribute('open') is None and not await ex.locator('ol').is_visible(), 'extra practice: collapsed')
    check(await ex.locator('a[href^="resources/workbooks/"]').count() == 10, 'extra practice: 10 LearnKey workbooks')
    await ex.locator('summary').click(); check(await ex.locator('ol').is_visible(), 'extra practice: opens on tap')
    check(await p.locator('a[href="quest.html"]').count() >= 1 and await p.locator('a[href="practice.html"]').count() >= 1, 'home: full Quest map and Practice Lab still reachable')
    check(chr(0x2014) not in await p.content(), 'home: no em dashes')
    await p.screenshot(path='/workspace/portal_shots/home_desktop_local.png', full_page=True)
    await c.close()
    # Next-class states
    for now, want in [('2026-10-26T23:30:00Z', ('Class is on now', 'Online')), ('2026-10-26T15:00:00Z', ('Today, 6:00 to 9:00 PM ET', 'Online')),
                      ('2026-10-22T02:30:00Z', ('Monday, October 26', 'Online')), ('2026-11-26T15:00:00Z', ('classes are finished', ''))]:
        c = await dev(b); await c.add_init_script(f"window.JC_NOW={json.dumps(now)}"); q = await c.new_page(); await q.goto(BASE)
        t = await q.inner_text('#nextc'); check(all(w in t for w in want), f'next class at {now}: {t.splitlines()[0]!r}'); await c.close()
    # Seeded progress: Ch 1 complete, Ch 2 read + some lessons, final 80%+ twice
    c = await dev(b, viewport={'width': 1280, 'height': 900}); p = await c.new_page(); watch(p, errs, ext)
    await p.goto(BASE); L = await p.evaluate('JC_HOME.chapters.map(c=>c.lessons)')
    seen = {}
    for lv, i in L[0]: seen.setdefault(lv, []).append(i)
    lv2, i2 = L[1][0]; seen.setdefault(lv2, []); seen[lv2] = sorted(set(seen[lv2] + [i2]))
    hist = [dict(date='2026-10-20T01:00:00Z', test='final', mode='test', pct=82, c=37, n=45, name='Final'), dict(date='2026-10-21T01:00:00Z', test='final', mode='test', pct=75, c=34, n=45, name='Final')]
    await c.add_init_script(seed(dict(name='Ana', sread=[1, 2], seen=seen), dict(best={'ch1:test': 85, 'ch2:train': 70}, history=hist)))
    await p.goto(BASE); await p.wait_for_load_state('networkidle')
    check(await p.inner_text('#hi') == 'Welcome, Ana!', 'home: name from saved progress')
    t1 = await p.inner_text('#ch1 ul.chk'); check('Summary read' in t1 and f'{len(L[0])} of {len(L[0])}' in t1 and '85%' in t1, 'chapter 1 checklist: read, all lessons, 85%')
    check(await p.locator('#ch1 .badge').is_visible() and '✓ Chapter complete' in await p.inner_text('#ch1 .badge'), 'chapter 1: ✓ Chapter complete badge at 80%+')
    t2 = await p.inner_text('#ch2 ul.chk'); check('Practice mode' in t2 and not await p.locator('#ch2 .badge').is_visible(), 'chapter 2: Practice-mode score shown, not complete')
    cont = await p.locator('a.cont').first.inner_text(); href = await p.locator('a.cont').first.get_attribute('href')
    check(cont.startswith('▶ Continue where you left off') and href == 'quest.html#ch=2', f'continue: goes to the first unfinished step (Ch 2 Play) ({href})')
    check(await p.inner_text('#ovch') == '1 of 7 chapters complete' and int((await p.inner_text('#ovpct')).split('%')[0]) > 14, 'progress bar reflects progress')
    check('1 of 2' in await p.inner_text('#rtxt') and await p.locator('#final .dots i.y').count() == 1, 'final readiness: 1 of 2 at 80%+')
    # Mark as read on the reader page
    await p.goto(BASE + 'chapters.html#ch=3'); await p.wait_for_selector('#ch3.show')
    mb = p.locator('#ch3 button.mark'); check(await mb.inner_text() == '✓ Mark as read', 'reader: Mark as read button')
    await mb.click(); check(await mb.inner_text() == '✅ Read' and await p.evaluate("JSON.parse(localStorage.ic3quest_v1).sread") == [1, 2, 3], 'reader: marking saves to the Quest progress (sread)')
    st = await p.evaluate("JSON.parse(localStorage.ic3quest_v1)"); check(st.get('name') == 'Ana' and st.get('seen'), 'reader: marking keeps the rest of the Quest progress')
    await p.click('#home'); await p.wait_for_selector('#ch3'); check('Summary read' in await p.inner_text('#ch3 ul.chk'), 'home: Chapter 3 now shows Summary read')
    await p.goto(BASE + 'quest.html#ch=3'); await p.wait_for_selector('#ch3'); check('✅' in await p.inner_text('#ch3 a.chsum'), 'quest: chapter view shows the summary as read')
    await p.goto(BASE + 'practice.html#final'); await p.wait_for_timeout(300); check('Final Exam Review' in await p.inner_text('#app h1'), 'practice.html#final opens the Final Exam Review')
    await c.close()
    # Mobile 375px
    m = await dev(b, viewport={'width': 375, 'height': 812}, is_mobile=True, has_touch=True); q = await m.new_page(); watch(q, errs, ext); await q.goto(BASE); await q.wait_for_load_state('networkidle')
    ov = await q.evaluate('document.documentElement.scrollWidth-innerWidth'); check(ov <= 0, f'mobile 375: no sideways scroll ({ov}px)')
    small = await q.evaluate("[...document.querySelectorAll('.btns a, a.cont, a.btn, ul.tools a, details.x summary')].filter(a=>{const r=a.getBoundingClientRect();return r.height<44||r.width<44}).length")
    check(small == 0, f'mobile 375: every main button is at least 44px ({small} too small)')
    w = await q.evaluate("document.querySelector('#ch1 .btns a').getBoundingClientRect().width"); check(w >= 90, f'mobile 375: Read/Play/Quiz side by side, {int(w)}px wide each')
    await q.screenshot(path='/workspace/portal_shots/home_mobile_local.png', full_page=True); await m.close()
    check(not [x for x in errs if 'pageerror' in x], 'no page errors (device mode) ' + str([x for x in errs if 'pageerror' in x][:2]))

async def part_b(b):
    print('--- Portal: cloud mode (mock Supabase)')
    mock = MockSupabase(); errs, ext = [], []
    A = await cloud_ctx(b, mock); p = await A.new_page(); watch(p, errs, ext)
    await p.goto(BASE); await p.wait_for_selector('#jcs-chip'); check(await p.locator('#cloud-note').is_visible(), 'home: cloud sign-in note shown')
    await signup(p, 'Ana Lopez', 'DL100', 'ana@s.org'); await p.wait_for_function("document.getElementById('hi').textContent==='Welcome, Ana!'")
    check(True, 'home: signed-in student name in the welcome header')
    await p.goto(BASE + 'chapters.html#ch=4'); await p.wait_for_selector('#jcs-chip'); await p.wait_for_function("document.querySelector('#jcs-chip').textContent.indexOf('Ana')>=0")
    await p.click('#ch4 button.mark'); await p.wait_for_timeout(2500)
    uid = mock.users['ana@s.org']['id']; d = (mock.progress.get((uid, 'quest')) or {}).get('data') or {}
    check(d.get('sread') == [4], f'cloud: summary read synced in the Quest progress ({d.get("sread")})')
    # New device: progress comes back
    B = await cloud_ctx(b, mock); q = await B.new_page(); watch(q, errs, ext); await q.goto(BASE); await q.wait_for_selector('#jcs-chip')
    await q.click('#jcs-chip'); await q.fill('#jcs-email', 'ana@s.org'); await q.fill('#jcs-pw', 'secret123'); await q.click('#jcs-go')
    await q.wait_for_function("document.querySelector('#ch4 ul.chk li').className==='y'", timeout=8000); check(True, 'cloud: another device shows Chapter 4 summary read after sign in')
    # Teacher dashboard
    T = await cloud_ctx(b, mock); t = await T.new_page(); watch(t, errs, ext)
    await t.goto(BASE); await t.wait_for_selector('#jcs-chip'); await signup(t, 'Jmal', 'DL100', 'jmal@s.org'); mock.promote('jmal@s.org')
    await t.goto(BASE + 'teacher.html'); await t.wait_for_selector('#tb')
    th, tb = await t.inner_text('#tb thead'), await t.inner_text('#tb tbody')
    check('summaries read' in th.lower() and '1 / 7' in tb, f'teacher: Summaries read column (1 / 7) {th!r} {tb!r}')
    cls = await t.inner_text('#chcls'); check('Summary read' in cls and re.search(r'Ch 4: File Management\s+100%', cls), 'teacher: class chapter card shows Summary read share')
    await t.click('#tb tbody tr[data-id]'); det = await t.inner_text('tr.det')
    check(re.search(r'Ch 4: File Management\s+✅ Yes', det) and re.search(r'Ch 1: Operating Systems\s+Not yet', det), 'teacher: student chapter table shows Summary read per chapter')
    await t.screenshot(path=SHOTS + 'portal_teacher.png', full_page=True)
    check(not [x for x in errs if 'pageerror' in x], 'no page errors (cloud) ' + str([x for x in errs if 'pageerror' in x][:2]))

async def main():
    os.makedirs('/workspace/portal_shots', exist_ok=True)
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try: socket.create_connection(('127.0.0.1', PORT), .2).close(); break
        except OSError: time.sleep(.1)
    try:
        sw = open(os.path.join(SITE, 'sw.js')).read(); check(re.search(r"ic3-apps-v(1[3-9]|[2-9][0-9])", sw) is not None, "service worker cache bumped (v13 or later)")
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome'); await part_a(b); await part_b(b); await b.close()
    finally:
        srv.terminate()
    bad = [r for r in results if not r[0]]
    print(f'\n{len(results) - len(bad)}/{len(results)} passed'); sys.exit(1 if bad else 0)
asyncio.run(main())
