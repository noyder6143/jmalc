// Unit tests for the merge logic in sync.js.  Run: node tests/merge.test.js
const fs = require('fs'), vm = require('vm'), path = require('path'), assert = require('assert');
const ctx = { window: {}, console };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '..', 'sync.js'), 'utf8'), ctx);
const J = ctx.window.JCSync; let n = 0;
const eq = (a, b, m) => { assert.deepStrictEqual(JSON.parse(JSON.stringify(a)), JSON.parse(JSON.stringify(b)), m); n++; };
eq(J.enabled, false, 'no config means disabled');

// ---- Quest
const qL = { name: 'Ana', xp: 120, seen: { mobile: [0, 2] }, quiz: { mobile: 70, hardware: 90 }, qok: { 'mobile:1': 1 }, games: { 'mobile:0': 1 }, sims: {}, mission: { mobile: [true, false, false] }, badges: ['lvl_hardware'], flips: 12, days: ['2026-10-08', '2026-10-09'], boss: 0 };
const qC = { name: '', xp: 300, seen: { mobile: [1, 2], cloud: [0] }, quiz: { mobile: 85 }, qok: { 'cloud:3': 1 }, games: {}, sims: { 'cloud:0': 1 }, mission: { mobile: [false, true], boss: [true] }, badges: ['lvl_mobile', 'lvl_hardware'], flips: 40, days: ['2026-10-01', '2026-10-09'], boss: 65 };
const q = J.merge.quest(qL, qC);
eq(q.name, 'Ana', 'local name kept'); eq(q.xp, 300, 'xp max'); eq(q.flips, 40, 'flips max'); eq(q.boss, 65, 'boss max');
eq(q.quiz, { mobile: 85, hardware: 90 }, 'quiz per-level max');
eq(q.qok, { 'mobile:1': 1, 'cloud:3': 1 }, 'qok union'); eq(q.sims, { 'cloud:0': 1 }, 'sims union'); eq(q.games, { 'mobile:0': 1 }, 'games union');
eq(q.seen, { mobile: [0, 1, 2], cloud: [0] }, 'seen union per level');
eq(q.mission, { mobile: [true, true, false], boss: [true] }, 'mission steps OR by position');
eq(q.badges.slice().sort(), ['lvl_hardware', 'lvl_mobile'], 'badges union');
eq(q.days, ['2026-10-01', '2026-10-08', '2026-10-09'], 'days union sorted');
eq(J.merge.quest(qL, null), J.merge.quest(qL, {}), 'null cloud ok');
eq(J.merge.quest(null, qC).xp, 300, 'null local ok');
eq(J.merge.quest(q, q), q, 'merge is idempotent');
eq(J.merge.quest(qL, qC), J.merge.quest(J.merge.quest(qL, qC), qC), 'remerge stable');
const days = []; for (let i = 1; i <= 70; i++) days.push('2026-08-' + String(i).padStart(2, '0'));
eq(J.merge.quest({ days: days.slice(0, 40) }, { days: days.slice(30) }).days.length, 60, 'days capped at 60');

// ---- Practice
const h = (date, test, pct, mode) => ({ date, test, name: test, mode: mode || 'test', c: pct, n: 100, pct });
const pL = { best: { 'tt_br:test': 70, 'final:test': 82 }, stats: { a: { c: 1, n: 3 }, b: { c: 2, n: 2 } }, missed: { a: 2, c: 1 }, history: [h('2026-10-02T10:00:00Z', 'tt_br', 70), h('2026-10-03T10:00:00Z', 'final', 82)] };
const pC = { best: { 'tt_br:test': 90, 'o16_pe1:train': 60 }, stats: { a: { c: 3, n: 5 }, c: { c: 0, n: 1 } }, missed: { b: 1 }, history: [h('2026-10-01T10:00:00Z', 'tt_sec', 50), h('2026-10-02T10:00:00Z', 'tt_br', 70)] };
const p = J.merge.practice(pL, pC);
eq(p.best, { 'tt_br:test': 90, 'final:test': 82, 'o16_pe1:train': 60 }, 'best per key max');
eq(p.stats, { a: { c: 3, n: 5 }, b: { c: 2, n: 2 }, c: { c: 0, n: 1 } }, 'stats max');
// a: missed locally only, cloud practiced it more (n 5 > 3) and fixed it -> dropped. b: missed in cloud only, local practiced more (2 > 0) -> dropped. c: missed locally, cloud n=1 = local n 0? local has no stats(0) < 1 -> dropped
eq(p.missed, {}, 'missed deck drops items fixed on the device that practiced more');
eq(J.merge.practice({ missed: { a: 2 }, stats: { a: { n: 3 } } }, { missed: { a: 1 }, stats: { a: { n: 4 } } }).missed, { a: 2 }, 'missed on both sides kept (max count)');
eq(J.merge.practice({ missed: { z: 1 }, stats: { z: { n: 2 } } }, {}).missed, { z: 1 }, 'local-only missed kept when cloud never saw it');
eq(p.history.map(x => x.date), ['2026-10-01T10:00:00Z', '2026-10-02T10:00:00Z', '2026-10-03T10:00:00Z'], 'history union, dedupe, sorted');
const big = []; for (let i = 0; i < 350; i++) big.push(h(new Date(Date.UTC(2026, 0, 1) + i * 6e4).toISOString(), 't', 1));
eq(J.merge.practice({ history: big.slice(0, 200) }, { history: big.slice(150) }).history.length, 300, 'history capped at 300');
eq(J.merge.practice(p, p), p, 'practice merge idempotent');

// ---- summary + attempts
eq(J.summary('quest', q), { xp: 300, best: { quiz: q.quiz, boss: 65, badges: 2 } }, 'quest summary');
eq(J.summary('practice', p).best, p.best, 'practice summary');
const fin = Object.assign(h('2026-10-05T10:00:00Z', 'final', 80), { c: 36, n: 45, byd: { 1: { c: 5, n: 6 } } });
eq(J.attemptRows([pL.history[0], fin], '2026-10-04T00:00:00Z'), [{ test_id: 'final', test_name: 'final', mode: 'test', score: 36, total: 45, by_domain: { 1: { c: 5, n: 6 } }, taken_at: '2026-10-05T10:00:00Z' }], 'attempt rows after watermark');
eq(J.attemptRows([pL.history[0]], '').length, 1, 'all rows with empty watermark');
console.log('merge tests: ' + n + ' passed');
