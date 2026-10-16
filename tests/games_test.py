"""Chapter Games + Activity Pack tests: original wording (9-word check vs the textbook), no em dashes,
every game playable by tapping on desktop and 375px mobile, points/stars/timer, best scores saved in the
Quest progress and synced, Games button + checklist on the home page, teacher dashboard games columns,
and Fun Activities links in the teacher Ch 1-7 Teaching Materials tab.
Run: python3 tests/games_test.py"""
import asyncio, os, sys, re, json, glob, subprocess, socket, time
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
from browser_test import cloud_ctx, signup, watch, check, results, BASE, SITE, PORT, SHOTS
from mock_supabase import MockSupabase
from playwright.async_api import async_playwright
from games import GAMES
from activities import A, CARDS
EMPTY = 'window.JC_CONFIG={SUPABASE_URL:"",SUPABASE_ANON_KEY:""};'
PACK = '/workspace/BCC_IC3_Class/Fun_Activities_Ch1-7'
W = lambda t: re.findall(r"[a-z0-9]+", t.lower().replace('\u2019', "'").replace("'", ''))
def grams(ws, k=9): return {' '.join(ws[i:i + k]) for i in range(len(ws) - k + 1)}

def static_checks():
    print('--- Games + Activity Pack: static checks')
    book = set().union(*(grams(W(open(f, encoding='utf-8', errors='ignore').read())) for f in glob.glob('/workspace/BCC_IC3_Class/ch1-7_text/*.txt')))
    pdf = subprocess.run(['pdftotext', PACK + '.pdf', '-'], capture_output=True, text=True).stdout
    import zipfile; dx = ' '.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', zipfile.ZipFile(PACK + '.docx').read('word/document.xml').decode('utf8')))
    gh = open(os.path.join(SITE, 'games.html'), encoding='utf-8').read()
    for name, t in [('games.py', open(os.path.join(SITE, 'tools/games.py'), encoding='utf-8').read()), ('activities.py', open(os.path.join(SITE, 'tools/activities.py'), encoding='utf-8').read()),
                    ('activity pack PDF', pdf), ('activity pack DOCX', dx), ('games.html', gh)]:
        hits = grams(W(t)) & book
        check(t.strip() and not hits, f'{name}: no 9-word stretch matches the textbook (hits {sorted(hits)[:2]})')
        check(chr(0x2014) not in t, f'{name}: no em dashes')
    check(all(3 <= len(A[n]) <= 4 for n in range(1, 8)), f'pack: 3-4 activities per chapter {[len(A[n]) for n in range(1, 8)]}')
    need = ('obj', 'min', 'mat', 'inp', 'zoom', 'steps', 'key', 'esl')
    check(all(all(a.get(k) for k in need) and 10 <= a['min'] <= 25 for n in A for a in A[n]), 'pack: every activity has objective, 10-25 min, materials, in-person, Zoom, steps, debrief/key, ESL tip')
    kinds = ' '.join(a['kind'].lower() for n in A for a in A[n])
    check(all(k in kinds for k in ('game', 'team', 'role-play', 'scavenger', 'mini-project')), 'pack: mix of games, team challenges, role-plays, scavenger hunt, mini-projects')
    titles = [a['t'] for n in A for a in A[n]]
    check(all(any(x in t for t in titles) for x in ('Port Detective', 'Scam or Legit', 'Build-a-PC', 'Wi-Fi Password', 'File Explorer Race', 'Cloud Relay')), 'pack: includes the requested example activities')
    pages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', PACK + '.pdf'], capture_output=True, text=True).stdout).group(1))
    check(pages >= 20 and all(f'Chapter {n}:' in pdf for n in range(1, 8)) and pdf.count('Printable ·') >= 15 and "Jmal C's Digital Literacy Class" in pdf, f'pack PDF: {pages} pages, 7 chapters, printable card pages, branded')
    check(all(1 <= sum(g['ch'] == n for g in GAMES) <= 2 for n in range(1, 8)) and len({g['type'] for g in GAMES}) >= 5, 'games: 1-2 per chapter, 5 game types')
    sw = open(os.path.join(SITE, 'sw.js')).read(); check(re.search(r"ic3-apps-v(1[4-9]|[2-9][0-9])", sw) and "'./games.html'" in sw, 'service worker v14 caches games.html')
    return pages

PLAY = """async (opts)=>{const g=window.__games.data.games.find(x=>x.id===opts.id);const sleep=ms=>new Promise(r=>setTimeout(r,ms));
 const q=s=>document.querySelector(s),qa=s=>[...document.querySelectorAll(s)];let wrong=opts.wrong||0;
 if(g.type==='match'){const L=qa('#gm .tile[data-s=l]');for(const t of L){if(wrong>0){const bad=qa('#gm .tile[data-s=r]').find(x=>x.dataset.i!==t.dataset.i&&!x.disabled);t.click();bad.click();wrong--;await sleep(20)}
   t.click();q('#gm .tile[data-s=r][data-i="'+t.dataset.i+'"]').click();await sleep(20)}}
 else if(g.type==='order'){for(let i=0;i<g.steps.length;i++){if(wrong>0&&i<g.steps.length-1){q('#pl .tile:not([data-i="'+i+'"])').click();wrong--}q('#pl .tile[data-i="'+i+'"]').click();await sleep(20)}}
 else{for(let k=0;k<g.items.length;k++){const txt=q('#it').innerText;let a;
   if(g.type==='tf'){a=g.items.find(x=>x[0]===txt)[1]?0:1}else if(g.type==='scam'){a=g.items.find(x=>txt.indexOf(x[2])>=0)[3]?0:1}else{a=g.items.find(x=>x[0]===txt)[1]}
   let pick=a;if(wrong>0){pick=(a+1)%qa('#gm .cats button').length;wrong--}q('#gm .cats button[data-c="'+pick+'"]').click();await sleep(10);q('#nx').click();await sleep(10)}}
 for(let i=0;i<100&&window.__games.view!=='result';i++)await sleep(50);return window.__games.last}"""

async def dev(b, **kw):
    c = await b.new_context(service_workers='block', **kw)
    await c.route('**/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=EMPTY))
    return c

async def part_a(b):
    print('--- Games: device-only mode')
    errs, ext = [], []
    c = await dev(b, viewport={'width': 1280, 'height': 900}); p = await c.new_page(); watch(p, errs, ext)
    await p.goto(BASE); await p.wait_for_load_state('networkidle')
    for n in range(1, 8):
        a = p.locator(f'#ch{n} a.games'); ng = sum(g['ch'] == n for g in GAMES)
        check(await a.count() == 1 and await a.get_attribute('href') == f'games.html#ch={n}' and f'{ng} quick games' in await a.inner_text(), f'home: chapter {n} card has a Games button')
        check(f'Games played: 0 of {ng}' in await p.inner_text(f'#ch{n} ul.chk'), f'home: chapter {n} checklist shows games played')
    await p.click('#ch7 a.games'); await p.wait_for_selector('#gc_c7_scam')
    check(await p.locator('.gi').count() == 2 and 'Not played yet' in await p.inner_text('#app'), 'games: Chapter 7 list shows 2 games, not played yet')
    for g in GAMES:
        await p.goto(BASE + f'games.html#g={g["id"]}'); await p.wait_for_selector('#gm')
        check(re.match(r'⏱ \d+s', await p.inner_text('#tm')) is not None and '⭐ 0' in await p.inner_text('#pt'), f'{g["id"]}: HUD shows timer and points')
        r = await p.evaluate(PLAY, {'id': g['id']})
        check(r and r['acc'] == 100 and r['stars'] == 3 and r['pts'] >= 50, f'{g["id"]} ({g["type"]}): perfect run = 100%, 3 stars, {r and r["pts"]} points')
    st = await p.evaluate("JSON.parse(localStorage.ic3quest_v1)")
    check(all(st['cgn'].get(g['id']) == 1 and st['cgs'][g['id']] == 3 and st['cg'][g['id']] == 100 for g in GAMES), 'saved: best %, stars, points, plays for all 14 games in the Quest progress')
    # A run with mistakes scores lower but keeps the best
    await p.goto(BASE + 'games.html#g=c1_sort'); await p.wait_for_selector('#gm'); r = await p.evaluate(PLAY, {'id': 'c1_sort', 'wrong': 4})
    check(r['acc'] == 60 and r['stars'] == 1, f'mistakes lower the score and stars ({r})')
    st = await p.evaluate("JSON.parse(localStorage.ic3quest_v1)"); check(st['cg']['c1_sort'] == 100 and st['cgn']['c1_sort'] == 2, 'best score kept; play count goes up')
    check('Play again' in await p.inner_text('#res') and await p.locator('#res a[href="#g=c2_sort"], #res a[href^="#g=c1_"]').count() >= 1, 'result screen: Play again and next game')
    await p.goto(BASE + 'games.html#g=c3_match'); await p.wait_for_selector('#gm')
    await p.locator('#gm .tile[data-s=l]').first.click(); i = await p.locator('#gm .tile[data-s=l]').first.get_attribute('data-i')
    await p.locator(f'#gm .tile[data-s=r]:not([data-i="{i}"])').first.click()
    check('Not a match' in await p.inner_text('#fb'), 'match: wrong pair gives feedback')
    await p.goto(BASE); await p.wait_for_selector('#ch1')
    t = await p.inner_text('#ch1 ul.chk'); check('Games played: 2 of 2' in t and '⭐⭐⭐' in t, 'home: checklist shows games played and best stars')
    await p.goto(BASE + 'games.html#ch=1'); await p.wait_for_selector('#gc_c1_match'); check('⭐⭐⭐' in await p.inner_text('#gc_c1_match') and 'played 1x' in await p.inner_text('#gc_c1_match'), 'games list shows best stars and plays')
    await c.close()
    # Mobile 375: tap-only play + screenshot
    m = await dev(b, viewport={'width': 375, 'height': 812}, is_mobile=True, has_touch=True, device_scale_factor=2); q = await m.new_page(); watch(q, errs, ext)
    await q.goto(BASE + 'games.html#g=c7_scam'); await q.wait_for_selector('#it')
    ov = await q.evaluate('document.documentElement.scrollWidth-innerWidth'); check(ov <= 0, f'mobile 375: no sideways scroll in a game ({ov}px)')
    small = await q.evaluate("[...document.querySelectorAll('#gm button, .hud a')].filter(b=>b.getBoundingClientRect().height<40).length"); check(small == 0, 'mobile 375: tap targets are big')
    g = next(x for x in GAMES if x['id'] == 'c7_scam'); txt = await q.inner_text('#it'); ans = next(x for x in g['items'] if x[2] in txt)
    await q.locator(f'#gm .cats button[data-c="{0 if ans[3] else 1}"]').tap(); await q.wait_for_selector('#nx')
    check('Correct' in await q.inner_text('#fbw'), 'mobile: tapping the right answer gives feedback')
    await q.screenshot(path='/workspace/portal_shots/game_mobile_local.png')
    await q.goto(BASE + 'games.html#g=c4_order'); await q.wait_for_selector('#pl')
    for i in range(6): await q.locator(f'#pl .tile[data-i="{i}"]').tap()
    await q.wait_for_selector('#res', timeout=5000); check(True, 'mobile: order game finished with taps only')
    for gid in ('c6_match',):
        await q.goto(BASE + f'games.html#g={gid}'); await q.wait_for_selector('#gm .tile')
        ls = q.locator('#gm .tile[data-s=l]')
        for k in range(await ls.count()):
            t = ls.nth(k); i = await t.get_attribute('data-i'); await t.tap(); await q.locator(f'#gm .tile[data-s=r][data-i="{i}"]').tap()
        await q.wait_for_selector('#res', timeout=5000); check(True, 'mobile: match game finished with taps only (no dragging)')
    await m.close()
    check(not [x for x in errs if 'pageerror' in x], 'no page errors (games device mode) ' + str([x for x in errs if 'pageerror' in x][:2]))

async def part_b(b):
    print('--- Games: cloud sync + teacher dashboard')
    mock = MockSupabase(); errs, ext = [], []
    A_ = await cloud_ctx(b, mock); p = await A_.new_page(); watch(p, errs, ext)
    await p.goto(BASE + 'games.html#ch=2'); await p.wait_for_selector('#jcs-chip'); await signup(p, 'Ana', 'DL100', 'ana@s.org')
    await p.wait_for_function("document.querySelector('#jcs-chip').textContent.indexOf('Ana')>=0")
    await p.goto(BASE + 'games.html#g=c2_order'); await p.wait_for_selector('#gm'); await p.evaluate(PLAY, {'id': 'c2_order'}); await p.wait_for_timeout(2500)
    uid = mock.users['ana@s.org']['id']; d = (mock.progress.get((uid, 'quest')) or {}).get('data') or {}
    check(d.get('cgn', {}).get('c2_order') == 1 and d.get('cg', {}).get('c2_order') == 100 and d.get('cgs', {}).get('c2_order') == 3, f'cloud: game best score synced ({ {k: d.get(k) for k in ("cg", "cgs", "cgn")} })')
    T = await cloud_ctx(b, mock); t = await T.new_page(); watch(t, errs, ext)
    await t.goto(BASE); await t.wait_for_selector('#jcs-chip'); await signup(t, 'Jmal', 'DL100', 'jmal@s.org'); mock.promote('jmal@s.org')
    await t.goto(BASE + 'teacher.html'); await t.wait_for_selector('#tb')
    th, tb = (await t.inner_text('#tb thead')).lower(), await t.inner_text('#tb tbody')
    check('games played' in th and '1 / 14' in tb, 'teacher: Games played column (1 / 14)')
    cls = await t.inner_text('#chcls'); check('Games played' in cls and re.search(r'Ch 2: Hardware\s+\S+.*?\s+50%\s+played\s+·\s+100%', cls), 'teacher: class chapter card shows games played and avg best')
    await t.click('#tb tbody tr[data-id]'); det = await t.inner_text('tr.det')
    check('Chapter games (best scores)' in det and re.search(r'Ch 2: Bytes Line-Up\s+100%\s+⭐⭐⭐\s+\d+\s+1', det), 'teacher: student detail lists each game with best %, stars, points, plays')
    check(re.search(r'Ch 2: Hardware\s+Not yet\s+1/2 · 100%', det), 'teacher: per-chapter table shows games played and best')
    await t.screenshot(path=SHOTS + 'games_teacher.png', full_page=True)
    await t.click('#t3'); await t.wait_for_selector('#tm7')
    for n in range(1, 8):
        c = t.locator(f'#tm{n}'); txt = await c.inner_text()
        hrefs = [await a.get_attribute('href') for a in await c.locator('a').all()]
        check('Fun Activities pack, Chapter %d' % n in txt and any('1q-mFXPIRjQp7YhU-YBjYd2oYg0ci5rja' in (h or '') for h in hrefs) and any('17gRJLFw6AXMm6IRQ3Z6UUnS7gSM3ae11' in (h or '') for h in hrefs),
              f'teacher materials: chapter {n} links the Fun Activities pack (PDF + Word on Drive)')
        check('Free App Versions guide' in txt and any('12Ctg0nHkBzfSazkvic22QuodKcIfaUF-' in (h or '') for h in hrefs) and f'Chapter {n} import files' in txt,
              f'teacher materials: chapter {n} links the Free App Versions guide and its import-files folder')
    check(not [x for x in errs if 'pageerror' in x], 'no page errors (games cloud) ' + str([x for x in errs if 'pageerror' in x][:2]))

async def main():
    os.makedirs('/workspace/portal_shots', exist_ok=True)
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try: socket.create_connection(('127.0.0.1', PORT), .2).close(); break
        except OSError: time.sleep(.1)
    try:
        static_checks()
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome'); await part_a(b); await part_b(b); await b.close()
    finally:
        srv.terminate()
    bad = [r for r in results if not r[0]]
    print(f'\n{len(results) - len(bad)}/{len(results)} passed'); sys.exit(1 if bad else 0)
asyncio.run(main())
