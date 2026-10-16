# Free-app versions of the Ch 1-7 Fun Activities and games. ORIGINAL wording for Jmal C's Digital Literacy Class.
# Question banks are built from games.py + summaries.py vocab, plus the extra questions below (correct answer first).
CH = {1: 'Operating Systems', 2: 'Hardware', 3: 'Networks and Mobile Devices', 4: 'File Management', 5: 'Software', 6: 'Cloud Computing', 7: 'Security and Maintenance'}

EXTRA = {
 1: [("You will be away for a weekend. Which choice saves your work and uses no battery?", ["Hibernate", "Sleep", "Lock", "Sign out"], "Hibernate saves your open work to the drive and turns the power off."),
     ("Which key combo opens Task View?", ["Windows key + Tab", "Ctrl + C", "Alt + F4", "Windows key + L"], "Windows key + Tab shows all open windows and desktops."),
     ("Your sister changes her desktop background. What happens to your background?", ["Nothing, it stays the same", "It changes too", "It turns black", "It is deleted"], "Backgrounds are saved in each user profile.")],
 2: [("Which port sends both video and sound to a TV?", ["HDMI", "USB-A", "Ethernet", "3.5 mm audio jack"], "HDMI carries picture and sound in one cable."),
     ("Which port is small, flat, and plugs in either way up?", ["USB-C", "VGA", "Ethernet", "USB-A"], "USB-C is reversible and charges many phones and laptops."),
     ("Which cable plugs a computer into a router for wired internet?", ["Ethernet", "HDMI", "VGA", "Power cord"], "Ethernet is the network cable."),
     ("Your laptop gets slow with 30 tabs open. What would help most?", ["More RAM", "A bigger monitor", "A new mouse", "More speakers"], "RAM holds the programs and tabs you have open right now."),
     ("Which is bigger: 500 MB or 2 GB?", ["2 GB", "500 MB", "They are the same", "It depends on the file"], "1 GB is about 1,000 MB, so 2 GB is about 2,000 MB.")],
 3: [("Which Wi-Fi password is the strongest?", ["Blue!Taxi-Sings-42", "password123", "12345678", "MyName"], "Long, mixed, and hard to guess beats short and common."),
     ("Which Wi-Fi security should you choose today?", ["WPA3 or WPA2", "WEP", "Open (no password)", "None needed"], "WEP is old and easy to break."),
     ("What should a professional voice mail greeting include?", ["Your name and when you will call back", "A long song", "Your password", "Your home address"], "Short, clear, and polite: name, sorry I missed you, call back.")],
 4: [("Which path is written correctly for Windows?", ["C:\\Users\\Ana\\Documents\\Resume.docx", "Resume.docx/Documents/Ana", "Users-Ana-Documents", "C//Ana//Resume"], "A path goes from the drive down through each folder to the file."),
     ("You delete a file from a USB flash drive. Where does it go?", ["It is gone (no Recycle Bin)", "The Recycle Bin", "The Downloads folder", "OneDrive"], "Files deleted from flash drives skip the Recycle Bin."),
     ("Where does a downloaded file usually go?", ["The Downloads folder", "The Desktop", "The Recycle Bin", "Program Files"], "Downloads is the default location for web downloads."),
     ("How do you select files 1, 4, and 7 only?", ["Hold Ctrl and click each one", "Hold Shift and click 1 and 7", "Double-click each one", "Press Ctrl + A"], "Ctrl + click picks items one at a time; Shift picks a range.")],
 5: [("A customer says Excel crashes every time. What should the help desk try first?", ["Repair Office in Settings > Apps", "Buy a new computer", "Delete all files", "Turn off Wi-Fi forever"], "Repair fixes broken program files and keeps settings."),
     ("Which app is best for a free video call with family in another country?", ["WhatsApp or another internet chat app", "SMS text", "Fax", "A printed letter"], "Internet chat apps make free voice and video calls on Wi-Fi."),
     ("Where do you change which browser opens links on Windows?", ["Settings > Apps > Default apps", "The Recycle Bin", "File Explorer", "The taskbar clock"], "Default apps decides which program opens each file or link."),
     ("What does freeware mean?", ["Software you can use at no cost", "Software that costs monthly", "Software that is broken", "A virus"], "Freeware is free to use.")],
 6: [("You want your teacher to read your file but not change it. Which share setting?", ["Can view", "Can edit", "Owner", "Public, anyone can edit"], "View-only lets people read without changing."),
     ("What do you need to use cloud storage?", ["An account, a device, and internet", "Only a printer", "A CD drive", "A landline phone"], "You sign in on a device that is online."),
     ("Which cloud is built into iPhones?", ["iCloud", "OneDrive", "Dropbox", "Google Drive"], "iCloud is Apple's cloud."),
     ("You delete a file in your synced OneDrive folder. What happens?", ["It is deleted in the cloud too", "Nothing happens online", "It moves to a USB drive", "It gets bigger"], "Sync keeps both copies the same, deletes too.")],
 7: [("Your computer is very slow. What is a good first step?", ["Restart it and close extra programs", "Throw it away", "Pay a stranger who calls you", "Turn off the antivirus"], "Restarting fixes many slow-down problems."),
     ("You are on airport Wi-Fi and need your bank. What should you use?", ["A VPN or your phone's data", "Any open Wi-Fi with no worry", "A stranger's laptop", "An email to the bank with your password"], "A VPN encrypts traffic on public Wi-Fi."),
     ("What should you do before a factory reset of your phone?", ["Back up your photos and contacts", "Nothing", "Delete your backups", "Turn off the screen"], "A factory reset erases everything on the device."),
     ("What does the 3-2-1 backup rule mean?", ["3 copies, 2 kinds of storage, 1 copy off-site", "Back up 3 times a year", "Use 2 passwords", "1 copy is enough"], "Keep copies in different places so one problem cannot erase them all.")],
}

# Activity -> app map (chapter, activity number) -> (app, what to use, how to run it)
MAP = {
 (1, 1): ('Wordwall', 'Wordwall #1: Group sort "Global or Just Me?"', 'Play on the projector or share the link in Zoom chat after the card sort.'),
 (1, 2): ('Kahoot', 'Kahoot Ch 1 quiz', 'Host live as the exit quiz after the role-play.'),
 (1, 3): ('Quizlet', 'Quizlet Ch 1 set (Quizlet Live, teams)', 'Run Quizlet Live in teams mode after the treasure hunt.'),
 (2, 1): ('Blooket', 'Blooket Ch 2 set (port questions included)', 'Host Gold Quest or Tower Defense for 8 minutes.'),
 (2, 2): ('Gimkit', 'Gimkit Ch 2 kit (input / output / storage)', 'Host Classic mode for 8 minutes.'),
 (2, 3): ('Kahoot', 'Kahoot Ch 2 quiz (bytes order questions)', 'Host live right after the line-up.'),
 (2, 4): ('Quizlet', 'Quizlet Ch 2 set', 'Quizlet Live or Match to review RAM vs. storage words.'),
 (3, 1): ('Padlet', 'Padlet #1: "Speed Test Lab" board', 'Students post their download, upload, and ping results.'),
 (3, 2): ('Mentimeter', 'Mentimeter #1: "Strongest Wi-Fi password" vote', 'Students vote for the strongest team password.'),
 (3, 3): ('Kahoot', 'Kahoot Ch 3 quiz', 'Host live after Be the Router.'),
 (3, 4): ('Wayground', 'Wayground Ch 3 quiz (with an open-ended voice mail question)', 'Assign as homework.'),
 (4, 1): ('Gimkit', 'Gimkit Ch 4 kit', 'Host Classic mode after the race.'),
 (4, 2): ('Wordwall', 'Wordwall #2: Group sort "File Type Sort"', 'Use as the warm-up before Extension Bingo.'),
 (4, 3): ('Kahoot', 'Kahoot Ch 4 quiz (path and zip questions)', 'Host live after the treasure map.'),
 (4, 4): ('Wayground', 'Wayground Ch 4 quiz (with an open-ended folder plan question)', 'Assign as homework with the mini-project.'),
 (5, 1): ('Blooket', 'Blooket Ch 5 set', 'Host Café or Gold Quest mode for 8 minutes.'),
 (5, 2): ('Kahoot', 'Kahoot Ch 5 quiz (help desk questions)', 'Host live after the role-play.'),
 (5, 3): ('Gimkit', 'Gimkit Ch 5 kit', 'Host Classic mode as the quick-fire round.'),
 (6, 1): ('Blooket', 'Blooket Ch 6 set', 'Host after the relay as a team race.'),
 (6, 2): ('Kahoot', 'Kahoot Ch 6 quiz (view vs. edit questions)', 'Host live.'),
 (6, 3): ('Padlet', 'Padlet #2: "Notification Makeover" board', 'Students post before and after screenshots.'),
 (6, 4): ('Mentimeter', 'Mentimeter #2: "Cloud: worth it?" before/after vote', 'Vote before and after the debate.'),
 (7, 1): ('Blooket', 'Blooket Ch 7 set (Scam or Legit questions)', 'Host Gold Quest after the team game.'),
 (7, 2): ('Wordwall', 'Wordwall #3: Match up "Malware Who Am I?"', 'Play as the riddle review.'),
 (7, 3): ('Kahoot', 'Kahoot Ch 7 quiz (troubleshooting questions)', 'Host live after the detective challenge.'),
 (7, 4): ('Padlet', 'Padlet #3: "My Backup Plan" board', 'Students post their 3-2-1 plan.'),
}

WAYGROUND_OPEN = {
 3: "Write a 3-sentence professional voice mail greeting for your phone.",
 4: "List 4 folders you will make for your important documents (for example: ID, Health, Jobs).",
}

PADLET = [
 dict(n=1, ch=3, title="Speed Test Lab (Ch 3)", fmt="Wall", desc="Jmal C's Digital Literacy Class. Post your internet speed test results.",
      prompt="Run a speed test (fast.com or speedtest.net). Post: 1) download Mbps, 2) upload Mbps, 3) ping, 4) Wi-Fi or cable? Add a screenshot if you can.",
      cols=None),
 dict(n=2, ch=6, title="Notification Makeover (Ch 6)", fmt="Columns", desc="Jmal C's Digital Literacy Class. Show your phone or PC notifications before and after.",
      prompt="Post a screenshot of your notifications BEFORE, then AFTER you turn off 3 apps. Write which 3 apps you turned off and why.",
      cols=["Before", "After", "What I changed"]),
 dict(n=3, ch=7, title="My Backup Plan (Ch 7)", fmt="Columns", desc="Jmal C's Digital Literacy Class. Share your 3-2-1 backup plan.",
      prompt="Write your plan: What will you back up? Where are your 3 copies? Which 2 kinds of storage? Where is 1 copy off-site? How often?",
      cols=["What I back up", "My 3 copies", "How often"]),
]
MENTI = [
 dict(n=1, ch=3, title="Strongest Wi-Fi Password (Ch 3)", slides=[
      ("Multiple choice", "Which Wi-Fi password is the strongest?", ["Team 1 password", "Team 2 password", "Team 3 password", "Team 4 password"]),
      ("Word cloud", "One word: what makes a password strong?", []),
      ("Multiple choice", "Which Wi-Fi security should you pick?", ["WPA3", "WPA2", "WEP", "No password"])]),
 dict(n=2, ch=6, title="Cloud: Worth It? (Ch 6)", slides=[
      ("Scales", "BEFORE the debate: How much do you trust the cloud with your files? (1 = not at all, 5 = a lot)", []),
      ("Open ended", "Best reason FOR the cloud?", []),
      ("Open ended", "Best reason to WATCH OUT?", []),
      ("Scales", "AFTER the debate: How much do you trust the cloud with your files? (1 = not at all, 5 = a lot)", [])]),
]
WORDWALL = [
 dict(n=1, ch=1, game='c1_sort', template='Group sort', title="Global or Just Me? (Ch 1)",
      inst="Drag or tap each setting into the right group: changes it for everyone, or just for me?"),
 dict(n=2, ch=4, game='c4_sort', template='Group sort', title="File Type Sort (Ch 4)",
      inst="Look at the letters after the dot. Put each file in the right group."),
 dict(n=3, ch=7, game='c7_match', template='Match up', title="Malware Who Am I? (Ch 7)",
      inst="Match each threat or tool to what it does."),
]
