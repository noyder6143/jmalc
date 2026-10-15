# Chapter 1-7 gap-fill items for the Practice Lab (Oct 2026). ORIGINAL wording written for Jmal C's class.
# They cover textbook topics the GMetrix-mirror items barely touched. Nothing here is copied from the
# CCI textbook, its quizzes, or its answer key. Correct option is listed first (the build shuffles).
# tt='CH' keeps them out of the GMetrix-mirror topic tests; they feed Chapter Quiz, Custom quiz, and the Final pool.
from h import MC, CH, TF
DOMT = {"1": "MD", "2": "HW", "3": "SA", "4": "BR", "5": "FS", "6": "CC", "7": "SEC"}
def _t(od): return DOMT[od[0].split('.')[0]]
def M(ch, id, od, q, opts, why, **k): return MC(id, _t(od), 'CH', od, q, opts, 0, why, chx=[ch], **k)
def C(ch, id, od, q, opts, n, why, **k): return CH(id, _t(od), 'CH', od, q, opts, list(range(n)), why, chx=[ch], **k)
def T(ch, id, od, q, ans, why, **k): return TF(id, _t(od), 'CH', od, q, ans, why, chx=[ch], **k)

# ---------- Chapter 1: Operating Systems
M(1, "ch1_os_job", ["2.8.1"], "What is the main job of an operating system like Windows, macOS, or Android?",
  ["It manages the hardware, runs your apps, and gives you a way to work with the device", "It only protects the computer from viruses", "It is the physical chip that does the math", "It is a website you sign in to"],
  "The operating system sits between you, your apps, and the hardware. Without one, the device can't run programs.")
M(1, "ch1_global_set", ["3.2.1"], "On a shared family PC, which change affects EVERY user account, not just yours?",
  ["Changing the computer's date and time", "Changing your desktop background", "Changing your theme colors", "Pinning an app to your own Start menu"],
  "Date and time is a system-wide (global) setting. Wallpaper, colors, and Start menu pins are saved in each person's own profile.")
T(1, "ch1_profile_tf", ["3.2.1"], "If you change the desktop background in your account, every other user on that PC sees your new background too.", False,
  "Your background is a profile setting. Each user account keeps its own desktop, documents, and preferences.")
M(1, "ch1_taskview", ["3.3.5"], "You want one screen of windows for schoolwork and a separate one for your job search, and to switch between them. Which Windows feature does this?",
  ["Task View with a new virtual desktop", "Airplane mode", "Screen saver", "Disk Cleanup"],
  "Task View (Windows key + Tab) shows your open windows and lets you add virtual desktops, each with its own set of windows.")
M(1, "ch1_notif_area", ["3.3.1"], "What is the area at the right end of the Windows taskbar that shows the clock, volume, network, and battery icons?",
  ["The notification area (system tray)", "The Recycle Bin", "The title bar", "The address bar"],
  "The notification area holds status icons and the clock. Click an icon there to change Wi-Fi, volume, or power settings quickly.")
C(1, "ch1_start", ["2.6.4", "3.8"], "Which TWO things can you do from the Windows Start button? (Choose 2.)",
  ["Open an installed app", "Shut down or restart the computer", "Add more RAM to the computer", "Make the monitor bigger"], 2,
  "The Start menu lists your apps and has the Power button for Sleep, Shut down, and Restart. Hardware changes need hands-on work.")
M(1, "ch1_zoom", ["2.13.1"], "On a tablet, how do you zoom in on a photo?",
  ["Spread two fingers apart on the screen", "Tap the photo once", "Swipe up from the bottom edge", "Press the volume-down button"],
  "Spreading two fingers zooms in, and pinching them together zooms out. One tap usually selects or opens an item.")
M(1, "ch1_hold", ["2.13.2"], "On a touch screen, which action usually does the same thing as a right-click with a mouse?",
  ["Press and hold on the item", "Double-tap quickly", "Swipe left", "Shake the device"],
  "Press and hold (long press) opens the shortcut or context menu, just like right-clicking.")
M(1, "ch1_mobile_update", ["3.1"], "Where do you check for an operating system update on most Android phones?",
  ["Settings, under System or Software update", "The Camera app", "The Contacts app", "The Google Play Store's Games tab"],
  "Phone OS updates are in Settings. On an iPhone it's Settings › General › Software Update. App updates come from the app store.")
M(1, "ch1_hibernate", ["2.6.4"], "You'll be away from your laptop for two days and want to come back to all your open windows without using battery. Which option fits best?",
  ["Hibernate", "Sleep", "Lock", "Switch user"],
  "Hibernate saves your open work to the drive and powers off, so it uses almost no battery. Sleep keeps things in RAM and slowly uses power.")

# ---------- Chapter 2: Hardware
M(2, "ch2_byte", ["2.2.4"], "How many bits make one byte?",
  ["8", "2", "10", "1,000"],
  "A bit is a single 1 or 0. Eight bits make one byte, which is about enough to store one typed character.")
M(2, "ch2_units", ["2.2.5"], "Which list goes from SMALLEST to LARGEST?",
  ["Kilobyte (KB), megabyte (MB), gigabyte (GB), terabyte (TB)", "Gigabyte, megabyte, terabyte, kilobyte", "Terabyte, gigabyte, megabyte, kilobyte", "Megabyte, kilobyte, gigabyte, terabyte"],
  "Each step is about 1,000 times bigger (exactly 1,024 in computer math): KB, MB, GB, TB.")
M(2, "ch2_tb", ["2.2.6"], "A new external drive holds 1 TB. About how many gigabytes is that?",
  ["About 1,000 GB", "About 100 GB", "About 10 GB", "About 1 GB"],
  "1 terabyte is about 1,000 gigabytes (1,024 GB). That is enough for hundreds of thousands of photos.")
M(2, "ch2_letter", ["2.2.4"], "About how much space does one typed letter, like the letter a, take up?",
  ["1 byte", "1 kilobyte", "1 megabyte", "1 gigabyte"],
  "One plain-text character takes about one byte. A one-page letter is a few kilobytes.")
M(2, "ch2_hz", ["2.12.1"], "A computer ad says the processor runs at 3.2 GHz. What does GHz measure?",
  ["Processor speed, in billions of cycles per second", "Storage space", "Internet speed", "Screen sharpness"],
  "Hertz means cycles per second. A gigahertz is a billion cycles per second, so a higher number usually means a faster CPU.")
M(2, "ch2_firmware", ["2.7"], "What do we call the small program built into a device's chip that controls the hardware at a basic level, separate from the operating system?",
  ["Firmware", "Freeware", "Adware", "A web app"],
  "Firmware lives on the device itself (a phone, router, printer, or the PC's BIOS/UEFI). A driver is different: it's installed in the OS so the OS can talk to the hardware.")
T(2, "ch2_firmware_tf", ["2.7"], "Updating your router's firmware is the same thing as installing a new app on your phone.", False,
  "A firmware update replaces the program that runs inside the device itself. It can fix bugs and security holes in the hardware.")
M(2, "ch2_fkeys", ["2.3.1"], "What are the keys labeled F1 to F12 across the top of a keyboard called?",
  ["Function keys", "Arrow keys", "Number pad keys", "Modifier keys"],
  "Function keys run shortcuts. In many apps, F1 opens Help. On laptops, they often share space with volume and brightness controls.")
M(2, "ch2_stylus", ["2.13.1"], "What is a pen-shaped tool used to tap, write, or draw on a touch screen?",
  ["A stylus", "A trackball", "A dongle", "A scanner"],
  "A stylus gives more precise control than a finger, which helps for handwriting and drawing.")
M(2, "ch2_chromebook", ["2.8.1"], "A low-cost laptop runs ChromeOS and is built mostly for web apps and cloud storage. What kind of computer is it?",
  ["A Chromebook", "A server", "A mainframe", "A smartwatch"],
  "Chromebooks run Google's ChromeOS. They start fast and rely on the internet and the cloud, so they have less local storage.")

# ---------- Chapter 3: Networks and Mobile Devices
M(3, "ch3_broadband", ["2.11.1"], "How is broadband internet different from old dial-up internet?",
  ["Broadband is always on and much faster", "Broadband needs a phone call every time you go online", "Broadband only works on phones", "There is no difference"],
  "Dial-up had to call in each time and was very slow. Broadband (DSL, cable, fiber, cellular, satellite) stays connected.")
M(3, "ch3_dsl", ["2.11.1"], "Which internet service runs over the telephone company's phone lines?",
  ["DSL", "Cable", "Satellite", "Bluetooth"],
  "DSL uses phone lines. Cable internet comes over the TV company's coaxial cable. Fiber uses light through glass strands.")
M(3, "ch3_satellite", ["2.11.4"], "A family lives far out in the country with no cable, fiber, or phone lines nearby. Which internet service is most likely available to them?",
  ["Satellite internet", "Fiber optic", "Cable", "A wired Ethernet cable to the nearest town"],
  "Satellite works almost anywhere with a clear view of the sky, but it can be slower to respond (higher latency) and costs more.")
M(3, "ch3_bands", ["2.11.4", "2.5"], "Your router offers a 2.4 GHz network and a 5 GHz network. Which statement is true?",
  ["5 GHz is usually faster but reaches a shorter distance", "2.4 GHz is always faster", "5 GHz only works with a cable", "They are exactly the same"],
  "The 5 GHz band is faster with less interference but weaker through walls. The 2.4 GHz band reaches farther but is slower and more crowded.")
M(3, "ch3_mbps", ["2.11.3"], "An internet company advertises 300 Mbps. What does that number measure?",
  ["How fast data moves, in megabits per second", "How much storage you get, in megabytes", "Your monthly price", "How many devices can connect"],
  "Mbps (megabits per second) is bandwidth, the speed of the connection. Storage is measured in bytes (MB, GB).")
M(3, "ch3_lan", ["2.11.5"], "A network that connects the computers and printers inside one building, like a school computer lab, is called a...",
  ["LAN (local area network)", "WAN (wide area network)", "VPN", "ISP"],
  "A LAN covers a small area such as a home, office, or school. A WAN links places that are far apart. The internet is the largest WAN.")
M(3, "ch3_landline", ["1.4.1"], "The power goes out in your apartment building. Which phone is most likely to still work?",
  ["A traditional corded landline phone", "A VoIP phone that plugs into your internet router", "A cordless phone whose base plugs into the wall outlet", "A calling app on your desktop computer"],
  "A classic corded landline gets its power from the phone line itself. VoIP phones, routers, modems, and cordless bases all need wall power.")
T(3, "ch3_voip", ["1.4.1"], "A VoIP (internet) phone keeps working when your modem and router lose power.", False,
  "VoIP sends calls over the internet, so it stops when the modem or router is off. That's why some people keep a landline or a cell phone for emergencies.")
M(3, "ch3_vm_greeting", ["1.4.2"], "You are applying for jobs. Which voice mail greeting is the most professional?",
  ["\"Hi, you've reached Ana Lopez. Please leave your name, number, and a short message, and I'll call you back soon.\"", "\"Yo, it's me. You know what to do.\"", "A favorite song with no words", "No greeting at all, just the robot reading your number"],
  "A professional greeting gives your name, asks for the caller's name and number, and promises a call back. Keep it short and clear.")
M(3, "ch3_vm_setup", ["1.4.2"], "You just got a new cell phone plan. What do you usually do to set up voice mail?",
  ["Call your voice mail (often by holding 1), make a PIN, and record your name and greeting", "Download a new operating system", "Turn on Airplane mode", "Buy a separate answering machine"],
  "Most carriers walk you through voice mail setup the first time you call it: create a PIN, record your name, and record a greeting.")
M(3, "ch3_tower", ["1.1.1"], "When you make a regular cell phone call, what connects your phone to the phone network?",
  ["A nearby cell tower (base station)", "Your Bluetooth earbuds", "A USB cable", "Your printer"],
  "Cell phones talk by radio to the nearest tower. The tower passes the call into the carrier's network, which also connects to landlines and the internet.")

# ---------- Chapter 4: File Management
M(4, "ch4_path", ["3.6.3"], "A file named Budget.xlsx is in a folder called 2026, which is inside your Documents folder. What is its path?",
  ["Documents\\2026\\Budget.xlsx", "Budget.xlsx\\2026\\Documents", "2026\\Documents\\Budget.xlsx", "Documents\\Budget.xlsx\\2026"],
  "A path lists folders from the outside in, separated by backslashes in Windows, and ends with the file name.")
M(4, "ch4_phone_usb", ["5.1.4"], "You connect your phone to a Windows PC with a USB cable to copy photos. Where does the phone show up?",
  ["In File Explorer under This PC, like a drive or device", "In the Recycle Bin", "Only in the Microsoft Store", "It can't be seen by the PC"],
  "Phones, tablets, and e-readers have their own operating systems. When you allow file transfer on the phone, it appears in File Explorer and you can copy photos from it.")
M(4, "ch4_recycle", ["3.6.3"], "You deleted a file from your laptop's hard drive by mistake. Where can you usually get it back?",
  ["The Recycle Bin, then choose Restore", "The Downloads folder", "The Start menu", "Task Manager"],
  "Files deleted from the computer's internal drive go to the Recycle Bin until you empty it. Restore puts the file back where it was.")
T(4, "ch4_usb_delete", ["3.6.3"], "Files you delete from a USB flash drive go to the computer's Recycle Bin, so you can easily restore them.", False,
  "Files deleted from most flash drives and network folders are removed right away. Double-check before you delete from removable drives.")
M(4, "ch4_drag", ["3.6.3"], "In File Explorer, what happens when you drag a file to a folder on the SAME drive, and when you drag it to a DIFFERENT drive like a USB stick?",
  ["Same drive: the file moves. Different drive: the file is copied.", "Same drive: copied. Different drive: moved.", "It is always deleted.", "It is always renamed."],
  "By default, Windows moves files within one drive and copies them to another drive. Right-drag if you want to choose.")
M(4, "ch4_ext", ["3.6.1"], "You can't see endings like .docx or .jpg on your file names. Where do you turn them on in File Explorer?",
  ["The View menu or tab, then File name extensions", "Settings › Wi-Fi", "The Recycle Bin", "Control Panel › Mouse"],
  "In Windows 10 it's View › File name extensions. In Windows 11 it's View › Show › File name extensions.")
M(4, "ch4_codec", ["2.9.1"], "A friend sends you a video file that won't play on your computer. What is the most likely reason?",
  ["Your computer doesn't have a player or codec for that file format", "The file is too small", "Your keyboard is unplugged", "Your screen saver is turned off"],
  "Media files come in many formats. Install a player that supports the format, or ask for the file in a common format such as MP4.")
M(4, "ch4_ctrl", ["3.8.1"], "You want to select several files that are NOT next to each other in a folder. What do you hold down while clicking each one?",
  ["Ctrl", "Shift", "Alt", "Tab"],
  "Ctrl+click picks files one by one. Shift+click picks everything in a row between the first and last file you click.")
M(4, "ch4_sort", ["3.9.2"], "A folder has 200 files. How can you quickly find the ones you changed most recently?",
  ["Sort by Date modified (click that column in Details view)", "Rename every file", "Empty the Recycle Bin", "Change the desktop background"],
  "Sorting by Date modified puts the newest files at the top. You can also sort by name, type, or size.")

# ---------- Chapter 5: Software
M(5, "ch5_sysreq", ["3.12.2"], "Before you buy or install a program, what should you check first?",
  ["That your computer meets its system requirements (OS, RAM, storage)", "That the program has a nice icon", "That your printer has paper", "That your screen saver is on"],
  "System requirements tell you the operating system, memory, storage, and other hardware the program needs to run well.")
M(5, "ch5_store", ["3.12.2"], "What is a safe place to get apps for a Windows 10 or Windows 11 PC?",
  ["The Microsoft Store or the software company's official website", "A pop-up ad that says your PC needs a free download", "A link from an unknown email", "Any file-sharing site"],
  "Official stores and publisher websites are much less likely to hide malware than random download sites.")
M(5, "ch5_subscription", ["3.12.1"], "Microsoft 365 is sold as a subscription. What does that mean?",
  ["You pay monthly or yearly and keep getting updates while you pay", "You pay once and it can never be updated", "It is free forever with ads", "You can only use it in a store"],
  "With a subscription you keep paying to keep using it, and you get new versions included. A one-time purchase is often called a perpetual license.")
M(5, "ch5_freeware", ["3.12.1"], "Which statement describes freeware?",
  ["Software you can use for free, but the company still owns it and controls the code", "Software anyone is allowed to change and share because its code is public", "A free trial that stops working after 30 days", "Hardware that comes free with a computer"],
  "Freeware costs nothing but isn't necessarily open source. Open-source software shares its code so others can study and change it.")
M(5, "ch5_repair", ["3.12.1"], "Word crashes every time it opens, but your other apps work fine. What should you try before uninstalling it?",
  ["Run Repair for Microsoft Office from Settings › Apps (or Control Panel › Programs)", "Delete the Word shortcut from the desktop", "Buy a new computer", "Turn off the monitor"],
  "Repair fixes damaged program files without removing your documents. Uninstall and reinstall is the next step if Repair doesn't help.")
M(5, "ch5_uninstall", ["3.12.1"], "What is the correct way to remove a program you no longer use in Windows?",
  ["Uninstall it from Settings › Apps (or Control Panel › Uninstall a program)", "Drag its desktop shortcut to the Recycle Bin", "Rename its folder", "Unplug the computer"],
  "Deleting a shortcut only removes the icon. Uninstalling removes the program's files and settings properly.")
M(5, "ch5_im_data", ["1.5.2"], "What does your phone need to send a WhatsApp or iMessage message?",
  ["An internet connection, through Wi-Fi or cellular data", "Only a landline", "A printer", "Bluetooth turned on"],
  "Chat apps send messages over the internet. Regular SMS texts use your carrier's text service instead.")
M(5, "ch5_app_pref", ["3.2.2", "3.4.3"], "You change the default font in Microsoft Word. What does that change affect?",
  ["New Word documents only. Other apps are not affected.", "Every app on the computer", "Every user's desktop background", "The Windows sign-in screen"],
  "An application setting only changes that one app. A system setting, like display resolution or date and time, affects the whole device.")
M(5, "ch5_old_tablet", ["2.9.2"], "An app runs slowly and crashes on an old tablet but works fine on a new one. What is the most likely cause?",
  ["The old tablet has less memory, a slower processor, or an older OS than the app needs", "The app is too new to be slow", "The tablet's case is the wrong color", "The Wi-Fi password is too long"],
  "Apps list minimum requirements. Older devices may not have enough RAM or processing power, or may not get the OS version the app needs.")

# ---------- Chapter 6: Cloud Computing
M(6, "ch6_onedrive_acct", ["6.2.2"], "What do you need to use OneDrive?",
  ["A Microsoft account and an internet connection", "An Apple ID only", "A CD drive", "A printer"],
  "OneDrive is Microsoft's cloud storage. You sign in with a Microsoft account (Outlook.com, school, or work account).")
M(6, "ch6_icloud", ["6.5.2"], "Which cloud storage service is built into iPhones and uses your Apple ID?",
  ["iCloud", "Dropbox", "OneDrive", "Google Drive"],
  "iCloud backs up and syncs photos, contacts, and files across Apple devices. Dropbox, OneDrive, and Google Drive also have iPhone apps.")
M(6, "ch6_online_only", ["6.3.3"], "In File Explorer, a OneDrive file shows only a cloud icon (online-only). What happens if you try to open it with no internet?",
  ["It won't open until you reconnect, unless you first set it to Always keep on this device", "It opens normally from the cloud", "It is deleted", "It opens in the Recycle Bin"],
  "Online-only files save space on your drive but need the internet. Mark important files Always keep on this device to use them offline.")
T(6, "ch6_sync_delete", ["6.3.3"], "If you delete a synced file from the OneDrive folder on your laptop, it is also deleted from OneDrive online and from your other synced devices.", True,
  "Sync keeps every copy the same, including deletes. You can usually get it back from the OneDrive website's Recycle bin for a limited time.")
M(6, "ch6_view", ["5.1.5"], "You share a cloud document so your teacher can read it but not change it. Which sharing setting should you choose?",
  ["Can view", "Can edit", "Owner", "Make it public on social media"],
  "View-only links let people read and download. Edit links let them change the file. Pick the lowest access people need.")
M(6, "ch6_share_big", ["5.1.5", "5.1.2"], "You need to send a classmate a 2 GB video. Email won't accept it. What's the easiest choice?",
  ["Upload it to cloud storage and send a share link", "Print it out", "Paste it into a text message", "Email it 100 times"],
  "Email attachments are usually limited to about 20 to 25 MB. Cloud services like OneDrive, Google Drive, or Dropbox let you share a link instead.")
M(6, "ch6_notifs", ["1.6.2"], "Your phone buzzes all day with alerts from games you rarely play. What is the best fix?",
  ["Go to Settings › Notifications and turn off alerts for those apps", "Turn the phone off for good", "Delete your contacts", "Factory reset the phone"],
  "Each app's notifications can be turned on or off, or set to silent, in the phone's Settings.")
C(6, "ch6_need", ["6.1.2", "6.2.2"], "Which TWO things do you need to use cloud storage? (Choose 2.)",
  ["An internet connection", "An account with the cloud provider", "A CD or DVD drive", "A printer"], 2,
  "Cloud storage lives on the provider's servers, so you need to get online and sign in to your account.")

# ---------- Chapter 7: Security and Maintenance
M(7, "ch7_adware", ["7.2.1"], "Ads keep popping up on your computer even when your web browser is closed. Which type of malware is most likely the cause?",
  ["Adware", "Firmware", "A firewall", "A driver"],
  "Adware shows unwanted ads and often comes bundled with free downloads. An antivirus or anti-malware scan can remove it.")
M(7, "ch7_reset_first", ["4.3.4"], "What should you do BEFORE you factory reset your phone?",
  ["Back up your photos, contacts, and files", "Install more apps", "Change your wallpaper", "Turn on Airplane mode and leave it on"],
  "A factory reset erases your personal data, settings, and apps, returning the phone to how it left the factory. Anything not backed up is gone.")
T(7, "ch7_reset_apps", ["4.3.4"], "After a factory reset, the apps you installed yourself are still on the device.", False,
  "A factory reset removes apps you added and your personal data. You reinstall apps afterward, often from your account's backup.")
M(7, "ch7_restore_point", ["4.3.3", "4.3.1"], "Which statement about a Windows System Restore point is TRUE?",
  ["It rolls back system files, drivers, and settings, but it is not a backup of your personal files", "It is a full backup of all your photos and documents", "It deletes all your files", "It only works on phones"],
  "System Restore undoes system changes like a bad driver or update. You still need File History or another backup for your documents and photos.")
M(7, "ch7_trouble_first", ["3.13.1"], "Your wireless mouse suddenly stops working. What should you try FIRST?",
  ["Check the batteries and the USB receiver, then restart if needed", "Reinstall Windows", "Buy a new computer", "Call the internet company"],
  "Start with the simple things: power, cables, connections, and a restart. Most problems are solved before you need advanced fixes.")
M(7, "ch7_describe", ["3.13.2"], "Which is the most helpful way to describe a problem to the help desk?",
  ["\"Since this morning, Excel closes with an error message when I open my budget file. I already restarted.\"", "\"My computer is broken.\"", "\"Nothing works.\"", "\"It's doing the thing again.\""],
  "Say what happened, when it started, any exact error message, and what you already tried. Clear details get faster help.")
M(7, "ch7_public", ["7.4.2", "7.4.6"], "You used a library computer to check your email. What should you do before you leave?",
  ["Sign out of your account and close the browser, and never let it save your password", "Leave it signed in for the next person", "Turn off the monitor only", "Write your password on a sticky note for next time"],
  "On public computers, always sign out, close the browser, and don't save passwords. Private (InPrivate or Incognito) windows help too.")
T(7, "ch7_pw_share", ["7.1.1"], "It's fine to share your password with a classmate if they promise not to tell anyone.", False,
  "Passwords should never be shared. Anything done with your account is traced to you. If someone needs access, they should get their own account.")
C(7, "ch7_protect", ["7.5.1", "7.6.1"], "Which TWO tools help protect your computer from malware and network attacks? (Choose 2.)",
  ["Antivirus software", "A firewall", "A screen saver", "A larger monitor"], 2,
  "Antivirus finds and removes malware. A firewall blocks unwanted network traffic. Keep both turned on and updated.")
