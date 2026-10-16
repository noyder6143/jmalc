"""Write index.html: the student home (Chapters 1-7 portal).
Static HTML for every card and link (works with no JS and offline); a small script fills in the
student's name, next class, progress, checklists, and the Continue button from the data the apps
already save (ic3quest_v1, ic3lab_v1). 'Summary read' lives in the Quest save as sread:[n,...],
so it syncs to the cloud with the rest of the Quest progress and the teacher dashboard can see it."""
import json, os
from html import escape as E
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Class schedule (from resources/Class_Calendar.pdf). All classes Mon/Wed 6:00-9:00 PM ET.
SESSIONS = [
    ('2026-10-19', 'In person', 'Welcome + Hardware I'), ('2026-10-21', 'In person', 'Hardware II + networks'),
    ('2026-10-26', 'Online', 'Mobile Devices'), ('2026-10-28', 'Online', 'Software I: operating systems'),
    ('2026-11-02', 'Online', 'Files, permissions, file sharing'), ('2026-11-04', 'Online', 'Install, troubleshoot, backup'),
    ('2026-11-09', 'Online', 'Cloud Computing'), ('2026-11-11', 'Online', 'Security'),
    ('2026-11-16', 'Online', 'Review: Mock Exam 1'), ('2026-11-18', 'Online', 'Review: Final Exam Review + Mock Exam 2'),
    ('2026-11-23', 'Online', 'Review: Mock Exam 3 + exam-day prep'), ('2026-11-25', 'Online', 'Final check + your exam plan'),
]
TOOLS = [
    ('https://quizlet.com/user/azul5477/folders/part-1', '🃏', 'Quizlet', 'Class flashcards'),
    ('https://kahoot.it/', '🎉', 'Kahoot', 'Class game. Type the PIN from class'),
    ('https://bccadulteducationandtraining.typingclub.com/', '⌨️', 'Typing Club', 'Typing practice (BCC Adult Ed)'),
    ('https://www.liveworksheets.com/workbook/299177', '📝', 'Liveworksheets', 'Class workbook'),
    ('https://texidium.com/', '📚', 'Texidium (optional)', 'The full textbook, if you want more detail'),
]

def kb(path):
    return f"{max(1, round(os.path.getsize(os.path.join(SITE, path)) / 1024))} KB"

CSS = r"""*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:#f4f7fb;color:#14202e;line-height:1.5;font-size:18px}
a{color:#0f5f66}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #ffcc33;outline-offset:3px}
header{background:linear-gradient(120deg,#1d3557,#0f7c83);color:#fff;padding:1rem 1rem 3.2rem}
.top{max-width:760px;margin:0 auto;display:flex;align-items:center;gap:.6rem;flex-wrap:wrap}.brand{font-weight:800;font-size:1rem;flex:1;min-width:12rem}
#acct{flex:0 0 auto}#acct .jcs-chip{font-size:1rem;padding:.55em 1em;min-height:44px}
.hello{max-width:760px;margin:1rem auto 0}.hello h1{margin:0;font-size:clamp(1.6rem,6vw,2.3rem);line-height:1.2}.hello p{margin:.3rem 0 0;opacity:.95}
.next{margin-top:.9rem;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.3);border-radius:14px;padding:.7rem .9rem}
.next b{display:block;font-size:1.08rem}.next span{display:block;opacity:.95;font-size:.95rem}
main{max-width:760px;margin:-2.3rem auto 1.5rem;padding:0 .8rem;display:grid;gap:1rem}
.card{background:#fff;border-radius:18px;padding:1.1rem;box-shadow:0 6px 20px rgba(20,32,46,.1)}
.card h2{margin:0 0 .5rem;font-size:1.3rem;color:#1d3557}
.bar{height:22px;background:#e6ebf2;border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;width:0;background:linear-gradient(90deg,#0f7c83,#2ecc71);border-radius:999px;transition:width .4s}
.ptxt{display:flex;justify-content:space-between;gap:.5rem;flex-wrap:wrap;margin-top:.45rem;font-size:1rem}
.go{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.4rem;text-align:center;text-decoration:none;font-weight:800;font-size:1.15rem;padding:1rem;border-radius:16px;min-height:60px;background:#ffcc33;color:#1a1a1a;margin-top:.9rem;box-shadow:0 3px 0 #d9a800}
.go small{display:block;font-weight:600;font-size:.95rem;margin-top:.1rem}
.sec{margin:.6rem 0 -.3rem;font-size:1.25rem;color:#1d3557;padding:0 .2rem}
.ch{border-left:8px solid #c9d4e1}.ch.done{border-left-color:#2ecc71}
.ch .hd{display:flex;align-items:flex-start;gap:.6rem}.ch .ic{font-size:2rem;line-height:1}.ch h3{margin:0;font-size:1.2rem;flex:1;color:#1d3557}.ch h3 small{display:block;font-size:.85rem;color:#5c6b7c;font-weight:600}
.badge{display:none;margin:.5rem 0 0 2.6rem;background:#2ecc71;color:#073b1d;font-weight:800;border-radius:999px;padding:.25em .7em;font-size:.88rem;white-space:nowrap}.ch.done .badge{display:inline-block}
.btns{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin:.9rem 0 .7rem}
.btns a{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:72px;border-radius:14px;text-decoration:none;font-weight:800;font-size:1.08rem;padding:.5rem .3rem;line-height:1.15;text-align:center}
.btns a span{font-size:1.5rem;line-height:1.1}.btns a small{font-weight:600;font-size:.78rem;opacity:.9;margin-top:.15rem}
.btns .read{background:#1d3557;color:#fff}.btns .play{background:#ffcc33;color:#1a1a1a}.btns .quiz{background:#0f7c83;color:#fff}
.btns a.ok{box-shadow:inset 0 0 0 3px #2ecc71}
a.games{display:flex;align-items:center;justify-content:center;gap:.4rem;min-height:52px;margin:-.2rem 0 .7rem;border-radius:14px;background:#efe7fa;color:#4b2a85;font-weight:800;text-decoration:none;font-size:1.05rem;border:2px solid #d6c6f0}
a.games small{font-weight:600;font-size:.82rem;opacity:.85}a.games.ok{border-color:#2ecc71}
ul.chk{list-style:none;margin:0;padding:0;font-size:1rem}ul.chk li{display:flex;gap:.5rem;align-items:center;padding:.3rem 0;border-top:1px solid #eef2f6}ul.chk li:first-child{border-top:0}
ul.chk .b{width:1.6rem;height:1.6rem;flex:0 0 1.6rem;border-radius:7px;border:2px solid #b9c3cf;display:flex;align-items:center;justify-content:center;font-weight:900;color:#fff}
ul.chk li.gm.y .b{background:#7a4fb5;border-color:#7a4fb5}ul.chk li.gm.y .b::after{content:"★"}ul.chk li.y .b{background:#2ecc71;border-color:#2ecc71}ul.chk li.y .b::after{content:"✓"}
.ready{display:flex;gap:.8rem;align-items:center;margin:.3rem 0 .7rem}.dots{display:flex;gap:.4rem}.dots i{width:2.2rem;height:2.2rem;border-radius:50%;border:3px solid #b9c3cf;display:flex;align-items:center;justify-content:center;font-style:normal;font-weight:900;color:#fff}
.dots i.y{background:#2ecc71;border-color:#2ecc71}.dots i.y::after{content:"✓"}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:.5rem}
a.btn{display:flex;align-items:center;justify-content:center;gap:.35rem;text-align:center;text-decoration:none;font-weight:800;padding:.85rem .6rem;border-radius:14px;min-height:56px;font-size:1.02rem}
a.b1{background:#0f7c83;color:#fff}a.b2{background:#1d3557;color:#fff}a.b3{background:#eef3f8;color:#1d3557;border:2px solid #c9d4e1}
ul.tools{list-style:none;margin:0;padding:0;display:grid;gap:.45rem}ul.tools a{display:flex;gap:.7rem;align-items:center;min-height:56px;padding:.55rem .8rem;border-radius:14px;background:#f4f7fb;text-decoration:none;color:#14202e}
ul.tools a b{display:block;color:#0f5f66}ul.tools a span.e{font-size:1.5rem}ul.tools a small{display:block;color:#5c6b7c;font-size:.88rem}
details.x{border-radius:14px;background:#f4f7fb}details.x summary{cursor:pointer;font-weight:800;padding:.9rem 1rem;min-height:52px;color:#1d3557}
details.x ol{margin:0;padding:0 1rem 1rem 2.2rem}details.x li{padding:.35rem 0}details.x .meta{color:#7a8796;font-size:.85rem}
.small{font-size:.92rem;color:#46566a}.muted{color:#5c6b7c}
.note ul{margin:.3rem 0 0;padding-left:1.2rem}.note li{margin:.3rem 0;font-size:.95rem}
footer{text-align:center;padding:0 1rem 2rem;font-size:.85rem;color:#7a8796}footer a{color:#7a8796}
@media (min-width:700px){header{padding:1.2rem 1.2rem 3.4rem}.btns a{min-height:78px}}
@media (max-width:360px){.btns a{font-size:.98rem}.row2{grid-template-columns:1fr}}"""

JS = r"""(function(){var H=window.JC_HOME,$=function(s){return document.querySelector(s)};
function get(k){try{return JSON.parse(localStorage.getItem(k))||{}}catch(e){return {}}}
function esc(t){return String(t==null?'':t).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function nowET(){var d=window.JC_NOW?new Date(window.JC_NOW):new Date();var p={};new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(d).forEach(function(x){p[x.type]=x.value});
 return {day:p.year+'-'+p.month+'-'+p.day,min:(+p.hour)*60+(+p.minute)}}
function nice(day){var d=new Date(day+'T12:00:00Z');return d.toLocaleDateString('en-US',{weekday:'long',month:'long',day:'numeric',timeZone:'UTC'})}
function nextClass(){var n=nowET(),S=H.sessions;for(var i=0;i<S.length;i++){var s=S[i];if(s[0]>n.day||(s[0]===n.day&&n.min<21*60)){
  var t=s[0]!==n.day?nice(s[0])+', 6:00 to 9:00 PM ET':(n.min>=18*60?'Class is on now (6:00 to 9:00 PM ET)':'Today, 6:00 to 9:00 PM ET');
  return {t:t,w:s[1]==='In person'?'🏫 In person':'💻 Online',topic:s[2],k:i+1}}}
 return null}
function prog(){var q=get(H.keys.quest),l=get(H.keys.practice),seen=q.seen||{},best=l.best||{},rd=q.sread||[];
 return H.chapters.map(function(c){var done=c.lessons.filter(function(p){return (seen[p[0]]||[]).indexOf(p[1])>=0}).length,b=best['ch'+c.n+':test'],tr=best['ch'+c.n+':train'];
  var r=rd.indexOf(c.n)>=0;return {n:c.n,games:c.games,read:r,les:done,tot:c.lessons.length,best:b==null?null:b,train:tr==null?null:tr,complete:b!=null&&b>=80,
   pct:((r?1:0)+(c.lessons.length?done/c.lessons.length:1)+Math.min(1,(b||0)/80))/3}})}
function ready(){var h=(get(H.keys.practice).history||[]).filter(function(x){return x&&x.test==='final'&&x.mode==='test'});
 var pass=h.filter(function(x){return (+x.pct||0)>=80}).length,b=h.reduce(function(m,x){return Math.max(m,+x.pct||0)},-1);return {pass:pass,best:b<0?null:b,tries:h.length}}
function name(){var u=window.JCSync&&JCSync.user&&JCSync.user(),p=u&&JCSync.profile&&JCSync.profile();
 var n=(p&&p.display_name)||(u&&u.user_metadata&&u.user_metadata.display_name)||'';if(!n&&u)n=(u.email||'').split('@')[0];if(!n)n=get(H.keys.quest).name||'';return String(n).trim().split(/\s+/)[0]||''}
function li(el,y,t){el.className=y?'y':'';el.querySelector('.t').innerHTML=t}
function render(){var P=prog(),R=ready(),nm=name();
 $('#hi').textContent=nm?'Welcome, '+nm+'!':'Welcome!';
 var nc=nextClass(),ne=$('#nextc');if(nc){ne.innerHTML='<b>📅 Next class: '+esc(nc.t)+'</b><span>'+esc(nc.w)+' · Class '+nc.k+' of '+H.sessions.length+': '+esc(nc.topic)+'</span>'}
 else ne.innerHTML='<b>🎓 Our classes are finished.</b><span>Keep practicing, and schedule your IC3 exam when you are ready.</span>';
 var tot=P.reduce(function(a,x){return a+x.pct},0)/P.length,cd=P.filter(function(x){return x.complete}).length,pc=Math.round(tot*100);
 $('#ovbar i').style.width=pc+'%';$('#ovbar').setAttribute('aria-valuenow',pc);$('#ovpct').textContent=pc+'% done';$('#ovch').textContent=cd+' of 7 chapters complete';
 P.forEach(function(x){var card=$('#ch'+x.n),L=card.querySelectorAll('ul.chk li');card.classList.toggle('done',x.complete);
  li(L[0],x.read,x.read?'Summary read':'Summary: not read yet');
  li(L[1],x.tot&&x.les>=x.tot,'Quest lessons done: <b>'+x.les+' of '+x.tot+'</b>');
  li(L[2],x.complete,x.best!=null?'Best quiz score: <b>'+x.best+'%</b>'+(x.complete?'':' (goal: 80%)'):(x.train!=null?'Best quiz score: <b>'+x.train+'%</b> in Practice mode. Take it in Test mode to count.':'Best quiz score: none yet (goal: 80%)'));
  var cg=get(H.keys.quest),gp=x.games.filter(function(id){return (cg.cgn||{})[id]}),gs=x.games.map(function(id){return (cg.cgs||{})[id]||0});
  li(L[3],gp.length>0,'Games played: <b>'+gp.length+' of '+x.games.length+'</b>'+(gp.length?' · best '+gs.map(function(n){return n?'⭐'.repeat(n):'☆'}).join(' '):''));card.querySelector('a.games').classList.toggle('ok',gp.length===x.games.length);
  card.querySelector('.read').classList.toggle('ok',x.read);card.querySelector('.play').classList.toggle('ok',x.tot&&x.les>=x.tot);card.querySelector('.quiz').classList.toggle('ok',x.complete)});
 var ds=document.querySelectorAll('#final .dots i');for(var i=0;i<ds.length;i++)ds[i].className=R.pass>i?'y':'';
 $('#rtxt').innerHTML=R.pass>=2?'<b>✅ You reached the goal!</b> Talk to your teacher about your exam date.':'<b>'+Math.min(R.pass,2)+' of 2</b> times at 80% or more.'+(R.best!=null?' Your best: <b>'+R.best+'%</b>.':' You have not taken it yet.');
 // Continue: first chapter step that is not done
 var go=null,any=P.some(function(x){return x.read||x.les||x.best!=null||x.train!=null});
 for(var k=0;k<P.length&&!go;k++){var x=P[k];if(x.complete)continue;
  if(!x.read)go=['chapters.html#ch='+x.n,'Chapter '+x.n+': Read the summary'];
  else if(x.les<x.tot)go=['quest.html#ch='+x.n,'Chapter '+x.n+': Play the Quest lessons'];
  else if(!x.complete)go=['practice.html#chapter='+x.n,'Chapter '+x.n+': Take the quiz'];}
 if(!go)go=R.pass>=2?['practice.html#final','All chapters done! Keep your Final Exam Review score up']:['practice.html#final','All chapters done! Take the Final Exam Review'];
 [].forEach.call(document.querySelectorAll('a.cont'),function(a){a.href=go[0];a.innerHTML='▶ '+(any?'Continue where you left off':'Start here')+'<small>'+esc(go[1])+'</small>'});
 window.__home={prog:P,ready:R,next:nc,go:go,pct:pc}}
window.JCHome={render:render};render();
addEventListener('storage',render);addEventListener('pageshow',render);document.addEventListener('visibilitychange',function(){if(document.visibilityState==='visible')render()});
if(window.JCSync&&JCSync.enabled){document.getElementById('cloud-note').hidden=false;document.getElementById('local-note').textContent='Without an account, your progress saves on this device and in this browser only.';
 JCSync.attach({mount:'#acct'});JCSync.onAuth(function(){render()})}})();"""

def build(chapters, minutes, lessons, quizn, workbooks, games):
    data = dict(keys=dict(quest='ic3quest_v1', practice='ic3lab_v1'), sessions=SESSIONS,
                chapters=[dict(n=c['n'], title=c['title'], lessons=lessons[c['n']], games=games[c['n']]) for c in chapters])
    cards = []
    for c in chapters:
        n = c['n']
        cards.append(
            f'<section class="card ch" id="ch{n}" aria-labelledby="cht{n}"><div class="hd"><span class="ic" aria-hidden="true">{c["icon"]}</span>'
            f'<h3 id="cht{n}">Chapter {n}: {E(c["title"])}<small>Read about {minutes[n]} min · {len(lessons[n])} Quest lessons · {quizn[n]} quiz questions</small></h3>'
            f'</div><span class="badge">✓ Chapter complete</span>'
            f'<div class="btns"><a class="read" href="chapters.html#ch={n}"><span aria-hidden="true">📖</span>Read<small>Summary</small></a>'
            f'<a class="play" href="quest.html#ch={n}"><span aria-hidden="true">🎮</span>Play<small>Quest lessons</small></a>'
            f'<a class="quiz" href="practice.html#chapter={n}"><span aria-hidden="true">📝</span>Quiz<small>Get 80%</small></a></div>'
            f'<a class="games" href="games.html#ch={n}"><span aria-hidden="true">🎲</span> Games <small>{len(games[n])} quick games</small></a>'
            f'<ul class="chk" aria-label="Chapter {n} checklist"><li><span class="b" aria-hidden="true"></span><span class="t">Summary: not read yet</span></li>'
            f'<li><span class="b" aria-hidden="true"></span><span class="t">Quest lessons done: 0 of {len(lessons[n])}</span></li>'
            f'<li><span class="b" aria-hidden="true"></span><span class="t">Best quiz score: none yet (goal: 80%)</span></li>'
            f'<li class="gm"><span class="b" aria-hidden="true"></span><span class="t">Games played: 0 of {len(games[n])}</span></li></ul></section>')
    tools = ''.join(f'<li><a href="{u}" target="_blank" rel="noopener"><span class="e" aria-hidden="true">{e}</span><span><b>{E(t)}</b><small>{E(d)}</small></span></a></li>' for u, e, t, d in TOOLS)
    wbs = ''.join(f'<li><a href="resources/workbooks/{f}" target="_blank" rel="noopener">LearnKey Lesson {i}: {E(t)}</a> <span class="meta">Chapter {", ".join(map(str, chs))} · PDF, {kb("resources/workbooks/" + f)}</span></li>'
                  for i, (f, t, chs) in enumerate(workbooks, 1))
    cont = '<a class="go cont" href="chapters.html#ch=1">▶ Start here<small>Chapter 1: Read the summary</small></a>'
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Jmal C's Digital Literacy Class</title>
<meta name="description" content="Student home for Jmal C's Digital Literacy Class: IC3 Computing Fundamentals, Chapters 1-7.">
<link rel="manifest" href="site.webmanifest"><meta name="theme-color" content="#1d3557">
<link rel="icon" href="icons/home-192.png"><link rel="apple-touch-icon" href="icons/home-180.png">
<script src="config.js"></script><script src="sync.js"></script>
<style>{CSS}</style></head><body>
<header><div class="top"><div class="brand">Jmal C's Digital Literacy Class</div><div id="acct"></div></div>
<div class="hello"><h1 id="hi">Welcome!</h1><p>IC3 Computing Fundamentals, Chapters 1 to 7. Each chapter has 3 steps: Read, Play, Quiz.</p>
<div class="next" id="nextc" role="status"><b>📅 Classes: Monday and Wednesday, 6:00 to 9:00 PM ET</b><span>October 19 to November 25. Week 1 is in person. The other weeks are online.</span></div></div></header>
<main>
<section class="card" id="progress" aria-labelledby="pgh"><h2 id="pgh">📈 My progress</h2>
<div class="bar" id="ovbar" role="progressbar" aria-label="Progress in Chapters 1 to 7" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i></i></div>
<div class="ptxt"><b id="ovpct">0% done</b><span id="ovch">0 of 7 chapters complete</span></div>
{cont}
<p class="small" style="margin:.7rem 0 0">A chapter is complete when you get <b>80% or more</b> on its quiz in Test mode.</p></section>
<h2 class="sec" id="chapters">📘 My chapters</h2>
{chr(10).join(cards)}
<section class="card" id="final" aria-labelledby="fnh"><h2 id="fnh">🎓 Final Exam Review</h2>
<p class="small" style="margin:0 0 .4rem">When you finish the chapters, practice for the real IC3 exam. <b>Goal: score 80% or more on the Final Exam Review 2 times.</b></p>
<div class="ready"><div class="dots" aria-hidden="true"><i></i><i></i></div><div id="rtxt"><b>0 of 2</b> times at 80% or more.</div></div>
<div class="row2"><a class="btn b1" href="practice.html#final">📝 Final Exam Review</a><a class="btn b2" href="https://www.gmetrix.net" target="_blank" rel="noopener">🎯 GMetrix</a></div>
<p class="small" style="margin:.6rem 0 0">GMetrix has the official practice tests. Your teacher gives you the GMetrix sign-in in class.</p></section>
<section class="card" id="resources" aria-labelledby="rsh"><h2 id="rsh">🧰 Class Tools</h2>
<ul class="tools">{tools}</ul>
<p class="small" style="margin:.6rem 0 0">Never post class logins online.</p>
<h2 style="margin-top:1.1rem">📅 Calendar</h2>
<div class="row2"><a class="btn b3" href="resources/Class_Calendar.pdf" target="_blank" rel="noopener">📅 Class Calendar (PDF)</a><a class="btn b3" href="resources/Chapter_Summaries_Ch1-7.pdf" target="_blank" rel="noopener">📖 All summaries (PDF)</a></div>
<h2 style="margin-top:1.1rem">📂 More practice</h2>
<div class="row2" style="margin-bottom:.6rem"><a class="btn b3" href="quest.html">🗺️ Full Quest map</a><a class="btn b3" href="practice.html">🧪 Practice Lab</a></div>
<details class="x" id="extra"><summary>➕ Extra practice: LearnKey workbooks (10)</summary>
<p class="small" style="margin:0 1rem .5rem">Optional. These PDFs go with the GMetrix lesson videos.</p><ol>{wbs}</ol>
<p class="small" style="margin:0 1rem .4rem">More study sheets: <a href="resources/study/Student_Vocab_Flashcards.pdf" target="_blank" rel="noopener">Vocabulary Flashcards</a> · <a href="resources/study/Student_Workbook_Handouts.pdf" target="_blank" rel="noopener">Workbook Handouts</a></p></details></section>
{cont}
<section class="card note"><h2 style="font-size:1.1rem">💡 Good to know</h2><ul>
<li id="local-note">Your progress saves on this device and in this browser. Use the same phone or computer each time.</li>
<li id="cloud-note" hidden>Want your progress on any device? Tap <b>☁️ Sign in</b> at the top. Make a free account with the class code from your teacher.</li>
<li>Add this site to your home screen: in Chrome, tap the menu, then "Add to Home screen". On iPhone, tap Share, then "Add to Home Screen".</li>
<li>After you open each app one time, it works offline too.</li></ul></section>
</main>
<footer><a href="teacher.html" rel="nofollow">Teacher</a></footer>
<script>window.JC_HOME={json.dumps(data, ensure_ascii=False, separators=(',', ':'))};</script>
<script>{JS}</script>
<script>if("serviceWorker" in navigator&&location.protocol.indexOf("http")===0){{addEventListener("load",function(){{navigator.serviceWorker.register("sw.js").catch(function(){{}})}})}}</script>
</body></html>
"""
    assert chr(0x2014) not in html
    open(os.path.join(SITE, 'index.html'), 'w', encoding='utf-8').write(html)
