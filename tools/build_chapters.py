"""Write chapters.html: the in-site Chapter 1-7 study summary reader (chapters.html#ch=N).
All seven chapters are rendered as static HTML (works offline, prints, no JS needed to read);
a small script shows one chapter at a time based on the #ch= hash. ?all=1 shows every chapter (used for the PDF)."""
import os, sys
from html import escape as E
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters import CHAPTERS
from summaries import SUMMARIES
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_NAME = 'Chapter_Summaries_Ch1-7.pdf'

def words(c):
    t = [c['intro']] + c['know'] + [a + ' ' + b for a, b in c['vocab'] + c['check']]
    for s in c['sections']:
        t += s.get('bullets', []); tb = s.get('table')
        if tb: t += [' '.join(r) for r in tb['rows']]
    return len(' '.join(t).split())

def minutes(c):  # about 150 words a minute for study reading with tables
    return max(5, min(10, round(words(c) / 150 + 1)))

def ul(items, cls=''):
    return f'<ul{" class=" + chr(34) + cls + chr(34) if cls else ""}>' + ''.join(f'<li>{E(x)}</li>' for x in items) + '</ul>'

def table(tb):
    h = ''.join(f'<th scope="col">{E(x)}</th>' for x in tb['head'])
    rows = ''.join('<tr>' + ''.join((f'<th scope="row">{E(x)}</th>' if i == 0 else f'<td>{E(x)}</td>') for i, x in enumerate(r)) + '</tr>' for r in tb['rows'])
    return f'<div class="tw"><table><thead><tr>{h}</tr></thead><tbody>{rows}</tbody></table></div>'

def chapter(c):
    n = c['n']; s = SUMMARIES[n]; m = minutes(s)
    out = [f'<article class="chap" id="ch{n}" data-ch="{n}" aria-labelledby="h{n}">',
           f'<div class="chead"><span class="kick">Chapter {n} of 7 · about {m} min read</span><h2 id="h{n}">{c["icon"]} Chapter {n}: {E(c["title"])}</h2>',
           f'<p class="intro">{E(s["intro"])}</p></div>']
    for sec in s['sections']:
        out.append(f'<section><h3>{E(sec["h"])}</h3>')
        if sec.get('table'): out.append(table(sec['table']))
        if sec.get('bullets'): out.append(ul(sec['bullets']))
        out.append('</section>')
    out.append('<section class="vocab"><h3>🔤 Key vocabulary</h3><dl>' + ''.join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a, b in s['vocab']) + '</dl></section>')
    out.append('<section class="know"><h3>✅ Know for the test</h3>' + ul(s['know']) + '</section>')
    out.append('<section class="check"><h3>🧠 Quick self-check</h3><p class="hint">Answer in your head, then tap a question to see the answer.</p>' +
               ''.join(f'<details><summary><b>Q{i}.</b> {E(q)}</summary><p><b>Answer:</b> {E(a)}</p></details>' for i, (q, a) in enumerate(s['check'], 1)) + '</section>')
    out.append(f'<div class="mk noprint"><button type="button" class="mark" data-ch="{n}">✓ Mark as read</button><span class="mkt" role="status" aria-live="polite">Finished reading? Tap the button. It shows on your home page.</span></div>')
    out.append(f'<div class="next noprint"><a class="go q" href="quest.html#ch={n}">🎮 Learn it: Chapter {n} Quest lessons</a>'
               f'<a class="go p" href="practice.html#chapter={n}">📝 Practice it: Chapter {n} Quiz</a></div>')
    out.append(f'<p class="opt noprint">Want every detail? <a href="https://texidium.com/" target="_blank" rel="noopener">Full textbook (optional): Chapter {n} on Texidium</a></p>')
    out.append('</article>')
    return '\n'.join(out)

CSS = """*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:#f4f7fb;color:#14202e;line-height:1.55;font-size:17px}
header{background:linear-gradient(120deg,#1d3557,#0f7c83);color:#fff;padding:1.4rem 1rem 1.6rem;text-align:center}
header .brand{margin:0;font-size:clamp(1.2rem,4.5vw,1.7rem);font-weight:800}header .brand a{color:#fff;text-decoration:none}header p{margin:.2rem 0 0;opacity:.92}
nav.chnav{position:sticky;top:0;z-index:5;background:#fff;box-shadow:0 2px 10px rgba(20,32,46,.12);padding:.5rem;display:flex;gap:.35rem;overflow-x:auto;justify-content:safe center}
nav.chnav a{flex:0 0 auto;padding:.45rem .75rem;border-radius:999px;background:#eef3f8;color:#1d3557;font-weight:700;text-decoration:none;font-size:.92rem}
nav.chnav a.on{background:#0f7c83;color:#fff}nav.chnav a:focus-visible,.go:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #1d3557;outline-offset:2px}
main{max-width:860px;margin:1rem auto 2rem;padding:0 .8rem}
.tools{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;margin:0 0 1rem}.tools .sp{flex:1}
button,.btnl{font:inherit;font-weight:700;border:0;border-radius:12px;padding:.6rem 1rem;background:#1d3557;color:#fff;cursor:pointer;text-decoration:none;display:inline-block}
.btnl.alt{background:#fff;color:#1d3557;border:2px solid #1d3557;padding:.45rem .9rem}
.chap{background:#fff;border-radius:18px;padding:1.1rem 1.1rem 1.3rem;box-shadow:0 6px 20px rgba(20,32,46,.1);margin-bottom:1.2rem}
.js .chap{display:none}.js .chap.show,.all .chap{display:block}
.kick{display:inline-block;font-size:.8rem;font-weight:700;letter-spacing:.03em;text-transform:uppercase;color:#0f7c83}
.chap h2{margin:.15rem 0 .4rem;font-size:clamp(1.35rem,4.5vw,1.8rem);color:#1d3557}.intro{margin:0 0 .4rem;font-size:1.05rem;color:#2c3a4b}
.chap h3{margin:1.3rem 0 .45rem;font-size:1.15rem;color:#1d3557;border-bottom:2px solid #e6ebf2;padding-bottom:.2rem}
.chap ul{margin:.4rem 0;padding-left:1.25rem}.chap li{margin:.25rem 0}
.tw{overflow-x:auto;margin:.4rem 0 .5rem;border-radius:10px;border:1px solid #dfe6ee}
table{border-collapse:collapse;width:100%;font-size:.94rem;min-width:420px}th,td{padding:.45rem .6rem;text-align:left;vertical-align:top;border-top:1px solid #e6ebf2}
thead th{background:#1d3557;color:#fff;border-top:0;font-size:.88rem}tbody th{font-weight:700;color:#14202e;background:#f7fafc}tbody tr:nth-child(even) td{background:#fbfcfe}
.vocab dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:.5rem;margin:.4rem 0}.vocab dl div{background:#f4f7fb;border-radius:10px;padding:.5rem .7rem}
dt{font-weight:800;color:#0f5f66}dd{margin:.1rem 0 0;font-size:.94rem}
.know{background:#fff8e1;border-left:6px solid #ffcc33;border-radius:12px;padding:.2rem 1rem .6rem;margin-top:1.2rem}.know h3{border:0}
.check .hint{margin:.2rem 0 .5rem;color:#46566a;font-size:.92rem}
details{border:1px solid #dfe6ee;border-radius:12px;margin:.45rem 0;background:#f9fbfd}summary{cursor:pointer;padding:.7rem .9rem;list-style-position:inside}
details[open] summary{border-bottom:1px solid #dfe6ee}details p{margin:0;padding:.6rem .9rem;background:#e9f7f3;border-radius:0 0 12px 12px}
.next{display:grid;gap:.6rem;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));margin-top:1.3rem}
.go{display:block;text-align:center;text-decoration:none;font-weight:700;padding:.85rem;border-radius:14px}.go.q{background:#ffcc33;color:#1a1a1a}.go.p{background:#0f7c83;color:#fff}
.opt{margin:.9rem 0 0;font-size:.9rem;color:#46566a}.opt a{color:#0f5f66}
footer{text-align:center;padding:0 1rem 2rem;font-size:.82rem;color:#7a8796}footer a{color:#5c6b7c}
.pfoot{display:none}
#acct{margin-top:.5rem}#acct:empty{display:none}
.mk{display:flex;flex-wrap:wrap;align-items:center;gap:.6rem;margin-top:1.3rem;background:#eef8f3;border-radius:14px;padding:.8rem}
button.mark{background:#2ecc71;color:#073b1d;font-size:1.1rem;min-height:56px;padding:.7rem 1.3rem;border-radius:14px}button.mark.on{background:#fff;color:#1d6b3f;border:2px solid #2ecc71}
.mkt{flex:1;min-width:12rem;font-size:.95rem;color:#2c3a4b}
@media print{
 @page{size:letter;margin:.55in .55in .6in}
 body{background:#fff;font-size:11pt;line-height:1.4}header{background:none;color:#1d3557;padding:0 0 .3rem;text-align:left;border-bottom:3px solid #0f7c83}
 header .brand a{color:#1d3557}header p{opacity:1;color:#46566a}
 nav.chnav,.tools,.noprint,footer{display:none!important}main{max-width:none;margin:0;padding:0}
 .chap{box-shadow:none;border-radius:0;padding:0;margin:0}.all .chap+.chap,.chap.brk{break-before:page}
 .chap h3,summary,dt{break-after:avoid}tr,.vocab dl div,details,.know li{break-inside:avoid}table{min-width:0;font-size:9.5pt}.tw{overflow:visible}
 thead th{background:#1d3557!important;color:#fff!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}
 .know{-webkit-print-color-adjust:exact;print-color-adjust:exact}details{background:#fff}details p{background:#fff;padding:.2rem .9rem .5rem}summary{list-style:none}summary::-webkit-details-marker{display:none}
 .pfoot{display:block;margin-top:1rem;font-size:8.5pt;color:#7a8796;border-top:1px solid #dfe6ee;padding-top:.3rem}
}"""

JS = r"""(function(){var d=document.documentElement,qs=new URLSearchParams(location.search);d.classList.add('js');if(qs.get('all')==='1')d.classList.add('all');
var A=[].slice.call(document.querySelectorAll('.chap')),N=[].slice.call(document.querySelectorAll('nav.chnav a'));
function cur(){var m=/ch=(\d)/.exec(location.hash);var n=m?+m[1]:1;return n>=1&&n<=7?n:1}
function show(){var n=cur(),all=d.classList.contains('all');A.forEach(function(a){a.classList.toggle('show',all||+a.dataset.ch===n)});
 N.forEach(function(a){var on=!all&&+a.dataset.ch===n;a.classList.toggle('on',on);if(on)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')});
 var pb=document.getElementById('pr');if(pb)pb.textContent=all?'🖨️ Print / Save as PDF (all chapters)':'🖨️ Print / Save as PDF';
 var t=document.getElementById('alltog');if(t){t.textContent=all?'Show one chapter':'Show all 7 chapters';}
 document.title=(all?'Chapters 1-7 Study Summaries':'Chapter '+n+' Summary')+" · Jmal C's Digital Literacy Class"}
addEventListener('hashchange',function(){d.classList.remove('all');show();scrollTo(0,0)});
N.forEach(function(a){a.addEventListener('click',function(){d.classList.remove('all')})});
var t=document.getElementById('alltog');if(t)t.onclick=function(){d.classList.toggle('all');show()};
var pr=document.getElementById('pr');if(pr)pr.onclick=function(){print()};
var opened=[];addEventListener('beforeprint',function(){opened=[];[].forEach.call(document.querySelectorAll('details:not([open])'),function(x){x.open=true;opened.push(x)})});
addEventListener('afterprint',function(){opened.forEach(function(x){x.open=false})});
show();window.__ch={cur:cur,show:show};
var QK='ic3quest_v1';function qget(){try{return JSON.parse(localStorage.getItem(QK))||{}}catch(e){return {}}}
function marks(){var r=qget().sread||[];[].forEach.call(document.querySelectorAll('button.mark'),function(b){var on=r.indexOf(+b.dataset.ch)>=0;b.classList.toggle('on',on);b.textContent=on?'✅ Read':'✓ Mark as read';b.setAttribute('aria-pressed',on?'true':'false');
 b.nextElementSibling.textContent=on?'Nice work! Next step: Play the Quest lessons.':'Finished reading? Tap the button. It shows on your home page.'})}
[].forEach.call(document.querySelectorAll('button.mark'),function(b){b.onclick=function(){var s=qget(),n=+b.dataset.ch,r=Array.isArray(s.sread)?s.sread:[];
 if(r.indexOf(n)<0){r.push(n);r.sort(function(a,c){return a-c});s.sread=r;try{localStorage.setItem(QK,JSON.stringify(s))}catch(e){}if(window.JCSync)JCSync.changed('quest')}marks()}});
marks();addEventListener('storage',marks);
if(window.JCSync&&JCSync.enabled){JCSync.attach({mount:'#acct'});JCSync.onAuth(marks)}
var hm=document.getElementById('home');function hl(){if(hm)hm.href='index.html#ch'+cur()}addEventListener('hashchange',hl);hl();
})();"""

def build():
    nav = ''.join(f'<a href="#ch={c["n"]}" data-ch="{c["n"]}">{c["icon"]} Ch {c["n"]}</a>' for c in CHAPTERS)
    body = '\n'.join(chapter(c) for c in CHAPTERS)
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chapter Summaries · Jmal C's Digital Literacy Class</title>
<meta name="description" content="Plain-language study summaries for Chapters 1-7 of IC3 GS5 Computing Fundamentals.">
<link rel="manifest" href="site.webmanifest"><meta name="theme-color" content="#1d3557">
<link rel="icon" href="icons/home-192.png"><link rel="apple-touch-icon" href="icons/home-180.png">
<script src="config.js"></script><script src="sync.js"></script>
<style>{CSS}</style></head><body>
<header><p class="brand"><a href="index.html">Jmal C's Digital Literacy Class</a></p><div id="acct" class="noprint"></div><p>Chapter Summaries · IC3 Computing Fundamentals, Chapters 1-7</p></header>
<nav class="chnav" aria-label="Chapters">{nav}</nav>
<main>
<div class="tools noprint"><a class="btnl alt" href="index.html#ch" id="home">← Home</a><span class="sp"></span>
<button type="button" id="alltog">Show all 7 chapters</button><button type="button" id="pr">🖨️ Print / Save as PDF</button>
<a class="btnl alt" href="resources/{PDF_NAME}" target="_blank" rel="noopener">All chapters PDF</a></div>
<p class="noprint" style="margin:-.3rem 0 1rem;color:#46566a;font-size:.92rem">Read the summary, check yourself, then learn it in the Quest and practice it in the Chapter Quiz. These summaries are written for our class in plain language.</p>
{body}
<p class="pfoot">Jmal C's Digital Literacy Class · Chapter Summaries for IC3 GS5 Computing Fundamentals, Chapters 1-7. Written for this class in plain language; not a copy of the textbook.</p>
</main>
<footer><a href="index.html">Home</a> · <a href="quest.html#ch=1">Quest</a> · <a href="practice.html#chapter=1">Practice Lab</a></footer>
<script>{JS}</script>
<script>if("serviceWorker" in navigator&&location.protocol.indexOf("http")===0){{addEventListener("load",function(){{navigator.serviceWorker.register("sw.js").catch(function(){{}})}})}}</script>
</body></html>
"""
    assert chr(0x2014) not in html, 'no em dashes'
    open(os.path.join(SITE, 'chapters.html'), 'w', encoding='utf-8').write(html)
    return {c['n']: minutes(SUMMARIES[c['n']]) for c in CHAPTERS}

if __name__ == '__main__':
    print('chapters.html minutes', build())
