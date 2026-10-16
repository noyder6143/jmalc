"""Build ready-to-import files for free apps (Kahoot, Blooket, Gimkit, Wayground, Quizlet, Wordwall, Padlet, Mentimeter)
for Chapters 1-7, plus the Free Apps Activity Guide (DOCX + PDF) and a zip. Formats follow each app's official template."""
import os, sys, csv, random, shutil, zipfile, subprocess, re
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import openpyxl
from games import GAMES
from summaries import SUMMARIES
from activities import A
from free_apps import CH, EXTRA, MAP, WAYGROUND_OPEN, PADLET, MENTI, WORDWALL
OUT = '/workspace/BCC_IC3_Class/Free_App_Activities'
TPL = os.path.join(OUT, '_templates')
BRAND = "Jmal C's Digital Literacy Class"
strip = lambda s: re.sub(r'^[^\w(]+', '', s).strip()

def bank(n):
    rnd = random.Random(n); Q = []
    gs = [g for g in GAMES if g['ch'] == n]
    for g in gs:
        if g['type'] == 'match':
            terms = [a for a, b in g['pairs']]
            for a, b in g['pairs']:
                Q.append(dict(q=f"Which word means: {b}?", o=[a] + rnd.sample([t for t in terms if t != a], 3), why=f"{a}: {b}.", src=g['id']))
        elif g['type'] == 'sort':
            cats = [strip(c) for c in g['cats']]
            for it, ci, why in g['items']:
                Q.append(dict(q=f"{it}: which group?" if len(cats) > 2 else f"{it}: which group?", o=[cats[ci]] + [c for j, c in enumerate(cats) if j != ci], why=why, src=g['id']))
        elif g['type'] == 'tf':
            for s, ans, why in g['items']:
                Q.append(dict(q=f"True or false: {s}", o=['True', 'False'] if ans else ['False', 'True'], why=why, src=g['id'], tf=True))
        elif g['type'] == 'scam':
            for snd, subj, body, scam, why in g['items']:
                Q.append(dict(q=f"Scam or legit? From {snd}: \"{body}\"", o=['Scam', 'Legit'] if scam else ['Legit', 'Scam'], why=why, src=g['id'], tf=True))
        elif g['type'] == 'order':
            st = g['steps']
            for i in range(len(st) - 1):
                Q.append(dict(q=f"What comes right after \"{st[i]}\"?", o=[st[i + 1]] + rnd.sample([s for s in st if s not in (st[i], st[i + 1])], 3), why=g.get('done', ''), src=g['id']))
    for q, o, why in EXTRA[n]:
        Q.append(dict(q=q, o=list(o), why=why, src='extra'))
    vocab = SUMMARIES[n]['vocab']; terms = [a for a, b in vocab]
    for a, b in vocab:
        Q.append(dict(q=f"What does \"{a}\" mean?", o=[b] + [x[1] for x in rnd.sample([v for v in vocab if v[0] != a], 3)], why=f"{a}: {b}.", src='vocab'))
    return Q

def fits(q, qmax=120, amax=75): return len(q['q']) <= qmax and all(len(o) <= amax for o in q['o'])

def pick(n, k, qmax=None, amax=None, seed=0):
    Q = bank(n); rnd = random.Random(100 * n + seed)
    if qmax: Q = [q for q in Q if fits(q, qmax, amax)]
    # spread across sources: extras first, then round-robin by source
    by = {}
    for q in Q: by.setdefault(q['src'], []).append(q)
    for v in by.values(): rnd.shuffle(v)
    order = ['extra'] + [s for s in by if s not in ('extra', 'vocab')] + ['vocab']
    out = list(by.get('extra', []))
    while len(out) < k and any(by.get(s) for s in order[1:]):
        for s in order[1:]:
            if by.get(s) and len(out) < k: out.append(by[s].pop())
    out = out[:k]; rnd.shuffle(out)
    res = []
    for q in out:
        o = q['o'][:]; c = o[0]
        if q.get('tf'): o = ['True', 'False'] if 'True' in o else ['Scam', 'Legit']
        else: rnd.shuffle(o)
        res.append(dict(q=q['q'], o=o, c=o.index(c) + 1, why=q['why']))
    return res

def title(n): return f"Jmal C IC3 Ch {n}: {CH[n]}"
def desc(n): return f"{BRAND}. Chapter {n} review game ({CH[n]}). Original questions for adult learners."

def kahoot(n, d):
    qs = pick(n, 15, 120, 75)
    wb = openpyxl.load_workbook(os.path.join(TPL, 'Kahoot_Quiz_Import_Template_official.xlsx')); ws = wb.active
    for r in range(9, 209):
        for col in 'BCDEFGH': ws[f'{col}{r}'].value = None
    for i, q in enumerate(qs):
        r = 9 + i; ws[f'B{r}'] = q['q']
        for j, o in enumerate(q['o']): ws[f'{"CDEF"[j]}{r}'] = o
        ws[f'G{r}'] = 20; ws[f'H{r}'] = q['c']
    p = os.path.join(d, f'Kahoot_Ch{n}_{CH[n].replace(" ", "_")}.xlsx'); wb.save(p); return p, qs

def blooket(n, d):
    qs = pick(n, 24)
    p = os.path.join(d, f'Blooket_Ch{n}_{CH[n].replace(" ", "_")}.csv')
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Blooket\nImport Template', '', '', '', '', '', '', ''])
        w.writerow(['Question #', 'Question Text', 'Answer 1', 'Answer 2', 'Answer 3\n(Optional)', 'Answer 4\n(Optional)', 'Time Limit (sec)\n(Max: 300 seconds)', 'Correct Answer(s)\n(Only include Answer #)'])
        for i, q in enumerate(qs, 1):
            o = q['o'] + [''] * (4 - len(q['o']))
            w.writerow([i, q['q'], *o, 20, q['c']])
    return p, qs

def gimkit(n, d):
    qs = pick(n, 24, seed=7)
    p = os.path.join(d, f'Gimkit_Ch{n}_{CH[n].replace(" ", "_")}.csv')
    with open(p, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['Gimkit Spreadsheet Import Template', '', '', '', ''])
        w.writerow(['Question', 'Correct Answer', 'Incorrect Answer 1', 'Incorrect Answer 2', 'Incorrect Answer 3'])
        for q in qs:
            c = q['o'][q['c'] - 1]; wrong = [o for o in q['o'] if o != c]
            w.writerow([q['q'], c] + wrong + [''] * (3 - len(wrong)))
    return p, qs

def wayground(n, d):
    qs = pick(n, 15, seed=3)
    wb = openpyxl.load_workbook(os.path.join(TPL, 'Wayground_Import_Template_official.xlsx')); ws = wb.active
    for r in range(3, 1001):
        for col in 'ABCDEFGHIJK': ws[f'{col}{r}'].value = None
    rows = [[q['q'], 'Multiple Choice', *(q['o'] + [None] * (5 - len(q['o']))), q['c'], 30, None, q['why']] for q in qs]
    if n in WAYGROUND_OPEN: rows.append([WAYGROUND_OPEN[n], 'Open-Ended', None, None, None, None, None, None, 180, None, None])
    for i, row in enumerate(rows):
        for j, v in enumerate(row): ws.cell(row=3 + i, column=1 + j, value=v)
    p = os.path.join(d, f'Wayground_Ch{n}_{CH[n].replace(" ", "_")}.xlsx'); wb.save(p); return p, rows

def quizlet(n, d):
    seen, rows = set(), []
    for a, b in SUMMARIES[n]['vocab']:
        if a.lower() not in seen: seen.add(a.lower()); rows.append((a, b))
    for g in GAMES:
        if g['ch'] == n and g['type'] == 'match':
            for a, b in g['pairs']:
                if a.lower() not in seen and not any(a.lower() in s for s in seen): seen.add(a.lower()); rows.append((a, b))
    p = os.path.join(d, f'Quizlet_Ch{n}_{CH[n].replace(" ", "_")}.txt')
    with open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(f'{a}\t{b}' for a, b in rows) + '\n')
    return p, rows

def wordwall(ww, d):
    g = next(x for x in GAMES if x['id'] == ww['game'])
    L = [f"WORDWALL #{ww['n']} of 3 (free Basic plan allows 3)", f"Template: {ww['template']}", f"Title: {ww['title']}",
         f"Instruction: {ww['inst']}", f"Description: {BRAND}. Original review game.", '']
    if ww['template'] == 'Group sort':
        cats = [strip(c) for c in g['cats']]
        for ci, c in enumerate(cats):
            L.append(f"GROUP {ci + 1}: {c}"); L += [f"  {it}" for it, k, _ in g['items'] if k == ci]; L.append('')
    else:
        L.append('KEYWORD -> MATCHING DEFINITION (one row per pair)'); L += [f"  {a}  ->  {b}" for a, b in g['pairs']]
    p = os.path.join(d, f"Wordwall_{ww['n']}_{ww['title'].split(' (')[0].replace(' ', '_').replace('?', '')}.txt")
    open(p, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); return p

def padlet(pd, d):
    L = [f"PADLET #{pd['n']} of 3 (free Neon plan allows 3 boards)", f"Format: {pd['fmt']}", f"Title: {pd['title']}", f"Description: {pd['desc']}", '',
         'Pin this first post (teacher):', f"  {pd['prompt']}"]
    if pd['cols']: L += ['', 'Column (section) names:'] + [f'  {c}' for c in pd['cols']]
    L += ['', 'Settings: Comments ON, Reactions = Like, Approval OFF (or ON if you want to check posts first). Share > Copy link > paste in Zoom chat.']
    p = os.path.join(d, f"Padlet_{pd['n']}_{pd['title'].split(' (')[0].replace(' ', '_')}.txt"); open(p, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); return p

def menti(m, d):
    L = [f"MENTIMETER #{m['n']} of 2 (free plan: 50 participants per month in total)", f"Presentation title: {m['title']}", '']
    for i, (t, q, opts) in enumerate(m['slides'], 1):
        L.append(f"Slide {i} ({t}): {q}"); L += [f"   - {o}" for o in opts]
    p = os.path.join(d, f"Mentimeter_{m['n']}_{m['title'].split(' (')[0].replace(' ', '_').replace(':', '').replace('?', '')}.txt"); open(p, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); return p

def build():
    imp = os.path.join(OUT, 'Import_Files')
    if os.path.isdir(imp): shutil.rmtree(imp)
    files = {}
    for n in range(1, 8):
        d = os.path.join(imp, f'Ch{n}_{CH[n].replace(" ", "_")}'); os.makedirs(d)
        files[n] = dict(kahoot=kahoot(n, d), blooket=blooket(n, d), gimkit=gimkit(n, d), wayground=wayground(n, d), quizlet=quizlet(n, d))
        files[n]['wordwall'] = [wordwall(w, d) for w in WORDWALL if w['ch'] == n]
        files[n]['padlet'] = [padlet(x, d) for x in PADLET if x['ch'] == n]
        files[n]['menti'] = [menti(x, d) for x in MENTI if x['ch'] == n]
    # official blank templates for reference
    td = os.path.join(imp, '_Official_Blank_Templates'); os.makedirs(td)
    for f in ['Kahoot_Quiz_Import_Template_official.xlsx', 'Wayground_Import_Template_official.xlsx']: shutil.copy(os.path.join(TPL, f), td)
    shutil.copy(os.path.join(TPL, 'gimkit', 'Copy of Gimkit Spreadsheet Import Template - Sheet1.csv'), os.path.join(td, 'Gimkit_Import_Template_official.csv'))
    return files

if __name__ == '__main__':
    f = build()
    for n in f: print(n, {k: (len(v[1]) if isinstance(v, tuple) else len(v)) for k, v in f[n].items()})
