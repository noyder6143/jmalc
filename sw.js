const CACHE='ic3-apps-v2-jmalc';
const FILES=['./','./index.html','./quest.html','./practice.html','./site.webmanifest','./quest.webmanifest','./practice.webmanifest',
'./icons/home-192.png','./icons/home-512.png','./icons/home-180.png','./icons/quest-192.png','./icons/quest-512.png','./icons/quest-180.png',
'./icons/practice-192.png','./icons/practice-512.png','./icons/practice-180.png'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
// Network first so updates show up when online; fall back to cache when offline.
self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET'||new URL(e.request.url).origin!==location.origin)return;
  e.respondWith(fetch(e.request).then(r=>{if(r.ok){const c=r.clone();caches.open(CACHE).then(x=>x.put(e.request,c));}return r;})
    .catch(()=>caches.match(e.request,{ignoreSearch:true}).then(r=>r||caches.match('./index.html'))));
});
