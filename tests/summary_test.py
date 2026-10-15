"""Chapter Summaries tests: original wording (no 9-word run shared with the textbook), no em dashes,
reader page (chapters.html#ch=N), tap-to-reveal self-check, print button, mobile layout, links from the
landing chapter boxes and the Quest chapter view, combined PDF, and service worker cache.
Run: python3 tests/summary_test.py"""
import asyncio, os, sys, re, glob, subprocess, socket, time, html
sys.path.insert(0, os.path.dirname(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
from browser_test import watch, check, results, BASE, SITE, PORT, SHOTS
from playwright.async_api import async_playwright
from summaries import SUMMARIES
import build_chapters
PDF = os.path.join(SITE, 'resources', 'Chapter_Summaries_Ch1-7.pdf')
EMPTY = 'window.JC_CONFIG={SUPABASE_URL:"",SUPABASE_ANON_KEY:""};'
W = lambda t: re.findall(r"[a-z0-9]+", t.lower().replace('\u2019', "'").replace("'", ''))

def grams(ws, k=9): return {' '.join(ws[i:i + k]) for i in range(len(ws) - k + 1)}

def static_checks():
    print('--- Summaries: static checks')
    srcs = sorted(glob.glob('/workspace/BCC_IC3_Class/ch1-7_text/*.txt'))
    check(len(srcs) >= 7, f'source text found ({len(srcs)} files)')
    book = set().union(*(grams(W(open(f, encoding='utf-8', errors='ignore').read())) for f in srcs))
    page = open(os.path.join(SITE, 'chapters.html'), encoding='utf-8').read()
    vis = html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<(script|style)[^>]*>.*?</\1>', ' ', page, flags=re.S)))
    pdf = subprocess.run(['pdftotext', '-layout', PDF, '-'], capture_output=True, text=True).stdout if os.path.exists(PDF) else ''
    for name, text in [('summaries.py', open(os.path.join(SITE, 'tools', 'summaries.py'), encoding='utf-8').read()), ('chapters.html text', vis), ('PDF text', pdf)]:
        hits = grams(W(text)) & book
        check(text.strip() and not hits, f'{name}: no 9-word stretch matches the textbook ({len(book)} source 9-grams; hits {sorted(hits)[:3]})')
        check('\u2014' not in text, f'{name}: no em dashes')
    for n in range(1, 8):
        s = SUMMARIES[n]; m = build_chapters.minutes(s)
        check(3 <= len(s['check']) <= 5 and len(s['vocab']) >= 10 and len(s['know']) >= 5 and sum(1 for x in s['sections'] if x.get('table')) >= 4,
              f'chapter {n}: {len(s["check"])} self-check Qs, {len(s["vocab"])} terms, {len(s["know"])} test bullets, {sum(1 for x in s["sections"] if x.get("table"))} tables')
        check(5 <= m <= 10, f'chapter {n}: about {m} min read ({build_chapters.words(s)} words)')
    pages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', PDF], capture_output=True, text=True).stdout).group(1))
    check(pages >= 7 and all(f'Chapter {n}:' in pdf for n in range(1, 8)) and "Jmal C's Digital Literacy Class" in pdf, f'combined PDF has all 7 chapters, branded ({pages} pages)')
    check(os.path.exists('/workspace/BCC_IC3_Class/Chapter_Summaries_Ch1-7.pdf'), 'PDF copied to /workspace/BCC_IC3_Class/')
    sw = open(os.path.join(SITE, 'sw.js')).read()
    check("ic3-apps-v1" in sw and "'./chapters.html'" in sw, 'service worker cache bumped and caches chapters.html')
    return pages

async def browser(b):
    print('--- Summaries: browser')
    ctx = await b.new_context(viewport={'width': 1200, 'height': 900}, service_workers='block')
    await ctx.route('**/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=EMPTY))
    errs, ext = [], []; p = await ctx.new_page(); watch(p, errs, ext)
    # Landing chapter boxes: summary is the primary Read action, Texidium is optional
    await p.goto(BASE); await p.wait_for_load_state('networkidle')
    for n in range(1, 8):
        box = p.locator(f'#ch{n}')
        first = await box.locator('.btns a').first.get_attribute('href')
        check(first == f'chapters.html#ch={n}' and 'Read' in await box.locator('.btns a').first.inner_text(), f'home: chapter {n} card: Read (the summary) is the first button')
    tex = p.locator('#resources a[href*="texidium.com"]')
    check(await tex.count() == 1 and 'optional' in (await tex.inner_text()).lower(), 'home: Texidium listed only as optional')
    check(await p.locator('a[href="resources/Chapter_Summaries_Ch1-7.pdf"]').count() == 1, 'home: combined PDF linked')
    # Reader page
    await p.click('#ch3 .btns a[href="chapters.html#ch=3"]'); await p.wait_for_selector('#ch3.show')
    vis = await p.evaluate("[...document.querySelectorAll('.chap')].filter(a=>getComputedStyle(a).display!=='none').map(a=>a.dataset.ch)")
    check(vis == ['3'], f'reader: #ch=3 shows only Chapter 3 ({vis})')
    check(await p.locator('nav.chnav a.on').get_attribute('href') == '#ch=3', 'reader: chapter tab 3 highlighted')
    check('Chapter 3' in await p.title() and "Jmal C" in await p.title(), 'reader: title names the chapter and class')
    d = p.locator('#ch3 details').first; ans = d.locator('p')
    check(not await ans.is_visible(), 'reader: self-check answer hidden before tap')
    await d.locator('summary').click(); check(await ans.is_visible(), 'reader: answer revealed on tap')
    await p.click('nav.chnav a[href="#ch=6"]'); await p.wait_for_selector('#ch6.show')
    check(await p.evaluate("getComputedStyle(document.getElementById('ch3')).display") == 'none', 'reader: switching tabs swaps chapters')
    await p.evaluate("window.__printed=0;window.print=()=>{window.__printed++};0")
    await p.click('#pr'); check(await p.evaluate('window.__printed') == 1 and 'Save as PDF' in await p.inner_text('#pr'), 'reader: Print / Save as PDF button prints')
    await p.click('#alltog'); check(await p.evaluate("[...document.querySelectorAll('.chap')].every(a=>getComputedStyle(a).display!=='none')"), 'reader: Show all 7 chapters')
    for n in range(1, 8):
        a = p.locator(f'#ch{n}')
        ok = (await a.locator(f'a[href="quest.html#ch={n}"]').count() == 1 and await a.locator(f'a[href="practice.html#chapter={n}"]').count() == 1
              and await a.locator('a[href*="texidium.com"]').count() == 1 and 3 <= await a.locator('details').count() <= 5 and await a.locator('table').count() >= 4)
        check(ok, f'reader: chapter {n} has tables, 3-5 self-check Qs, Quest + Quiz links, optional textbook link')
    # Print media: menus hidden, answers shown
    await p.goto(BASE + 'chapters.html#ch=2'); await p.wait_for_selector('#ch2.show'); await p.emulate_media(media='print')
    await p.evaluate("dispatchEvent(new Event('beforeprint'))")
    check(await p.evaluate("getComputedStyle(document.querySelector('nav.chnav')).display==='none'&&getComputedStyle(document.querySelector('.tools')).display==='none'"), 'print: nav and buttons hidden')
    check(await p.evaluate("[...document.querySelectorAll('#ch2 details')].every(d=>d.open)"), 'print: self-check answers printed')
    await p.emulate_media(media='screen')
    # Quest chapter view links the summary
    await p.goto(BASE + 'quest.html#ch=4'); await p.wait_for_selector('#ch4')
    lk = p.locator('#ch4 a[href="chapters.html#ch=4"]')
    check(await lk.count() == 1 and 'Summary' in await lk.inner_text(), 'quest: chapter view links the Chapter 4 summary')
    await lk.click(); await p.wait_for_selector('#ch4.show'); check(p.url.endswith('chapters.html#ch=4'), 'quest: summary link opens chapters.html#ch=4')
    check(not errs, f'no page errors ({errs[:2]})')
    await ctx.close()
    # Mobile
    m = await b.new_context(viewport={'width': 375, 'height': 760}, is_mobile=True, has_touch=True, service_workers='block')
    await m.route('**/config.js', lambda r: r.fulfill(status=200, content_type='application/javascript', body=EMPTY))
    q = await m.new_page(); await q.goto(BASE + 'chapters.html#ch=1'); await q.wait_for_selector('#ch1.show')
    ov = await q.evaluate("document.documentElement.scrollWidth-innerWidth")
    check(ov <= 1, f'mobile: no sideways page scroll at 375px ({ov}px); wide tables scroll inside their box')
    await q.locator('#ch1 details summary').first.tap(); check(await q.locator('#ch1 details p').first.is_visible(), 'mobile: tap reveals answer')
    await q.screenshot(path=SHOTS + 'summary_mobile.png', full_page=False)
    await m.close()

async def main():
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT), '--bind', '127.0.0.1'], cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(50):
        try: socket.create_connection(('127.0.0.1', PORT), .2).close(); break
        except OSError: time.sleep(.1)
    try:
        static_checks()
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome'); await browser(b); await b.close()
    finally:
        srv.terminate()
    bad = [r for r in results if not r[0]]
    print(f'\n{len(results) - len(bad)}/{len(results)} passed')
    sys.exit(1 if bad else 0)
asyncio.run(main())
