# coderat

[![HitCount](https://hits.dwyl.com/realb3y/RealBey/ThisIsNotRat.svg?style=flat-square)](http://hits.dwyl.com/realb3y/RealBey/ThisIsNotRat)

<p align="center">
👀 Control your Windows computer from Telegram (and many advanced features)! 👀
<br>
<a href="https://ibb.co/SRWX61h"><img src="https://i.ibb.co/J50Rcbf/ideogram-15.jpg" alt="ideogram-15" border="0"></a>
</p>

---

## ⚙️ INSTALLATION

```sh
pip install -r requirements.txt
```

## 🤖 BOT SETUP

Get your Telegram Bot API token and paste it in `tinar.py` or `tinar_super.py` where indicated.

## 🏃🏼 RUN

```sh
python tinar.py
# or for advanced features:
python tinar_super.py
```

---

## 📣 Commands & Features 📣

**General:**
- `/start` — Show intro and available commands
- `/help` — Show detailed help for all commands

**File & System:**
- `/screen` — Capture screenshot 🖵
- `/sys` — Get system information ℹ️
- `/ip` — Get public IP address 📟
- `/cd [folder]` — Change working directory 🗂️
- `/ls` — List files/folders in current directory 🗂️
- `/upload [path]` — Send file at given path 📤
- `/download [url] [dest]` — Download file from internet to path 🌐
- `/find [filename]` — Search for file by name 🔍

**Security & Control:**
- `/crypt [path]` — Encrypt folder/files (secure delete originals) 🔒
- `/decrypt [path]` — Decrypt folder/files 🔓
- `/lock` — Lock session (Windows/Mac/Linux) 🔑
- `/shutdown` — Shutdown system 🙅
- `/schedule_shutdown [seconds]` — Schedule a shutdown timer ⏳
- `/restart` — Restart system 🔄
- `/wifi` — Get WiFi SSID & password (Windows only) 📶

**Media & Devices:**
- `/webcam` — Take webcam photo 📷
- `/gifwebcam` — 2-second webcam GIF 🎥
- `/speech [lang] [text]` — Text-to-speech (TTS) 💬
- `/clipboard` — Read clipboard content 📋
- `/volume [up/down/mute]` — Control system volume 🔊

**System Stats:**
- `/disk` — Disk usage info 💾
- `/stats` — CPU & RAM usage 📊

**Pro & Utilities:**
- `/shell` — Enter remote shell mode (type `exit` to leave) 🖬
- `/genpass [length]` — Generate secure password 🔑
- `/note [save/get/del] [text]` — Save, retrieve, or delete secure notes 📓
- `/history` — Show your command history 📜

---

## 💡 Usage Tips

- All commands are run on your computer—keep your bot token secret!
- Some features may be OS-specific (see `/wifi`, `/volume`, `/lock`).
- You can extend functionality in `tinar.py` for even more features.
- Try `/help` in chat for live command reference!

---

## DEMO

[![Demo Video](https://img.youtube.com/vi/72259af5-b9ea-4c1e-8ae4-3bcc58eca116/0.jpg)](https://github.com/TheBwof/Coderat/blob/main/266782600-72259af5-b9ea-4c1e-8ae4-3bcc58eca116.mp4)

---

<span style="color: green;"><b>Note:</b> This tool is for educational and personal remote control. Use responsibly!</span>
