"""Free App Versions: import files match each app's official template, content is original (9-word check), no em dashes.
Run: python3 tests/free_apps_test.py"""
import os, sys, re, glob, csv, zipfile, subprocess
import openpyxl
OUT = '/workspace/BCC_IC3_Class/Free_App_Activities'; IMP = os.path.join(OUT, 'Import_Files'); TPL = os.path.join(OUT, '_templates')
fails = []
def check(c, m): print(('PASS ' if c else 'FAIL ') + m); c or fails.append(m)
W = lambda t: re.findall(r"[a-z0-9]+", t.lower().replace('\u2019', "'").replace("'", ''))
def grams(ws, k=9): return {' '.join(ws[i:i + k]) for i in range(len(ws) - k + 1)}
chs = sorted(d for d in glob.glob(IMP + '/Ch*'))
check(len(chs) == 7, '7 chapter folders')
# Kahoot
kt = openpyxl.load_workbook(os.path.join(TPL, 'Kahoot_Quiz_Import_Template_official.xlsx')).active
texts = []
for d in chs:
    f = glob.glob(d + '/Kahoot_*.xlsx'); ws = openpyxl.load_workbook(f[0]).active
    same = all(ws[f'{c}8'].value == kt[f'{c}8'].value for c in 'ABCDEFGH')
    rows = [[ws[f'{c}{r}'].value for c in 'BCDEFGH'] for r in range(9, 209) if ws[f'B{r}'].value]
    ok = all(len(q) <= 120 and all(len(a) <= 75 for a in o if a) and sum(1 for a in o if a) >= 2 and t in (5, 10, 20, 30, 60, 120) and 1 <= int(c) <= sum(1 for a in o if a)
             for q, *rest in rows for o, t, c in [(rest[:4], rest[4], rest[5])])
    check(same and ok and 10 <= len(rows) <= 20 and ws['B9'].value != kt['B9'].value, f'Kahoot {os.path.basename(f[0])}: official header row 8, {len(rows)} valid questions')
    texts += [' '.join(str(x) for x in r if x) for r in rows]
# Blooket
for d in chs:
    f = glob.glob(d + '/Blooket_*.csv')[0]; R = list(csv.reader(open(f, encoding='utf-8')))
    ok = R[0][0] == 'Blooket\nImport Template' and R[1][:2] == ['Question #', 'Question Text'] and R[1][6].startswith('Time Limit') and R[1][7].startswith('Correct Answer')
    body = R[2:]; ok2 = all(len(r) == 8 and r[0] == str(i) and r[2] and r[3] and 1 <= int(r[7]) <= 4 and r[2 + int(r[7]) - 1] and 0 < int(r[6]) <= 300 for i, r in enumerate(body, 1))
    check(ok and ok2 and len(body) >= 15, f'Blooket {os.path.basename(f)}: template header, {len(body)} valid rows'); texts += [' '.join(r) for r in body]
# Gimkit
gt = list(csv.reader(open(os.path.join(TPL, 'gimkit', 'Copy of Gimkit Spreadsheet Import Template - Sheet1.csv'), encoding='utf-8')))
for d in chs:
    f = glob.glob(d + '/Gimkit_*.csv')[0]; R = list(csv.reader(open(f, encoding='utf-8')))
    ok = R[0][0] == gt[0][0] and R[1] == gt[1] and all(len(r) == 5 and r[0] and r[1] and r[2] for r in R[2:])
    check(ok and len(R) - 2 >= 15, f'Gimkit {os.path.basename(f)}: official template header, {len(R) - 2} rows'); texts += [' '.join(r) for r in R[2:]]
# Wayground
wt = openpyxl.load_workbook(os.path.join(TPL, 'Wayground_Import_Template_official.xlsx')).active
types = {'Multiple Choice', 'Checkbox', 'Fill-in-the-Blank', 'Open-Ended', 'Poll', 'Draw'}
for d in chs:
    f = glob.glob(d + '/Wayground_*.xlsx')[0]; ws = openpyxl.load_workbook(f).active
    same = all(ws.cell(r, c).value == wt.cell(r, c).value for r in (1, 2) for c in range(1, 12))
    rows = [[ws.cell(r, c).value for c in range(1, 12)] for r in range(3, 1001) if ws.cell(r, 1).value]
    ok = all(r[1] in types and (r[1] == 'Open-Ended' or (r[2] and r[3] and 1 <= int(r[7]) <= 5 and r[1 + int(r[7])])) and r[8] in (5, 10, 20, 30, 45, 60, 120, 180, 300, 900) for r in rows)
    check(same and ok and len(rows) >= 10 and rows[0][0] != wt.cell(3, 1).value, f'Wayground {os.path.basename(f)}: official header rows 1-2, {len(rows)} valid rows'); texts += [' '.join(str(x) for x in r if x) for r in rows]
# Quizlet
for d in chs:
    f = glob.glob(d + '/Quizlet_*.txt')[0]; L = open(f, encoding='utf-8').read().splitlines()
    check(len(L) >= 10 and all(l.count('\t') == 1 and all(p.strip() for p in l.split('\t')) for l in L), f'Quizlet {os.path.basename(f)}: {len(L)} lines, one tab each'); texts += L
# Free-plan caps
allf = glob.glob(IMP + '/*/*')
check(sum('Wordwall_' in f for f in allf) == 3, 'Wordwall: exactly 3 activities (free Basic cap)')
check(sum('Padlet_' in f for f in allf) == 3, 'Padlet: exactly 3 boards (free Neon cap)')
check(sum('Mentimeter_' in f for f in allf) == 2, 'Mentimeter: 2 presentations (50 participants per month)')
check(sum('Wayground_Ch' in f for f in allf) <= 20, 'Wayground: within the 20-resource free library cap')
texts += [open(f, encoding='utf-8').read() for f in allf if f.endswith('.txt')]
# Guide + zip
G = os.path.join(OUT, 'Free_Apps_Activity_Guide_Ch1-7')
pdf = subprocess.run(['pdftotext', G + '.pdf', '-'], capture_output=True, text=True).stdout
dx = ' '.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', zipfile.ZipFile(G + '.docx').read('word/document.xml').decode('utf8')))
check(all(a in pdf for a in ('Kahoot', 'Blooket', 'Gimkit', 'Wayground', 'Quizlet', 'Wordwall', 'Padlet', 'Mentimeter')) and "Jmal C's Digital Literacy Class" in pdf, 'guide PDF: every app, branded')
from_map = sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools'))
from free_apps import MAP
from activities import A
check(len(MAP) == sum(len(v) for v in A.values()) == 26, 'every one of the 26 activities has an app')
z = os.path.join(OUT, 'Free_App_Import_Files_Ch1-7.zip'); check(os.path.getsize(z) < 25 * 1024 * 1024 and len(zipfile.ZipFile(z).namelist()) >= 40, f'zip under 25 MB ({os.path.getsize(z)} bytes)')
book = set().union(*(grams(W(open(f, encoding='utf-8', errors='ignore').read())) for f in glob.glob('/workspace/BCC_IC3_Class/ch1-7_text/*.txt')))
for name, t in [('import files', '\n'.join(texts)), ('guide PDF', pdf), ('guide DOCX', dx), ('free_apps.py', open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools/free_apps.py'), encoding='utf-8').read())]:
    hits = grams(W(t)) & book
    check(not hits, f'{name}: no 9-word stretch matches the textbook {sorted(hits)[:2]}')
    check(chr(0x2014) not in t, f'{name}: no em dashes')
print(f'\n{len(fails)} failed'); sys.exit(1 if fails else 0)
