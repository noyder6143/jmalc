/* Jmal C's Digital Literacy Class: optional student accounts and cloud sync (Supabase).
   If config.js is empty, or Supabase cannot be reached, nothing changes:
   the apps keep saving on this device only, and they still work offline. */
(function () {
  "use strict";
  var LIB = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.117.2/dist/umd/supabase.js";
  var SRI = "sha384-Rj26LVGvoeRVR6+mwQmFfcR3QOBEwT+ZmuCWpuiqeTzJpCs0ER4ITAWGb4Hiy3Ok";
  var KEYS = { quest: "ic3quest_v1", practice: "ic3lab_v1" };
  var DEBOUNCE = 1500;

  /* ---------------- merge logic (pure, unit tested) ---------------- */
  function isObj(x) { return !!x && typeof x === "object" && !Array.isArray(x); }
  function num(a, b) { return Math.max(+a || 0, +b || 0); }
  function keys2(a, b) { var k = {}; [a, b].forEach(function (m) { if (isObj(m)) Object.keys(m).forEach(function (x) { k[x] = 1; }); }); return Object.keys(k); }
  function union(a, b) {
    var out = [], seen = {};
    [a, b].forEach(function (arr) { (Array.isArray(arr) ? arr : []).forEach(function (v) { var id = typeof v + ":" + JSON.stringify(v); if (!seen[id]) { seen[id] = 1; out.push(v); } }); });
    return out;
  }
  function maxMap(a, b) {
    var o = {};
    keys2(a, b).forEach(function (k) {
      var x = isObj(a) ? a[k] : undefined, y = isObj(b) ? b[k] : undefined;
      if (x == null) o[k] = y; else if (y == null) o[k] = x;
      else if (typeof x === "number" || typeof y === "number") o[k] = Math.max(+x || 0, +y || 0);
      else o[k] = x || y;
    });
    return o;
  }
  function unionMap(a, b) { var o = {}; keys2(a, b).forEach(function (k) { o[k] = union(isObj(a) ? a[k] : [], isObj(b) ? b[k] : []).sort(function (p, q) { return p > q ? 1 : p < q ? -1 : 0; }); }); return o; }
  function orMap(a, b) {
    var o = {};
    keys2(a, b).forEach(function (k) {
      var x = (isObj(a) && Array.isArray(a[k])) ? a[k] : [], y = (isObj(b) && Array.isArray(b[k])) ? b[k] : [];
      var n = Math.max(x.length, y.length), r = [];
      for (var i = 0; i < n; i++) r.push(!!(x[i] || y[i]));
      o[k] = r;
    });
    return o;
  }
  function mergeQuest(L, C) {
    L = isObj(L) ? L : {}; C = isObj(C) ? C : {};
    var o = Object.assign({}, C, L);
    o.name = L.name || C.name || "";
    o.xp = num(L.xp, C.xp); o.flips = num(L.flips, C.flips); o.boss = num(L.boss, C.boss);
    o.quiz = maxMap(L.quiz, C.quiz); o.qok = maxMap(L.qok, C.qok);
    o.games = maxMap(L.games, C.games); o.sims = maxMap(L.sims, C.sims);
    o.seen = unionMap(L.seen, C.seen); o.mission = orMap(L.mission, C.mission);
    o.badges = union(L.badges, C.badges);
    o.days = union(L.days, C.days).sort().slice(-60);
    return o;
  }
  function mergePractice(L, C) {
    L = isObj(L) ? L : {}; C = isObj(C) ? C : {};
    var o = Object.assign({}, C, L);
    o.best = maxMap(L.best, C.best);
    var ls = isObj(L.stats) ? L.stats : {}, cs = isObj(C.stats) ? C.stats : {};
    o.stats = {};
    keys2(ls, cs).forEach(function (id) {
      var x = ls[id] || {}, y = cs[id] || {};
      o.stats[id] = { c: num(x.c, y.c), n: num(x.n, y.n) };
    });
    // Missed deck: keep the union, except an item one side already fixed after more practice.
    var lm = isObj(L.missed) ? L.missed : {}, cm = isObj(C.missed) ? C.missed : {};
    o.missed = {};
    keys2(lm, cm).forEach(function (id) {
      var inL = lm[id] != null, inC = cm[id] != null;
      var nL = (ls[id] || {}).n || 0, nC = (cs[id] || {}).n || 0;
      if (inL && !inC && nC > nL) return;
      if (inC && !inL && nL > nC) return;
      o.missed[id] = num(lm[id], cm[id]);
    });
    var seen = {}, h = [];
    [L.history, C.history].forEach(function (arr) {
      (Array.isArray(arr) ? arr : []).forEach(function (x) { if (!x) return; var k = x.date + "|" + x.test + "|" + x.mode; if (!seen[k]) { seen[k] = 1; h.push(x); } });
    });
    h.sort(function (p, q) { return p.date > q.date ? 1 : p.date < q.date ? -1 : 0; });
    o.history = h.slice(-300);
    return o;
  }
  var MERGE = { quest: mergeQuest, practice: mergePractice };
  function summary(app, st) {
    st = st || {};
    if (app === "quest") return { xp: Math.round(+st.xp || 0), best: { quiz: st.quiz || {}, boss: st.boss || 0, badges: (st.badges || []).length } };
    return { xp: 0, best: st.best || {} };
  }
  function attemptRows(history, after) {
    return (Array.isArray(history) ? history : []).filter(function (h) { return h && h.date && h.test && (!after || h.date > after); }).map(function (h) {
      return { test_id: String(h.test), test_name: h.name || null, mode: h.mode || "test", score: +h.c || 0, total: +h.n || 0, by_domain: h.byd || {}, taken_at: h.date };
    });
  }

  var API = {
    merge: MERGE, summary: summary, attemptRows: attemptRows, keys: KEYS,
    enabled: false, attach: function () {}, changed: function () {}, ready: function () { return Promise.resolve(null); },
    user: function () { return null; }, profile: function () { return null; }, onAuth: function () {},
    signIn: nope, signUp: nope, signOut: nope, syncNow: function () { return Promise.resolve(false); }, open: function () {}
  };
  function nope() { return Promise.resolve({ error: "Cloud accounts are not set up yet." }); }
  window.JCSync = API;

  var CFG = window.JC_CONFIG || {};
  var SB_URL = String(CFG.SUPABASE_URL || "").trim().replace(/\/+$/, "");
  var SB_KEY = String(CFG.SUPABASE_ANON_KEY || "").trim();
  if (!/^https?:\/\/[^\s]+$/.test(SB_URL) || SB_KEY.length < 20) return; // no config: device-only mode, exactly as before

  /* ---------------- cloud mode ---------------- */
  API.enabled = true;
  var sb = null, user = null, prof = null, attached = {}, timers = {}, mounts = [], listeners = [], state = "idle", lastSaved = null, readyP = null, curUid = null, pulled = false;
  function ls(k, v) { try { if (v === undefined) return localStorage.getItem(k); if (v === null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) { return null; } }
  function readLocal(app) {
    var a = attached[app]; if (a) return a.get();
    try { return JSON.parse(ls(KEYS[app])) || null; } catch (e) { return null; }
  }
  function writeLocal(app, st) {
    var a = attached[app]; if (a) { a.set(st); return; }
    ls(KEYS[app], JSON.stringify(st));
  }
  function dirty(app, v) { if (v === undefined) return ls("jcsync_dirty_" + app) === "1"; ls("jcsync_dirty_" + app, v ? "1" : null); }

  function loadLib() {
    return new Promise(function (res) {
      if (window.supabase && window.supabase.createClient) return res(window.supabase);
      if (navigator.onLine === false) return res(null);
      var s = document.createElement("script"), done = false;
      function fin() { if (!done) { done = true; res(window.supabase && window.supabase.createClient ? window.supabase : null); } }
      s.src = LIB; s.integrity = SRI; s.crossOrigin = "anonymous"; s.async = true; s.onload = fin; s.onerror = fin;
      document.head.appendChild(s); setTimeout(fin, 15000);
    });
  }
  function boot() {
    if (readyP) return readyP;
    readyP = loadLib().then(function (lib) {
      if (!lib) { setState("offline"); return null; }
      try { sb = lib.createClient(SB_URL, SB_KEY, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false, storageKey: "jc-auth" } }); }
      catch (e) { setState("offline"); return null; }
      sb.auth.onAuthStateChange(function (ev, session) { setTimeout(function () { handleSession(session); }, 0); });
      return sb.auth.getSession().then(function (r) { return handleSession(r && r.data && r.data.session); }, function () { return null; }).then(function () { return sb; });
    }).catch(function () { setState("offline"); return null; });
    return readyP;
  }
  function handleSession(session) {
    var u = session && session.user ? session.user : null, uid = u ? u.id : null;
    if (uid === curUid) return Promise.resolve();
    curUid = uid; user = u; prof = null; pulled = false;
    if (!u) { setState("idle"); emit(); return Promise.resolve(); }
    setState("syncing"); emit();
    return startSync();
  }
  var syncP = null;
  function startSync() {
    if (!user) return Promise.resolve();
    if (syncP) return syncP;
    var uid = user.id;
    return syncP = (prof ? Promise.resolve() : loadProfile()).then(function () { emit(); return pullAll(); })
      .then(function () { if (user && user.id === uid) { pulled = true; setState("ok"); } }, function () { setState("error"); }).then(function () { syncP = null; emit(); });
  }
  function loadProfile() {
    return sb.from("profiles").select("id,display_name,class_code,role").eq("id", user.id).maybeSingle().then(function (r) {
      if (r.error) throw r.error;
      if (r.data) { prof = r.data; return; }
      var md = user.user_metadata || {};
      var row = { id: user.id, display_name: String(md.display_name || "").slice(0, 40), class_code: cleanCode(md.class_code) };
      return sb.from("profiles").insert(row).then(function (r2) { if (r2.error) throw r2.error; prof = Object.assign({ role: "student" }, row); });
    });
  }
  function pullAll() {
    return sb.from("progress").select("app,data").eq("user_id", user.id).then(function (r) {
      if (r.error) throw r.error;
      var cloud = {}; (r.data || []).forEach(function (x) { cloud[x.app] = x.data; });
      var jobs = Object.keys(KEYS).map(function (app) {
        var local = readLocal(app), c = cloud[app] || null;
        if (!local && !c) return Promise.resolve();
        var merged = MERGE[app](local, c);
        if (app === "quest" && !merged.name && prof && prof.display_name) merged.name = prof.display_name.split(" ")[0].slice(0, 30);
        if (JSON.stringify(merged) !== JSON.stringify(local)) writeLocal(app, merged);
        if (JSON.stringify(merged) !== JSON.stringify(c)) return push(app, true).then(function (ok) { if (!ok) throw new Error("push failed"); });
        return app === "practice" ? pushAttempts(merged) : Promise.resolve();
      });
      return Promise.all(jobs);
    });
  }
  function push(app, force) {
    if (!sb || !user) return Promise.resolve(false);
    clearTimeout(timers[app]);
    if (!pulled && !force) return startSync().then(function () { return pulled; });
    var st = readLocal(app); if (!st) return Promise.resolve(true);
    var s = summary(app, st), uid = user.id;
    dirty(app, true);
    return sb.from("progress").upsert({ user_id: uid, app: app, data: st, xp: s.xp, best_scores: s.best }, { onConflict: "user_id,app" })
      .then(function (r) { if (r.error) throw r.error; return app === "practice" ? pushAttempts(st) : null; })
      .then(function () { if (user && user.id === uid) { dirty(app, false); lastSaved = new Date(); setState("ok"); } return true; })
      .catch(function () { setState("error"); return false; });
  }
  function pushAttempts(st) {
    var wk = "jcsync_att_" + user.id, wm = ls(wk) || "";
    var rows = attemptRows(st.history, wm);
    if (!rows.length) return Promise.resolve();
    rows.forEach(function (x) { x.user_id = user.id; });
    return sb.from("attempts").upsert(rows, { onConflict: "user_id,test_id,taken_at", ignoreDuplicates: true }).then(function (r) {
      if (r.error) throw r.error;
      ls(wk, rows.reduce(function (m, x) { return x.taken_at > m ? x.taken_at : m; }, wm));
    });
  }
  function changed(app) {
    if (!user || !KEYS[app]) return;
    dirty(app, true);
    clearTimeout(timers[app]);
    timers[app] = setTimeout(function () { push(app); }, DEBOUNCE);
  }
  function flush() { if (!user) return Promise.resolve(true); if (!pulled) return startSync().then(function () { return pulled && flush(); }); return Promise.all(Object.keys(KEYS).filter(function (a) { return dirty(a); }).map(push)).then(function (r) { return r.every(Boolean); }); }
  addEventListener("online", function () { if (!sb) { readyP = null; boot(); } else flush(); });
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") flush(); });

  function cleanCode(c) { return String(c || "").replace(/\s+/g, "").toUpperCase().slice(0, 20); }
  function friendly(e) {
    var m = String((e && (e.message || e.error_description || e)) || "");
    if (/invalid login/i.test(m)) return "That email or password is not right. Try again.";
    if (/already (registered|exists)/i.test(m)) return "That email already has an account. Tap \"I have an account\" to sign in.";
    if (/not confirmed/i.test(m)) return "Your account is waiting for email confirmation. Ask your teacher to turn off \"Confirm email\".";
    if (/password/i.test(m) && /(6|short|least)/i.test(m)) return "Your password needs at least 6 characters.";
    if (/email/i.test(m) && /invalid/i.test(m)) return "Please type a real-looking email, like name@gmail.com.";
    if (/fetch|network|failed|load|unavailable|timeout|gateway|503|502|504/i.test(m)) return "Can't reach the internet right now. Your progress still saves on this device.";
    return m || "Something went wrong. Try again.";
  }
  function signIn(email, password) {
    return boot().then(function (c) {
      if (!c) return { error: friendly("network") };
      return c.auth.signInWithPassword({ email: String(email).trim(), password: password }).then(function (r) {
        if (r.error) return { error: friendly(r.error) };
        return handleSession(r.data.session).then(function () { return { ok: true }; });
      }, function (e) { return { error: friendly(e) }; });
    });
  }
  function signUp(name, code, email, password) {
    name = String(name || "").trim().slice(0, 40); code = cleanCode(code);
    if (!name) return Promise.resolve({ error: "Type your first name." });
    if (!code) return Promise.resolve({ error: "Type the class code from your teacher." });
    if (String(password || "").length < 6) return Promise.resolve({ error: "Your password needs at least 6 characters." });
    return boot().then(function (c) {
      if (!c) return { error: friendly("network") };
      return c.auth.signUp({ email: String(email).trim(), password: password, options: { data: { display_name: name, class_code: code } } }).then(function (r) {
        if (r.error) return { error: friendly(r.error) };
        if (!r.data.session) return { error: friendly("not confirmed") };
        return handleSession(r.data.session).then(function () { return { ok: true }; });
      }, function (e) { return { error: friendly(e) }; });
    });
  }
  function signOut(skipConfirm) {
    if (!sb || !user) return Promise.resolve({ ok: true });
    if (!skipConfirm && !confirm("Sign out?\n\nYour progress is saved in your account and will be removed from this device. Sign in again anytime to get it back.")) return Promise.resolve({ cancelled: true });
    return flush().then(function (ok) {
      if (!ok) { alert("Can't reach the internet, so your newest progress is not saved to your account yet. Try signing out again when you're online."); return { error: "offline" }; }
      var uid = user.id;
      return Promise.resolve(sb.auth.signOut()).catch(function () {}).then(function () {
        Object.keys(KEYS).forEach(function (a) { ls(KEYS[a], null); dirty(a, false); });
        ls("jcsync_att_" + uid, null);
        location.reload();
        return { ok: true };
      });
    });
  }

  /* ---------------- UI: header chip + sign-in sheet ---------------- */
  function css() {
    if (document.getElementById("jcs-css")) return;
    var s = document.createElement("style"); s.id = "jcs-css";
    s.textContent = ".jcs-chip{font:inherit;font-size:.85rem;font-weight:600;cursor:pointer;border-radius:999px;padding:.3em .8em;border:1px solid rgba(255,255,255,.4);background:rgba(255,255,255,.14);color:inherit;white-space:nowrap;max-width:14em;overflow:hidden;text-overflow:ellipsis}" +
      ".jcs-chip:hover{background:rgba(255,255,255,.25)}.jcs-chip:focus-visible{outline:3px solid #ffcc33;outline-offset:2px}" +
      ".jcs-ov{position:fixed;inset:0;background:rgba(10,15,30,.55);z-index:1000;display:flex;align-items:center;justify-content:center;padding:1rem}" +
      ".jcs-box{background:#fff;color:#14202e;border-radius:18px;max-width:380px;width:100%;padding:1.2rem 1.3rem;box-shadow:0 12px 40px rgba(0,0,0,.35);font-family:system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;line-height:1.4;max-height:92vh;overflow:auto}" +
      ".jcs-box h2{margin:0 0 .3rem;font-size:1.25rem}.jcs-box p{margin:.2rem 0 .8rem;color:#46566a;font-size:.92rem}" +
      ".jcs-tabs{display:flex;gap:.3rem;margin:.6rem 0 .8rem;background:#eef2f7;border-radius:12px;padding:.25rem}.jcs-tabs button{flex:1;border:0;border-radius:9px;padding:.55em;font:inherit;font-weight:600;background:transparent;color:#2c3a4b;cursor:pointer}.jcs-tabs button.on{background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.12)}" +
      ".jcs-box label{display:block;font-size:.85rem;font-weight:600;margin:.55rem 0 .2rem}.jcs-box input{width:100%;box-sizing:border-box;font:inherit;font-size:1rem;padding:.65em .7em;border:1px solid #b9c3cf;border-radius:10px;background:#fff;color:#14202e}" +
      ".jcs-box input:focus{outline:3px solid #9fd3d6;border-color:#0f7c83}.jcs-go{width:100%;margin-top:1rem;border:0;border-radius:12px;padding:.8em;font:inherit;font-weight:700;font-size:1.05rem;background:#0f7c83;color:#fff;cursor:pointer}" +
      ".jcs-go[disabled]{opacity:.6}.jcs-link{background:none;border:0;color:#0f7c83;font:inherit;font-weight:600;cursor:pointer;padding:.4em 0;margin-top:.4rem}.jcs-err{background:#fde8ea;color:#8a1626;border-radius:10px;padding:.55em .7em;margin-top:.7rem;font-size:.9rem}" +
      ".jcs-row{display:flex;gap:.5rem;flex-wrap:wrap;margin-top:1rem}.jcs-row button{flex:1;border:1px solid #b9c3cf;border-radius:12px;padding:.7em;font:inherit;font-weight:600;background:#fff;color:#14202e;cursor:pointer}.jcs-row button.pri{background:#0f7c83;color:#fff;border-color:#0f7c83}.jcs-small{font-size:.8rem;color:#5a6a7d}";
    document.head.appendChild(s);
  }
  function esc(t) { return String(t == null ? "" : t).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function chipText() {
    if (!user) return "☁️ Sign in";
    var n = (prof && prof.display_name) || (user.email || "").split("@")[0];
    return (state === "error" ? "⚠️ " : state === "syncing" ? "🔄 " : "✅ ") + n;
  }
  function chipTitle() {
    if (!user) return "Optional: sign in to save your progress to your account";
    if (state === "error") return "Not saved to your account yet. It will try again when you're online.";
    return "Signed in. Progress saves to your account.";
  }
  function renderChips() { mounts.forEach(function (b) { b.textContent = chipText(); b.title = chipTitle(); b.setAttribute("aria-label", chipTitle()); }); }
  function setState(s) { state = s; renderChips(); }
  function emit() { renderChips(); listeners.forEach(function (f) { try { f(user, prof); } catch (e) {} }); }
  function mount(sel) {
    var host = typeof sel === "string" ? document.querySelector(sel) : sel;
    if (!host) return;
    css();
    var b = document.createElement("button"); b.type = "button"; b.className = "jcs-chip"; b.id = "jcs-chip";
    b.onclick = function () { open(); };
    host.appendChild(b); mounts.push(b); renderChips();
  }
  var ov = null;
  function close() { if (ov) { ov.remove(); ov = null; } }
  function open(tab) {
    css(); close();
    ov = document.createElement("div"); ov.className = "jcs-ov"; ov.setAttribute("role", "dialog"); ov.setAttribute("aria-modal", "true");
    ov.onclick = function (e) { if (e.target === ov) close(); };
    ov.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    var box = document.createElement("div"); box.className = "jcs-box"; ov.appendChild(box); document.body.appendChild(ov);
    if (user) {
      var t = lastSaved ? lastSaved.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) : "";
      box.innerHTML = "<h2>👋 Hi, " + esc((prof && prof.display_name) || "there") + "</h2>" +
        "<p>" + (state === "error" ? "⚠️ Your newest progress is saved on this device but not in your account yet. It will try again when you're online." : "✅ Your progress saves to your account, so you can pick up on any device.") + "</p>" +
        "<p class='jcs-small'>" + esc(user.email || "") + (prof && prof.class_code ? " · Class code " + esc(prof.class_code) : "") + (t ? " · Last saved " + esc(t) : "") + "</p>" +
        "<div class='jcs-row'><button id='jcs-sync' class='pri'>Save now</button><button id='jcs-out'>Sign out</button></div><button class='jcs-link' id='jcs-x'>Close</button>";
      box.querySelector("#jcs-x").onclick = close;
      box.querySelector("#jcs-sync").onclick = function () { var b = this; b.disabled = true; b.textContent = "Saving..."; Promise.all(Object.keys(KEYS).map(push)).then(function (r) { b.disabled = false; b.textContent = r.every(Boolean) ? "Saved ✅" : "Try again"; renderChips(); }); };
      box.querySelector("#jcs-out").onclick = function () { signOut(); };
      box.querySelector("#jcs-sync").focus();
      return;
    }
    tab = tab || "in";
    box.innerHTML = "<h2>☁️ Save your progress</h2><p>Optional. Sign in to keep your XP and scores on any device. Without an account, everything still saves on this device.</p>" +
      "<div class='jcs-tabs'><button id='jcs-tin'>I have an account</button><button id='jcs-tup'>New account</button></div>" +
      "<form id='jcs-f' novalidate><div id='jcs-upf'><label for='jcs-name'>First name</label><input id='jcs-name' autocomplete='given-name' maxlength='40'>" +
      "<label for='jcs-code'>Class code <span class='jcs-small'>(ask your teacher)</span></label><input id='jcs-code' autocapitalize='characters' autocomplete='off' maxlength='20'></div>" +
      "<label for='jcs-email'>Email</label><input id='jcs-email' type='email' autocomplete='email' inputmode='email'>" +
      "<label for='jcs-pw'>Password <span class='jcs-small' id='jcs-pwh'></span></label><input id='jcs-pw' type='password' autocomplete='current-password'>" +
      "<div id='jcs-err' class='jcs-err' hidden></div><button class='jcs-go' id='jcs-go' type='submit'></button></form><button class='jcs-link' id='jcs-x'>Not now</button>";
    var q = function (s) { return box.querySelector(s); };
    function setTab(t) {
      tab = t; q("#jcs-tin").classList.toggle("on", t === "in"); q("#jcs-tup").classList.toggle("on", t === "up");
      q("#jcs-upf").hidden = t !== "up"; q("#jcs-go").textContent = t === "up" ? "Create my account" : "Sign in";
      q("#jcs-pwh").textContent = t === "up" ? "(at least 6 characters, write it down!)" : "";
      q("#jcs-pw").setAttribute("autocomplete", t === "up" ? "new-password" : "current-password"); q("#jcs-err").hidden = true;
      (t === "up" ? q("#jcs-name") : q("#jcs-email")).focus();
    }
    q("#jcs-tin").onclick = function () { setTab("in"); }; q("#jcs-tup").onclick = function () { setTab("up"); };
    q("#jcs-x").onclick = close;
    q("#jcs-f").onsubmit = function (e) {
      e.preventDefault();
      var go = q("#jcs-go"), err = q("#jcs-err"), email = q("#jcs-email").value, pw = q("#jcs-pw").value;
      err.hidden = true;
      if (!/^\S+@\S+\.\S+$/.test(email.trim())) { err.textContent = "Please type your email, like name@gmail.com."; err.hidden = false; return; }
      if (!pw) { err.textContent = "Type your password."; err.hidden = false; return; }
      go.disabled = true; go.textContent = "One moment...";
      var p = tab === "up" ? signUp(q("#jcs-name").value, q("#jcs-code").value, email, pw) : signIn(email, pw);
      p.then(function (r) {
        if (r && r.ok) { close(); return; }
        go.disabled = false; setTab(tab); err.textContent = (r && r.error) || "Something went wrong. Try again."; err.hidden = false;
      });
    };
    setTab(tab);
  }

  /* ---------------- public API ---------------- */
  API.attach = function (o) {
    if (!o) return;
    if (o.app && KEYS[o.app]) attached[o.app] = o;
    if (o.mount) mount(o.mount);
    boot();
  };
  API.changed = changed;
  API.ready = boot;
  API.user = function () { return user; };
  API.profile = function () { return prof; };
  API.client = function () { return sb; };
  API.onAuth = function (f) { listeners.push(f); if (readyP) readyP.then(function () { try { f(user, prof); } catch (e) {} }); };
  API.signIn = signIn; API.signUp = signUp; API.signOut = signOut; API.open = open;
  API.syncNow = function () { return Promise.all(Object.keys(KEYS).map(push)).then(function (r) { return r.every(Boolean); }); };
  API._state = function () { return state; };
})();
