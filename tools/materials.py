"""Teacher-only Ch 1-7 Teaching Materials (teacher.html tab). Links point to Jmal's organized Drive copies
(folder "BCC Digital Literacy Class (IC3) - Fall 2026"), plus Fatima's originals where no copy exists.
Drive sharing settings keep these files private; the page only lists links. No logins or passwords here."""
D = 'https://drive.google.com/file/d/{}/view'
S = 'https://docs.google.com/presentation/d/{}/edit'
G = 'https://docs.google.com/document/d/{}/edit'
FOLDERS = [
    ('Class folder (everything)', 'https://drive.google.com/drive/folders/1FvbcBZ60pe7SIbeOYUnxAJOr6ajoH3Za'),
    ('03 Study Materials Ch 1-7', 'https://drive.google.com/drive/folders/1B7JI0bIUsl9AKQHN3j2H0keQ60dkpqpY'),
    ('04 Textbook Lessons 1-7 (copies)', 'https://drive.google.com/drive/folders/1Jky2xHNoXVIFa6gZ6iO2MWP46iyidTPF'),
    ('05 Instructor Materials Ch 1-7 (copies)', 'https://drive.google.com/drive/folders/1AJIn47I5LY9tFsCDP4a28FvGkqiUds1n'),
    ('Class Organizer (Google Doc)', G.format('1CTL3xky8GgnmdBSGBQQKBCLi61zJRijTm7gqfJVXJE0')),
    ('Study Materials Ch 1-7 link list (your copy)', G.format('1PrRAwHdsVV2tCX2u_exIefSU7tWAi25q6qe0cLoFM3U')),
    ("Fatima's IC3 GS5 Instructor Materials (original, all 17 lessons)", 'https://drive.google.com/drive/folders/1Uyg7c6tcQINHk8fO6bNql17np9EBgwv0'),
    ("Elizabeth Materials (original)", 'https://drive.google.com/drive/folders/1biPnC1od3HO0Bkm2hXJg9KJmWFhp7mX6'),
]
ANSWER_KEY = ('Answers to Review Questions, Lessons 1-7 (scanned key with explanations)', D.format('1ZOOa6J9Dg0yoY2hfTFlaHC9kQo1Xqy_c'))
KH = 'https://kahoot.it/challenge/{}?challenge-id=b55b1fea-8a8e-4436-8f68-edf147c160dc_{}'
CH = {
 1: dict(text='1_WpmeJ_6Zto3wJSPMBgEbppkA8xR0nF_', slides='1BEfnt25Lq1i5TTGWL0DN-f1FNKJpIGVs', quiz='1oJelcfCYLgDpTmeTV2KYlHdi3Lt20dr6',
         preview=None, kahoot=[('Kahoot challenge', KH.format('002374691', '1764085052986'))],
         warm=('1C6PqsIaxlX5Eai3CS_qe9UfOtKte9ISA', '1vMEWvJ4X2RkcZX0KDPV_eEMKeRDlNjyh'), study=('1cPxwsqi1RDUDf-k_xbPz_E0SAHUsWNMl', '1gxo26zeaM6v3x85o-FCs2nYcQURPzCnR')),
 2: dict(text='1j9H59pUYaDtcT1oAFd2DRwgM9Wm3UJUP', slides='1JeOofYAM6gbmhjinFhivtlLgWVeLEVi3', quiz='1E8kjD-VsleAqYNfjszADclGTMcO2PQf-',
         preview=G.format('17ykBq2PyDtKlNlZVQgNmX44sO269b26ddm7YedD2TFc'), kahoot=[('Kahoot challenge', KH.format('006182042', '1764085006467'))],
         warm=('1_TWK8Hg7ugsxSYfZgEo5pKDNtAOiPdMG', '1dUpYoKO3szR6dF4IvNONkiDu--CxSZXN'), study=('1x_0FpdlctkrPUSvD69X9mtRIuezfbpEd', '18cplRwHQVAWnTMHj5O4TS3epjv0c1QWV')),
 3: dict(text='1WcLJzM4JPL4CHzOzehOYdq9HrxKIOPR8', slides='16blakEWPvKRkFz5eTfitt8msaHPT9cVR', quiz='1j7xw70LgMPP3sZegfOCQnn1-NikTd1fd',
         preview=D.format('1pQmpDbltDwFGsfbs15QjodxlgnakVJ68'), kahoot=[('Kahoot challenge', KH.format('001711574', '1764084964953'))],
         warm=('19ZpFV_ahKIhr72YCJhe5hgGNNryswF7p', '1YpRV-WIlN5nVJqvLfdBPNHmyurXYN1m4'), study=('1v1sdCfaIHxlNp3mJ4Vc_Ul21AMktt_hg', '1nKBYbW8Mu8TKu6kNorMvoQiqC2mwAwmy')),
 4: dict(text='1yOUtT6Q_pj8uGvhmlGE7vpN0uNvfQ4iy', slides='1YJ_Y023lAilHLnTnHyENJvAxpmYNQsQE', quiz='1XNIlvgwUfF0PJ5jCPdNBxdD8VT3Cp4DB',
         preview=G.format('15LUg5fRjINpYWiZANFNwepsGrOzSbWgYBRMvRx-eig4'),
         kahoot=[('Kahoot challenge, part 1', KH.format('00688897', '1763586195115')), ('Kahoot challenge, part 2', KH.format('001106080', '1763586309196'))],
         warm=('17vipm_L3OnDRXmrnbrjIxR0E0qoJ65Ou', '1t_dIAC6ZCcMU7KpnQj7bnT9t7k3Z95zb'), study=('1pLJ3hJBp-x65bKmAXPJOjNcOjLq5b_Iu', '1btcV_wbkKaXnusUu4paPs-2xuKUbB2IF')),
 5: dict(text='1kmZjbsrH5CvawSe_xdOvaY16ii4NEb_I', slides='1-rCfbRWoOK2p94WvRC5vIXdtX3WI11MZ', quiz='1T16LQk4EePrvzadACgA8pQk7Iw_CS09u',
         preview=G.format('15qz86EXuJTHI66i19g3EYXBiW9p6VM0CP02kcrwDfuo'), kahoot=[('Kahoot challenge', KH.format('005475747', '1763586367475'))],
         warm=('1BCi5dKx9-OQ7XzAtEOM4D6YSfm_nqhCh', '1JoT8IwkTlgqFPxYTSYSy_oljqwq2qfqO'), study=('12olIvhSPSdwTY9EvjbnHnQoP7P7Jrcm-', '172Rsja698uo5HJDtv0XeFevnbxJjCtjY')),
 6: dict(text='1lo1BN5Ik6s4EPm3jbBUlCbBtzTqQXuE6', slides='1M7QJ7Yh0HSbJOfto5km37EBaYfm_c5Of', quiz='1P3gP8t3feC6Vo1tK9sTyZ1UKSxmEhHGR',
         preview=G.format('1pZyZzP-MXhxnRAdRQaD_t4CrRT_pbtoYxtm3pu_b5jM'), kahoot=[('Kahoot challenge', KH.format('001053709', '1763592177878'))],
         warm=('1ap9r19jMTzGc2lwPf9t1MeXWvCSC2axi', '1jaDxF9ze9ZEoSsmBM8r0SnWrpuwKMk9z'), study=('1CIZeRC5tzfcl3u9k6rNugWWCKpcpRWFk', '16LbQg5s6fNQUbcYj9-InEuKnMp2TPT81'),
         extra=[("Fatima's Lesson 6 worksheets (folder)", 'https://drive.google.com/drive/folders/1A1ARV1XwRRJm1gg9YrzRRyHe8X4dda_6')]),
 7: dict(text='1Zw26TAnEK9_GgtdJx-skCDQK7O1p6FVe', slides='1N1QkVD20QUygZO9ou2nLxHbcgKrzy48y', quiz='1X6wSPPtNOJu6L4zSa_3lmFvlqShDg18X',
         preview=G.format('1ymPGtM4-WycTKXjLn9hwJ4ndqHZz8KPhuUGDwXHPoHM'), kahoot=[('Kahoot challenge', KH.format('007439098', '1764019458537'))],
         warm=('1Ltb6BMDWXlIz6u7aMcVdPxLJiiAhD9yw', None), study=(None, None),
         extra=[("Fatima's Lesson 7 worksheets: gap fill, word scramble, discussion (folder)", 'https://drive.google.com/drive/folders/1PmKg12F924sTVWhI2k1gH7jsUK0aExX8')]),
}
QUIZ_N = {1: 10, 2: 10, 3: 10, 4: 21, 5: 9, 6: 15, 7: 20}
SLIDES_N = {1: 34, 2: 32, 3: 35, 4: 35, 5: 30, 6: 32, 7: 69}

def build(chapters):
    out = dict(folders=[dict(t=t, u=u) for t, u in FOLDERS], key=dict(t=ANSWER_KEY[0], u=ANSWER_KEY[1]), chapters=[])
    for c in chapters:
        m = CH[c['n']]; L = []
        L.append(dict(k='Textbook', t=f"Lesson {c['n']} {c['title']} (textbook PDF, your copy)", u=D.format(m['text'])))
        L.append(dict(k='Slides', t=f"Lesson {c['n']} slides ({SLIDES_N[c['n']]} slides, PowerPoint)", u=S.format(m['slides'])))
        L.append(dict(k='Quiz', t=f"Lesson {c['n']} quiz ({QUIZ_N[c['n']]} questions, PDF)", u=D.format(m['quiz'])))
        L.append(dict(k='Answer key', t=f"Answer key for the Lesson {c['n']} quiz: see Lesson {c['n']} in Answers to Review Questions", u=ANSWER_KEY[1]))
        if m['preview']: L.append(dict(k='Preview', t=f"Preview Lesson {c['n']} (Fatima's original)", u=m['preview']))
        else: L.append(dict(k='Preview', t=f"Preview Lesson {c['n']}: not shared with your account yet (ask Fatima)", u=''))
        w, wa = m['warm']
        if w: L.append(dict(k='Warm-up', t=f"L{c['n']} warm-up gap fill (Elizabeth)", u=G.format(w)))
        L.append(dict(k='Warm-up', t=(f"L{c['n']} warm-up answers (Elizabeth)" if wa else f"L{c['n']} warm-up answers: none in the folder"), u=G.format(wa) if wa else ''))
        sq, sa = m['study']
        if sq: L.append(dict(k='Study Q&A', t=f"L{c['n']} study questions (Elizabeth)", u=G.format(sq)))
        if sa: L.append(dict(k='Study Q&A', t=f"L{c['n']} study answers (Elizabeth)", u=G.format(sa)))
        if not sq: L.append(dict(k='Study Q&A', t=f"L{c['n']} study questions: none in the folder", u=''))
        for t, u in m['kahoot']: L.append(dict(k='Kahoot', t=t + ' (Fall 2025 link, test before class)', u=u))
        for t, u in m.get('extra', []): L.append(dict(k='Worksheets', t=t, u=u))
        out['chapters'].append(dict(n=c['n'], title=c['title'], icon=c['icon'], links=L))
    return out
