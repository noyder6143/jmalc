"""Render chapters.html?all=1 to Chapter_Summaries_Ch1-7.pdf (site resources/ and /workspace/BCC_IC3_Class/)."""
import asyncio, os, shutil, subprocess, sys, time, socket
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(SITE, 'resources', 'Chapter_Summaries_Ch1-7.pdf')
COPY = '/workspace/BCC_IC3_Class/Chapter_Summaries_Ch1-7.pdf'
from playwright.async_api import async_playwright
FOOT = ('<div style="font-size:8px;color:#7a8796;width:100%;padding:0 .55in;display:flex;justify-content:space-between;font-family:Arial">'
        '<span>Jmal C\'s Digital Literacy Class · Chapter Summaries, Ch 1-7</span><span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span></div>')
async def main():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); port = s.getsockname()[1]; s.close()
    srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1'], cwd=SITE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as pw:
            b = await pw.chromium.launch(executable_path='/usr/bin/google-chrome'); p = await b.new_page()
            await p.goto(f'http://127.0.0.1:{port}/chapters.html?all=1#ch=1'); await p.wait_for_selector('.chap.show')
            await p.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            await p.emulate_media(media='print')
            await p.pdf(path=OUT, format='Letter', print_background=True, display_header_footer=True, header_template='<span></span>',
                        footer_template=FOOT, margin=dict(top='0.55in', bottom='0.65in', left='0.55in', right='0.55in'))
            await b.close()
    finally:
        srv.terminate()
    shutil.copy(OUT, COPY)
asyncio.run(main())
pages = subprocess.run(['pdfinfo', OUT], capture_output=True, text=True).stdout
print(OUT, [l for l in pages.splitlines() if l.startswith(('Pages', 'File size'))])
