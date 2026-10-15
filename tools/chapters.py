"""Chapters 1-7 of the BCC textbook (CCI Learning, IC3 GS5 Computing Fundamentals) mapped to the
official IC3 GS5 objective numbers that every Quest and Practice Lab item already carries.

Used by the Quest build, the Practice Lab build, and tools/build_site.py.
Topic lists are short labels written for this class (no textbook text).
Note: the textbook prints its own objective tags (like 1-2.14). A few of those are numbered differently
from Certiport's official list, so this map follows the official numbering by content.
"""
CHAPTERS = [
    dict(n=1, title='Operating Systems', icon='🪟',
         topics=['What an operating system does', 'Popular desktop and mobile operating systems', 'User accounts and profiles',
                 'Signing in, locking, sleep, hibernate, and shutting down', 'Start menu, desktop, taskbar, and Task View',
                 'Settings app and Control Panel', 'System-wide vs. personal settings', 'Personalizing the desktop', 'Touch gestures', 'Operating system updates']),
    dict(n=2, title='Hardware', icon='🖥️',
         topics=['Drivers, firmware, and platforms', 'Units of measure (bits, bytes, hertz)', 'Memory (RAM) vs. storage', 'Types of computers',
                 'Keyboards, mice, touch screens, and styluses', 'Smartphone hardware', 'Power plans and battery life', 'Peripherals and ports',
                 'Bluetooth, infrared, and other wireless connections']),
    dict(n=3, title='Networks and Mobile Devices', icon='📶',
         topics=['Why we network', 'Network basics and IP addresses', 'Internet service: DSL, cable, fiber, satellite, cellular', 'Bandwidth and speed',
                 'Modems, routers, and LANs', 'Ethernet', 'Wi-Fi and wireless security', 'Cellular networks and phone plans', 'How phones and tablets connect',
                 'Landlines and VoIP', 'Voice mail']),
    dict(n=4, title='File Management', icon='📁',
         topics=['Folders, directories, and paths', 'Rights and permissions', 'File Explorer and windows', 'File types and extensions',
                 'Copy, move, rename, delete, and new folders', 'Searching and sorting', 'Recycle Bin', 'Default save and download locations',
                 'Getting photos off a phone', 'Managing media files', 'Sharing files and zipping/unzipping']),
    dict(n=5, title='Software', icon='💿',
         topics=['Why we use software', 'Getting software: stores, websites, licenses, subscriptions', 'System requirements',
                 'Install, uninstall, repair, and update', 'App preferences and options (Office)', 'Windows apps and the Microsoft Store',
                 'Messaging apps (SMS, MMS, chat)']),
    dict(n=6, title='Cloud Computing', icon='☁️',
         topics=['What the cloud is and why it helps', 'Cloud accounts', 'OneDrive', 'iCloud', 'Dropbox and Google Drive', 'Upload, download, and sync',
                 'Sharing links and permissions', 'Web apps, SaaS, CRM, LMS, and discussion boards', 'Mobile notifications']),
    dict(n=7, title='Security and Maintenance', icon='🔒',
         topics=['Usernames and strong passwords', 'Malware: viruses, worms, Trojans, spyware, adware, ransomware', 'Network and Wi-Fi risks',
                 'Public computers', 'Social engineering and phishing', 'Antivirus, firewalls, HTTPS, and VPNs', 'Backup and restore',
                 'System Restore and factory reset', 'Troubleshooting basics']),
]

# Official GS5 objective (or parent objective) -> chapter(s). The longest matching prefix wins.
OD_CH = {
    # 1 Mobile Devices
    '1.1': [3], '1.2': [3], '1.2.2': [5], '1.3': [3], '1.3.1': [2, 3], '1.3.2': [5], '1.4': [3], '1.5': [5], '1.6': [6],
    # 2 Hardware Devices
    '2.1': [2], '2.2': [2], '2.3': [2], '2.4': [2, 3], '2.5': [3], '2.6': [2], '2.6.4': [1], '2.7': [2], '2.8': [1, 2],
    '2.9': [5], '2.9.1': [4], '2.10': [3], '2.11': [3], '2.12': [2], '2.13': [1, 2], '2.13.2': [2],
    # 3 Computer Software Architecture
    '3.1': [1], '3.2': [1], '3.2.2': [1, 5], '3.3': [1], '3.3.5': [4], '3.4': [5], '3.5': [1], '3.6': [4], '3.7': [4], '3.8': [1, 4],
    '3.9': [4], '3.10': [4], '3.11': [3], '3.12': [5], '3.13': [7], '3.13.4': [3, 7], '3.13.5': [3, 7],
    # 4 Backup and Restore, 5 File Sharing, 6 Cloud, 7 Security
    '4': [7], '5.1': [4], '5.1.5': [6], '5.1.4': [4, 6], '5.2': [4], '6': [6],
    '7': [7], '7.1.4': [1, 7], '7.1.5': [1, 7], '7.1.6': [1, 7], '7.4.1': [3, 7], '7.4.3': [3, 7],
}

def od_chapters(code):
    code = str(code)
    parts = code.split('.')
    for k in range(len(parts), 0, -1):
        key = '.'.join(parts[:k])
        if key in OD_CH:
            return OD_CH[key]
    return []

def chapters_for(ods, extra=()):
    out = []
    for c in list(ods or []):
        for n in od_chapters(c):
            if n not in out:
                out.append(n)
    for n in extra or ():
        if n not in out:
            out.append(n)
    return sorted(out)

# LearnKey workbooks (kept as Extra practice) -> chapters
WORKBOOKS = [
    ('L01_Workbook_Mobile_Devices.pdf', 'Mobile Devices', [3]),
    ('L02_Workbook_Hardware_Part_I.pdf', 'Hardware Part I', [2]),
    ('L03_Workbook_Hardware_Part_II.pdf', 'Hardware Part II', [2, 3]),
    ('L04_Workbook_Computer_Software_Architecture_Part_I.pdf', 'Software Architecture Part I', [1]),
    ('L05_Workbook_Computer_Software_Architecture_Part_II.pdf', 'Software Architecture Part II', [4]),
    ('L06_Workbook_Computer_Software_Architecture_Part_III.pdf', 'Software Architecture Part III', [4, 5, 7]),
    ('L07_Workbook_Backup_and_Restore.pdf', 'Backup and Restore', [7]),
    ('L08_Workbook_File_Sharing.pdf', 'File Sharing', [4, 6]),
    ('L09_Workbook_Cloud_Computing.pdf', 'Cloud Computing', [6]),
    ('L10_Workbook_Security.pdf', 'Security', [7]),
]

if __name__ == '__main__':
    import sys; sys.path.insert(0, '/workspace/quest')
    from official_od import leaves
    miss = [c for c, _ in leaves() if not od_chapters(c)]
    print('leaves without a chapter:', miss)
    from collections import Counter
    print(Counter(n for c, _ in leaves() for n in od_chapters(c)))
