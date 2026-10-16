"""Write games.html: tap-based, self-scoring chapter games (games.html#ch=N lists a chapter's games,
games.html#g=ID plays one). Best scores save in the Quest progress (cg = best %, cgp = best points,
cgs = best stars, cgn = times played) so they sync to the cloud and show on the teacher dashboard."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chapters import CHAPTERS
from games import GAMES
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPE = dict(match='Match', sort='Sort', tf='True or false', order='Put in order', scam='Spot the scam')

CSS = r"""*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;background:#f4f7fb;color:#14202e;line-height:1.45;font-size:18px}
header{background:linear-gradient(120deg,#1d3557,#0f7c83);color:#fff;padding:.8rem 1rem}
.top{max-width:760px;margin:0 auto;display:flex;align-items:center;gap:.6rem;flex-wrap:wrap}.brand{flex:1;font-weight:800;min-width:11rem}.brand a{color:#fff;text-decoration:none}
#acct .jcs-chip{font-size:.95rem;min-height:44px;padding:.5em 1em}
nav.chnav{background:#fff;box-shadow:0 2px 10px rgba(20,32,46,.12);padding:.45rem;display:flex;gap:.35rem;overflow-x:auto;justify-content:safe center}
nav.chnav a{flex:0 0 auto;padding:.5rem .8rem;border-radius:999px;background:#eef3f8;color:#1d3557;font-weight:700;text-decoration:none;font-size:.92rem;min-height:40px}
nav.chnav a.on{background:#0f7c83;color:#fff}
main{max-width:760px;margin:1rem auto 2rem;padding:0 .8rem}
.card{background:#fff;border-radius:18px;padding:1.1rem;box-shadow:0 6px 20px rgba(20,32,46,.1);margin-bottom:1rem}
h1{font-size:1.5rem;margin:.1rem 0 .4rem;color:#1d3557}h2{font-size:1.25rem;margin:0 0 .3rem;color:#1d3557}
.muted{color:#5c6b7c}.small{font-size:.92rem}
a.back,button,.btn{font:inherit;font-weight:800;border:0;border-radius:14px;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;gap:.3rem;min-height:48px;padding:.6rem 1rem}
a.back{background:#fff;color:#1d3557;border:2px solid #c9d4e1;min-height:44px}
.gl{display:grid;gap:.8rem}.gi{display:flex;gap:.8rem;align-items:center}.gi .ic{font-size:2.3rem}.gi .tx{flex:1}.gi .stars{font-size:1.2rem;letter-spacing:.05em}
.play{background:#ffcc33;color:#1a1a1a;min-width:7rem;min-height:56px;font-size:1.1rem}
.hud{position:sticky;top:0;z-index:4;display:flex;gap:.5rem;justify-content:space-between;align-items:center;background:#1d3557;color:#fff;border-radius:14px;padding:.55rem .8rem;margin-bottom:.8rem;font-weight:800}
.hud span{white-space:nowrap}.hud .x{background:rgba(255,255,255,.15);color:#fff;min-height:40px;padding:.3rem .7rem;font-size:.9rem}
.bar{height:10px;background:#e6ebf2;border-radius:999px;overflow:hidden;margin:-.3rem 0 .8rem}.bar i{display:block;height:100%;background:#2ecc71;width:0;transition:width .3s}
.cols{display:grid;grid-template-columns:1fr 1fr;gap:.5rem}.cols>div{display:grid;gap:.5rem;align-content:start}
.tile{background:#fff;border:2px solid #c9d4e1;color:#14202e;font-weight:700;min-height:64px;padding:.5rem .6rem;font-size:.98rem;line-height:1.25;text-align:center;width:100%}
.tile.def{font-weight:600;font-size:.92rem}.tile.sel{border-color:#0f7c83;background:#e3f4f5;box-shadow:0 0 0 3px #9fd3d6}
.tile.ok{background:#e9f9ef;border-color:#2ecc71;color:#1d6b3f;opacity:.75}.tile.bad{animation:shake .35s;border-color:#e74c3c;background:#fdecea}
@keyframes shake{25%{transform:translateX(-6px)}75%{transform:translateX(6px)}}
.item{background:#fff;border:3px solid #1d3557;border-radius:18px;padding:1.2rem;text-align:center;font-size:1.35rem;font-weight:800;min-height:120px;display:flex;align-items:center;justify-content:center;margin-bottom:.8rem}
.msg{text-align:left;font-size:1rem;font-weight:500;display:block;border-color:#0f7c83}.msg .from{font-size:.85rem;color:#5c6b7c}.msg .sub{font-weight:800;margin:.2rem 0}
.cats{display:grid;gap:.6rem}.cats.c2{grid-template-columns:1fr 1fr}.cats button{background:#0f7c83;color:#fff;min-height:64px;font-size:1.08rem}
.cats button:nth-child(2){background:#1d3557}.cats button:nth-child(3){background:#7a4fb5}.cats button:nth-child(4){background:#b5651d}
.fb{border-radius:14px;padding:.8rem;margin:.7rem 0 0;font-weight:600;min-height:3rem}.fb.ok{background:#e9f9ef;color:#1d6b3f}.fb.no{background:#fdecea;color:#8a1626}
.next{background:#ffcc33;color:#1a1a1a;width:100%;margin-top:.6rem;min-height:56px;font-size:1.1rem}
.picked{display:grid;gap:.4rem;margin-bottom:.8rem;counter-reset:s}.picked div{background:#e9f9ef;border:2px solid #2ecc71;border-radius:12px;padding:.5rem .7rem;font-weight:700;counter-increment:s}
.picked div::before{content:counter(s) ". "}.pool{display:grid;gap:.5rem}
.res{text-align:center}.res .big{font-size:3rem;letter-spacing:.1em}.res .nums{display:grid;grid-template-columns:repeat(3,1fr);gap:.5rem;margin:1rem 0}.res .nums div{background:#f4f7fb;border-radius:12px;padding:.6rem}.res .nums b{display:block;font-size:1.4rem;color:#1d3557}
.res .acts{display:grid;gap:.5rem}.again{background:#0f7c83;color:#fff}.nextg{background:#ffcc33;color:#1a1a1a}.quiz{background:#1d3557;color:#fff}
.newbest{display:inline-block;background:#2ecc71;color:#073b1d;border-radius:999px;padding:.2rem .8rem;font-weight:800}
footer{text-align:center;padding:0 1rem 2rem;font-size:.85rem;color:#7a8796}footer a{color:#5c6b7c}
button:focus-visible,a:focus-visible{outline:3px solid #ffcc33;outline-offset:2px}
@media (max-width:520px){.gi{flex-wrap:wrap}.gi .tx{flex:1 1 calc(100% - 3.5rem)}.gi .play{flex:1 1 100%}}"""

JS = r"""(function(){var D=window.JC_GAMES,G=D.games,$=function(s){return document.querySelector(s)},app=$('#app'),QK='ic3quest_v1',T=null,S=null;
function esc(t){return String(t==null?'':t).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function shuf(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a}
function qget(){try{return JSON.parse(localStorage.getItem(QK))||{}}catch(e){return {}}}
function best(id){var s=qget();return {acc:(s.cg||{})[id],pts:(s.cgp||{})[id],stars:(s.cgs||{})[id]||0,n:(s.cgn||{})[id]||0}}
function save(id,acc,pts,stars){var s=qget();['cg','cgp','cgs','cgn'].forEach(function(k){if(!s[k]||typeof s[k]!=='object'||Array.isArray(s[k]))s[k]={}});
 var old=best(id);s.cg[id]=Math.max(s.cg[id]||0,acc);s.cgp[id]=Math.max(s.cgp[id]||0,pts);s.cgs[id]=Math.max(s.cgs[id]||0,stars);s.cgn[id]=(s.cgn[id]||0)+1;
 try{localStorage.setItem(QK,JSON.stringify(s))}catch(e){}if(window.JCSync)JCSync.changed('quest');return old}
function stars(n){var o='';for(var i=0;i<3;i++)o+=i<n?'⭐':'☆';return o}
function chOf(){var m=/ch=(\d)/.exec(location.hash);return m?+m[1]:1}
function nav(n){[].forEach.call(document.querySelectorAll('nav.chnav a'),function(a){a.classList.toggle('on',+a.dataset.ch===n)})}
function stop(){if(T){clearInterval(T);T=null}}
function route(){stop();var m=/g=(\w+)/.exec(location.hash);if(m){var g=G.filter(function(x){return x.id===m[1]})[0];if(g)return start(g)}list(chOf())}
function list(n){var c=D.chapters.filter(function(x){return x.n===n})[0]||D.chapters[0];nav(c.n);scrollTo(0,0);
 document.title='Chapter '+c.n+' Games · Jmal C\'s Digital Literacy Class';
 var gs=G.filter(function(g){return g.ch===c.n});
 app.innerHTML='<div class="card"><h1>'+c.icon+' Chapter '+c.n+' Games</h1><p class="muted" style="margin:0">'+esc(c.title)+'. Quick games to practice. Get points and up to 3 stars. Your best score is saved.</p></div><div class="gl">'+
  gs.map(function(g){var b=best(g.id);return '<div class="card gi" id="gc_'+g.id+'"><span class="ic" aria-hidden="true">'+g.icon+'</span><div class="tx"><h2>'+esc(g.title)+'</h2><div class="small muted">'+esc(D.types[g.type])+' · '+esc(g.intro)+'</div>'+
   '<div class="stars" aria-label="Best '+b.stars+' of 3 stars">'+stars(b.stars)+(b.n?' <span class="small muted">Best '+b.pts+' points · played '+b.n+'x</span>':' <span class="small muted">Not played yet</span>')+'</div></div><a class="btn play" href="#g='+g.id+'">▶ Play</a></div>'}).join('')+
  '</div><div class="card small"><a href="chapters.html#ch='+c.n+'">📖 Read the Chapter '+c.n+' summary</a> · <a href="quest.html#ch='+c.n+'">🎮 Quest lessons</a> · <a href="practice.html#chapter='+c.n+'">📝 Chapter '+c.n+' Quiz</a></div>';
 window.__games.view='list'}
function hud(){var t=Math.floor((Date.now()-S.t0)/1000);$('#tm').textContent='⏱ '+t+'s';$('#pt').textContent='⭐ '+S.pts;$('#pg').textContent=S.done+' / '+S.total;$('#pb i').style.width=(100*S.done/S.total)+'%'}
function start(g){nav(g.ch);scrollTo(0,0);document.title=g.title+' · Chapter '+g.ch+' Games';
 S={g:g,t0:Date.now(),pts:0,done:0,ok:0,total:0,miss:{}};
 app.innerHTML='<div class="hud" role="status"><a class="btn x" href="#ch='+g.ch+'" aria-label="Quit game">✕</a><span id="pg"></span><span id="pt"></span><span id="tm"></span></div><div class="bar" id="pb"><i></i></div>'+
  '<div class="card"><h1>'+g.icon+' '+esc(g.title)+'</h1><p class="muted" style="margin:0 0 .8rem">'+esc(g.intro)+'</p><div id="gm"></div></div>';
 ({match:match,sort:sort,tf:sort,scam:sort,order:order})[g.type](g);hud();T=setInterval(hud,250);window.__games.view='play';window.__games.S=S}
function match(g){var P=shuf(g.pairs).slice(0,6);S.total=P.length;var L=shuf(P.map(function(p,i){return [i,p[0]]})),R=shuf(P.map(function(p,i){return [i,p[1]]})),sel={l:null,r:null};
 $('#gm').innerHTML='<div class="cols"><div>'+L.map(function(x){return '<button class="tile" data-s="l" data-i="'+x[0]+'">'+esc(x[1])+'</button>'}).join('')+'</div><div>'+R.map(function(x){return '<button class="tile def" data-s="r" data-i="'+x[0]+'">'+esc(x[1])+'</button>'}).join('')+'</div></div><div class="fb" id="fb" aria-live="polite"></div>';
 [].forEach.call(document.querySelectorAll('#gm .tile'),function(b){b.onclick=function(){if(b.classList.contains('ok'))return;var s=b.dataset.s;
  if(sel[s])sel[s].classList.remove('sel');sel[s]=b;b.classList.add('sel');
  if(sel.l&&sel.r){var a=sel.l,c=sel.r,i=a.dataset.i;if(i===c.dataset.i){[a,c].forEach(function(x){x.classList.remove('sel');x.classList.add('ok');x.disabled=true});
    var first=!S.miss[i];S.pts+=first?10:5;if(first)S.ok++;S.done++;$('#fb').className='fb ok';$('#fb').textContent='✅ '+P[i][0]+': '+P[i][1];hud();if(S.done===S.total)setTimeout(finish,600)}
   else{S.miss[a.dataset.i]=1;[a,c].forEach(function(x){x.classList.remove('sel');x.classList.add('bad');setTimeout(function(){x.classList.remove('bad')},400)});$('#fb').className='fb no';$('#fb').textContent='❌ Not a match. Try again.'}
   sel={l:null,r:null}}}})}
function sort(g){var cats=g.type==='tf'?['✅ True','❌ False']:g.type==='scam'?['🎣 Scam','✅ Legit']:g.cats;
 var items=shuf(g.items).map(function(x){if(g.type==='tf')return {html:esc(x[0]),a:x[1]?0:1,why:x[2]};if(g.type==='scam')return {html:'<div class="from">From: '+esc(x[0])+'</div><div class="sub">'+esc(x[1])+'</div><div>'+esc(x[2])+'</div>',a:x[3]?0:1,why:x[4],msg:1};return {html:esc(x[0]),a:x[1],why:x[2]}});
 S.total=items.length;var k=0;
 function show(){var it=items[k];$('#gm').innerHTML='<div class="item'+(it.msg?' msg':'')+'" id="it">'+it.html+'</div><div class="cats'+(cats.length===2?' c2':'')+'">'+cats.map(function(c,i){return '<button data-c="'+i+'">'+esc(c)+'</button>'}).join('')+'</div><div id="fbw"></div>';
  [].forEach.call(document.querySelectorAll('#gm .cats button'),function(b){b.onclick=function(){var ok=+b.dataset.c===it.a;[].forEach.call(document.querySelectorAll('#gm .cats button'),function(x){x.disabled=true;if(+x.dataset.c!==it.a)x.style.opacity=.45});
   S.done++;if(ok){S.ok++;S.pts+=10}hud();
   $('#fbw').innerHTML='<div class="fb '+(ok?'ok':'no')+'" aria-live="polite">'+(ok?'✅ Correct! ':'❌ It is <b>'+esc(cats[it.a])+'</b>. ')+esc(it.why)+'</div><button class="next" id="nx">'+(k<items.length-1?'Next ➜':'See my score ➜')+'</button>';
   $('#nx').onclick=function(){k++;if(k<items.length)show();else finish()};$('#nx').focus()}})}
 show()}
function order(g){var st=g.steps,pool=shuf(st.map(function(s,i){return [i,s]})),nxt=0;S.total=st.length;
 $('#gm').innerHTML='<div class="small muted" style="margin-bottom:.4rem">Your order:</div><div class="picked" id="pk"></div><div class="small muted" style="margin-bottom:.4rem">Tap the next step:</div><div class="pool" id="pl">'+pool.map(function(x){return '<button class="tile" data-i="'+x[0]+'">'+esc(x[1])+'</button>'}).join('')+'</div><div class="fb" id="fb" aria-live="polite"></div>';
 [].forEach.call(document.querySelectorAll('#pl .tile'),function(b){b.onclick=function(){var i=+b.dataset.i;if(i===nxt){var first=!S.miss[i];S.pts+=first?10:5;if(first)S.ok++;S.done++;nxt++;
   var d=document.createElement('div');d.textContent=st[i];$('#pk').appendChild(d);b.remove();$('#fb').className='fb ok';$('#fb').textContent='✅ Good!';hud();if(nxt===st.length){$('#fb').textContent='✅ '+(g.done||'All in order!');setTimeout(finish,900)}}
  else{S.miss[nxt]=1;b.classList.add('bad');setTimeout(function(){b.classList.remove('bad')},400);$('#fb').className='fb no';$('#fb').textContent='❌ Not yet. Which step comes next?'}}})}
function finish(){stop();var g=S.g,t=Math.max(1,Math.round((Date.now()-S.t0)/1000)),acc=Math.round(100*S.ok/S.total),bonus=t<=g.par?20:t<=g.par*1.5?10:0,pts=S.pts+bonus;
 var st=acc>=90&&t<=g.par*1.5?3:acc>=70?2:1,old=save(g.id,acc,pts,st),nb=!old.n||pts>(old.pts||0);
 var gs=G.filter(function(x){return x.ch===g.ch}),ix=gs.indexOf(g),nx=gs[ix+1];
 app.innerHTML='<div class="card res" id="res"><h1>'+(st===3?'🎉 Amazing!':st===2?'👏 Good job!':'💪 Keep practicing!')+'</h1><div class="big" aria-label="'+st+' of 3 stars">'+stars(st)+'</div>'+(nb?'<div class="newbest">New best score!</div>':'')+
  '<div class="nums"><div><b id="rp">'+pts+'</b>points</div><div><b>'+acc+'%</b>right first time</div><div><b>'+t+'s</b>time</div></div>'+
  '<p class="small muted">'+(bonus?'Includes a time bonus of '+bonus+' points. ':'Finish in '+g.par+' seconds for a time bonus. ')+'3 stars: 90% or more right, and fast.</p>'+
  '<div class="acts"><a class="btn again" href="#g='+g.id+'&r='+Date.now()+'">🔁 Play again</a>'+(nx?'<a class="btn nextg" href="#g='+nx.id+'">▶ Next game: '+esc(nx.title)+'</a>':'<a class="btn nextg" href="practice.html#chapter='+g.ch+'">📝 Take the Chapter '+g.ch+' Quiz</a>')+'<a class="btn back" href="#ch='+g.ch+'">← All Chapter '+g.ch+' games</a></div></div>';
 window.__games.view='result';window.__games.last={id:g.id,pts:pts,acc:acc,stars:st,t:t};scrollTo(0,0)}
window.__games={data:D,finish:function(){finish()},view:''};
addEventListener('hashchange',route);route();
if(window.JCSync&&JCSync.enabled){JCSync.attach({mount:'#acct'});JCSync.onAuth(function(){if(window.__games.view==='list')list(chOf())})}})();"""

def build():
    data = dict(types=TYPE, chapters=[dict(n=c['n'], title=c['title'], icon=c['icon']) for c in CHAPTERS], games=GAMES)
    nav = ''.join(f'<a href="#ch={c["n"]}" data-ch="{c["n"]}">{c["icon"]} Ch {c["n"]}</a>' for c in CHAPTERS)
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chapter Games · Jmal C's Digital Literacy Class</title>
<link rel="manifest" href="site.webmanifest"><meta name="theme-color" content="#1d3557">
<link rel="icon" href="icons/home-192.png"><link rel="apple-touch-icon" href="icons/home-180.png">
<script src="config.js"></script><script src="sync.js"></script>
<style>{CSS}</style></head><body>
<header><div class="top"><div class="brand"><a href="index.html">Jmal C's Digital Literacy Class</a><div class="small" style="font-weight:600;opacity:.9">🎲 Chapter Games</div></div><div id="acct"></div></div></header>
<nav class="chnav" aria-label="Chapters">{nav}</nav>
<main><div style="margin-bottom:.8rem"><a class="back" href="index.html">← Home</a></div><div id="app"></div></main>
<footer><a href="index.html">Home</a> · <a href="chapters.html#ch=1">Chapter Summaries</a> · <a href="quest.html">Quest</a> · <a href="practice.html">Practice Lab</a></footer>
<script>window.JC_GAMES={json.dumps(data, ensure_ascii=False, separators=(',', ':'))};</script>
<script>{JS}</script>
<script>if("serviceWorker" in navigator&&location.protocol.indexOf("http")===0){{addEventListener("load",function(){{navigator.serviceWorker.register("sw.js").catch(function(){{}})}})}}</script>
</body></html>
"""
    assert chr(0x2014) not in html
    open(os.path.join(SITE, 'games.html'), 'w', encoding='utf-8').write(html)
    return {c['n']: [g['id'] for g in GAMES if g['ch'] == c['n']] for c in CHAPTERS}

if __name__ == '__main__':
    print(build())
