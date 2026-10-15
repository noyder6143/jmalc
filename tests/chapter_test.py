"""Chapters 1-7 tests: landing study path, Practice Lab Chapter Quiz mode, Quest chapter path,
teacher Ch 1-7 Teaching Materials tab, Answer Key chapter filter, and per-chapter dashboard progress.
Run: python3 tests/chapter_test.py   (mock Supabase + real supabase-js, same as the other tests)"""
import asyncio, os, sys, re, glob, json, zipfile, socket, subprocess, time
sys.path.insert(0, os.path.dirname(__file__))
from browser_test import cloud_ctx, signup, watch, check, results, BASE, SITE, PORT, SHOTS
from mock_supabase import MockSupabase
from playwright.async_api import async_playwright
EMPTY = 'window.JC_CONFIG={SUPABASE_URL:"",SUPABASE_ANON_KEY:""};'
# Correct response for any item type, so a whole chapter can be scored without clicking every widget.
RIGHT = """b=>{switch(b.type){case 'mc':case 'tf':case 'img':return b.ans;case 'multi':case 'yn':case 'dd':return b.ans.slice();
 case 'match':return b.left.map((_,i)=>i);case 'order':return b.steps.map((_,i)=>i);case 'sim':return {step:99,mistakes:0,done:true}}}"""

def secrets_from_accounts_doc():
    """Read the shared Texidium login from the private doc on the box (never printed) so we can prove it isn't on the site."""
    f = glob.glob('/workspace/BCC_IC3_Class/02_Student_Accounts_and_Tools/*.docx')
    if not f: return []
    x = zipfile.ZipFile(f[0]).read('word/document.xml').decode('utf8', 'ignore')
    t = ' '.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', x))
    out = re.findall(r'[\w.+-]+@gmail\.com', t)
    m = re.search(r'[Pp]assword\s*[:=]?\s*(\S+)', t)
    if m and len(m.group(1)) >= 4: out.append(m.group(1))
    return out

async def run_chapter(p, n, mode='test'):
    await p.evaluate(f"__lab.chStart({n},'{mode}','all')")
    info = await p.evaluate(f"""(()=>{{const R=__lab.run(),B=__lab.data.bank,right={RIGHT};
      R.items.forEach((x,k)=>{{R.resp[k]=right(B[x.id])}});
      return {{n:R.items.length,id:R.id,min:R.minutes,all:R.items.every(x=>(B[x.id].ch||[]).includes({n})),pool:__lab.chPool({n}).length}}}})()""")
    await p.evaluate('__lab.finish()'); await p.wait_for_selector('.score')
    return info, await p.locator('.score').inner_text()

async def part_a(b):
    print('--- Chapters: device-only mode')
    ctx = await b.new_context(viewport={'width': 1280, 'height': 900}, service_workers='block')
    await ctx.route('**/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=EMPTY))
    errs, ext = [], []; p = await ctx.new_page(); watch(p, errs, ext)
    # Landing page
    await p.goto(BASE); await p.wait_for_load_state('networkidle')
    chs = p.locator('#chapters .rbox.ch'); check(await chs.count() == 7, 'landing: 7 chapter boxes in the study path')
    for n in range(1, 8):
        box = p.locator(f'#ch{n}')
        check(await box.locator(f'a[href="quest.html#ch={n}"]').count() == 1 and await box.locator(f'a[href="practice.html#chapter={n}"]').count() == 1,
              f'landing: chapter {n} links its Quest lessons and Chapter Quiz')
    txt = await p.inner_text('body')
    check('Chapter 3: Networks and Mobile Devices' in txt and 'Chapter 7: Security and Maintenance' in txt, 'landing: chapter titles match the textbook')
    for host, name in [('quizlet.com', 'Quizlet'), ('liveworksheets.com', 'Liveworksheets'), ('typingclub.com', 'Typing Club'), ('texidium.com', 'Texidium'), ('kahoot.it', 'Kahoot')]:
        check(await p.locator(f'#resources a[href*="{host}"]').count() >= 1, f'landing: {name} link in Class Tools')
    check('Extra practice' in txt and await p.locator('#resources a[href^="resources/workbooks/"]').count() == 10, 'landing: 10 LearnKey workbooks kept, labeled Extra practice')
    check(await p.locator('#chapters a[href^="resources/workbooks/"]').count() >= 7, 'landing: each chapter links matching LearnKey workbooks')
    check('\u2014' not in await p.content(), 'landing: no em dashes')
    await p.screenshot(path=SHOTS + 'ch_landing.png', full_page=True)
    # Practice Lab Chapter Quiz
    await p.goto(BASE + 'practice.html'); await p.wait_for_load_state('networkidle')
    check(await p.locator('#nav button[data-v="chapter"]').count() == 1, 'practice: Chapter Quiz in the nav')
    await p.click('#nav button[data-v="chapter"]')
    check(await p.locator('[id^="chq"]').count() == 7, 'practice: 7 chapter cards')
    D = await p.evaluate("(()=>{const B=__lab.data.bank;const o={};for(let n=1;n<=7;n++)o[n]=__lab.chPool(n).length;return {pools:o,noch:Object.values(B).filter(b=>!(b.ch||[]).length).length,newi:Object.values(B).filter(b=>b.tt==='CH').map(b=>[b.id,b.ch,b.type])}})()")
    check(all(v >= 30 for v in D['pools'].values()), f'practice: every chapter has 30+ questions {D["pools"]}')
    check(D['noch'] == 0, 'practice: every Practice Lab item maps to at least one chapter')
    check(len(D['newi']) == 66 and all(int(i[0][2]) in i[1] for i in D['newi']), f'practice: {len(D["newi"])} new Ch 1-7 items, each in its own chapter')
    for n in range(1, 8):
        tag = await p.locator(f'#chq{n} .tag').inner_text()
        check(f'{D["pools"][str(n)]} questions' in tag.lower(), f'practice: chapter {n} card shows its pool size')
    # UI path: 10-question Testing quiz on chapter 3
    await p.select_option('#chn', '10'); await p.click('button[data-ch="3"][data-m="test"]'); await p.wait_for_selector('#qt')
    r = await p.evaluate("(()=>{const R=__lab.run();return {n:R.items.length,id:R.id,all:R.items.every(x=>__lab.data.bank[x.id].ch.includes(3)),name:R.name}})()")
    check(r['n'] == 10 and r['id'] == 'ch3' and r['all'] and r['name'] == 'Chapter 3 Quiz: Networks and Mobile Devices', f'practice: Chapter 3 quiz pulls 10 Chapter 3 items ({r})')
    check(await p.locator('#tm').inner_text() == '10:00', 'practice: Testing mode gives 1 minute per question')
    check('Ch 3' in await p.inner_text('.qhead + div'), 'practice: question shows its chapter tag')
    await p.screenshot(path=SHOTS + 'ch_quiz_q1.png', full_page=True)
    await p.evaluate("__lab.finish()"); await p.wait_for_selector('.score')
    check(await p.locator('#lib').inner_text() == 'Back to chapters', 'practice: results page goes back to chapters')
    await p.click('#lib'); check(await p.locator('#chq3').count() == 1, 'practice: back to the chapter picker')
    # Every chapter, all items, answered correctly
    for n in range(1, 8):
        info, sc = await run_chapter(p, n)
        check(info['all'] and info['n'] == info['pool'] and sc == '100%', f'practice: Chapter {n} full quiz {info["n"]} items scores {sc}')
    st = await p.evaluate("__lab.state()")
    check(all(st['best'].get(f'ch{n}:test') == 100 for n in range(1, 8)), 'practice: best Chapter Quiz scores saved per chapter')
    check([h['test'] for h in st['history']][-7:] == [f'ch{n}' for n in range(1, 8)], 'practice: chapter attempts land in history')
    # Training mode with feedback
    await p.evaluate("__lab.chStart(6,'train','10')"); await p.wait_for_selector('#qt')
    await p.evaluate(f"(()=>{{const R=__lab.run();R.resp[0]=({RIGHT})(__lab.data.bank[R.items[0].id])}})()"); await p.click('#ck')
    check('Correct' in await p.inner_text('#fb'), 'practice: Training mode shows feedback in a Chapter Quiz')
    await p.evaluate('__lab.finish()')
    # Deep link
    await p.goto(BASE + 'practice.html#chapter=5'); await p.wait_for_selector('#chq5')
    check('outline' in (await p.get_attribute('#chq5', 'style') or '') and await p.locator('#nav button.on').inner_text() == 'Chapter Quiz', 'practice: #chapter=5 deep link opens and highlights Chapter 5')
    await p.screenshot(path=SHOTS + 'ch_picker.png', full_page=True)
    # Final Exam pool still 45 / 50 min with the new items
    await p.goto(BASE + 'practice.html'); await p.click('#nav button[data-v="final"]'); await p.click('#fx')
    f = await p.evaluate("(()=>{const R=__lab.run();return [R.items.length,R.minutes]})()"); check(f == [45, 50], 'practice: Final Exam Review still 45 questions in 50 minutes')
    await p.evaluate('__lab.finish()')
    # Quest chapter path
    await p.goto(BASE + 'quest.html'); await p.wait_for_load_state('networkidle')
    await p.fill('#nm', 'Ana'); await p.click('#nmgo'); await p.click('#chp')
    check(await p.locator('[data-c]').count() == 7, 'quest: Chapters 1-7 view with 7 chapter tabs')
    check(await p.locator('a[href="practice.html#chapter=4"]').count() == 1, 'quest: each chapter links its Chapter Quiz')
    await p.goto(BASE + 'quest.html#ch=2'); await p.wait_for_selector('#ch2')
    btn = p.locator('#ch2 [data-lv]').first; lv, li, title = await btn.get_attribute('data-lv'), int(await btn.get_attribute('data-i')), (await btn.inner_text()).replace('✅ ', '')
    await p.screenshot(path=SHOTS + 'ch_quest.png', full_page=True)
    await btn.click(); await p.wait_for_selector('.lesson')
    check(title in await p.inner_text('.lesson h3'), f'quest: chapter lesson button opens that lesson ({title})')
    s = await p.evaluate('__quest.state()'); check(li in s['seen'].get(lv, []), 'quest: opening it counts as read')
    check(not errs, 'no console errors (chapters, device-only) ' + str(errs[:3]))
    await ctx.close()

async def part_b(b):
    print('--- Chapters: teacher portal (mock Supabase)')
    mock = MockSupabase(); errs, ext = [], []
    A = await cloud_ctx(b, mock); p = await A.new_page(); watch(p, errs, ext)
    await p.goto(BASE + 'practice.html'); await p.wait_for_selector('#jcs-chip'); await signup(p, 'Ana', 'DL100', 'ana@s.org')
    await p.wait_for_function("document.querySelector('#jcs-chip').textContent.indexOf('Ana')>=0")
    info, sc = await run_chapter(p, 2); await p.wait_for_timeout(2500)
    uid = mock.users['ana@s.org']['id']
    check(mock.progress[(uid, 'practice')]['best_scores'].get('ch2:test') == 100, 'chapter quiz best score synced to the cloud')
    check(any(a['test_id'] == 'ch2' for a in mock.attempts if a['user_id'] == uid), 'chapter quiz attempt saved to attempts')
    await p.goto(BASE + 'quest.html#ch=2'); await p.wait_for_selector('#ch2 [data-lv]'); await p.locator('#ch2 [data-lv]').first.click(); await p.wait_for_timeout(2500)
    T = await cloud_ctx(b, mock); t = await T.new_page(); watch(t, errs, ext)
    await t.goto(BASE); await t.wait_for_selector('#jcs-chip'); await signup(t, 'Jmal', 'DL100', 'jmal@s.org'); mock.promote('jmal@s.org')
    await t.goto(BASE + 'teacher.html'); await t.wait_for_selector('#tb')
    cls = await t.inner_text('#chcls'); check('Ch 2: Hardware' in cls and '100%' in cls, 'teacher: class progress by chapter card')
    await t.click('#tb tbody tr[data-id]'); det = await t.inner_text('tr.det')
    check('By textbook chapter' in det and re.search(r'Ch 2: Hardware\s+100%\s+100%', det), 'teacher: student detail shows Chapter 2 quiz and lab accuracy')
    check(re.search(r'Ch 2: Hardware.*\(1/\d+\)', det, re.S) is not None, 'teacher: Quest lessons read per chapter')
    await t.screenshot(path=SHOTS + 'ch_teacher_dash.png', full_page=True)
    # Teaching Materials tab
    await t.click('#t3'); await t.wait_for_selector('#tm7')
    tm = t.locator('#tmv'); check(await tm.locator('[id^="tm"]').count() == 7, 'teacher: Ch 1-7 Teaching Materials has 7 chapter cards')
    for n in range(1, 8):
        c = t.locator(f'#tm{n}'); ks = await c.locator('.k').all_inner_texts()
        hrefs = [await a.get_attribute('href') for a in await c.locator('a[target="_blank"]').all()]
        check({'TEXTBOOK', 'SLIDES', 'QUIZ', 'ANSWER KEY', 'KAHOOT'} <= {k.upper() for k in ks} and all(h.startswith('https://') for h in hrefs) and any('drive.google.com' in h for h in hrefs),
              f'teacher: chapter {n} lists textbook, slides, quiz, answer key, Kahoot (Drive links)')
    body = (await tm.inner_text()).lower(); check('password:' not in body, 'teacher: no password shown in Teaching Materials')
    check(await t.locator('#app').is_hidden() and await t.locator('#keyv').is_hidden(), 'teacher: tabs switch panes')
    await t.screenshot(path=SHOTS + 'ch_teacher_materials.png', full_page=True)
    # Answer Key chapter filter
    await t.click('#t2'); await t.wait_for_selector('#kl .ki')
    K = await t.evaluate("window.JC_KEY")
    await t.select_option('#kc', '3'); n3 = await t.locator('#kl .ki').count()
    check(n3 == sum(1 for k in K if 3 in (k.get('ch') or [])) and n3 > 50, f'teacher: Answer Key Chapter 3 filter ({n3} items)')
    await t.select_option('#kc', ''); await t.select_option('#ka', 'new'); nn = await t.locator('#kl .ki').count()
    check(nn == 66, f'teacher: Answer Key shows the {nn} new Ch 1-7 items with answers')
    check(all(k['a'] and k['why'] for k in K if k.get('new')), 'teacher: every new item has an answer and explanation')
    check(sum(1 for k in K if not k.get('ch')) == 0, 'teacher: every Answer Key item maps to a chapter')
    await t.click('#t1'); check(await t.locator('#app').is_visible(), 'teacher: back to the Class tab')
    bad = [x for x in errs if 'pageerror' in x]; check(not bad, 'no page errors (teacher chapters) ' + str(bad[:3]))

def static_checks():
    print('--- Chapters: static checks')
    files = [f for f in glob.glob(SITE + '/**/*', recursive=True) if os.path.isfile(f) and '/.git/' not in f and '/tests/' not in f and not f.endswith(('.png', '.pdf', '.docx'))]
    blob = ''.join(open(f, encoding='utf-8', errors='ignore').read() for f in files)
    sec = secrets_from_accounts_doc()
    check(sec and not any(s in blob for s in sec), f'Texidium shared login is not anywhere on the site ({len(sec)} values checked)')
    # Spot check: no long verbatim runs from the textbook in the new items
    src = open(SITE + '/tools/chapter_items.py', encoding='utf-8').read()
    book = ' '.join(open(f, encoding='utf-8', errors='ignore').read() for f in glob.glob('/workspace/BCC_IC3_Class/ch1-7_text/**/*.txt', recursive=True))
    book = re.sub(r'\s+', ' ', book).lower()
    words = re.findall(r"[a-z0-9']+", re.sub(r'\s+', ' ', src).lower())
    hits = {' '.join(words[i:i + 9]) for i in range(len(words) - 9) if ' '.join(words[i:i + 9]) in book}
    check(not hits if book.strip() else True, f'new items share no 9-word run with the textbook, quizzes, or key ({list(hits)[:2]})')
    check('\u2014' not in blob, 'no em dashes anywhere on the site')

async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try: socket.create_connection(('127.0.0.1', PORT), .2).close(); break
        except OSError: time.sleep(.1)
    try:
        static_checks()
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome')
            await part_a(b); await part_b(b); await b.close()
    finally: srv.terminate()
    f = [m for ok, m in results if not ok]
    print(f'\n{len(results) - len(f)}/{len(results)} checks passed'); sys.exit(1 if f else 0)
if __name__ == '__main__':
    asyncio.run(main())
