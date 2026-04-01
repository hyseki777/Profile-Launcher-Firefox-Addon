import sys
import os
import json
import winreg

home = os.path.expanduser("~")
appdata = os.getenv("APPDATA")

msg = "\nWelcome to the Profile Launcher installation, please enter the profiles and executable directions of your browser.\nThis is because the addon cant get this kind of information and must be set manually.\nOn Windows profiles usually are on %APPDATA%, example: %APPDATA%\\zen or %APPDATA%\\Mozilla\\Firefox\nYou can go to about:profiles on your browser to see the paths. The path you input must be were the profiles.ini file is.\nEnter a empty line if you use Zen: "
PROFILES_DIR = input(msg)

msg = "\n\nPlease input the executable path of your browser, example: C:\\Program Files\\Zen Browser\\zen.exe or C:\\Program Files\\Mozilla Firefox\\firefox.exe\nEnter a empty line if you have the default location for Zen shown previously: "
BROWSER_DIR = input(msg)

msg = "\n\nAlmost finished, please enter a identificator for the browser, example: zen or firefox01\nThis ID will be needed on the popup of the addon.\nThis is because the script will point to only one file making it impossible to run on multiple firefox forks at the same time. With the id each script will be separated.\nDo this if you have multiple browsers and want to use the extension on more than one of them. With this you can also open one profile from other browser if both have the addon.\nIf thats not the case you can enter a empty line: "
BROWSER_ID = input(msg)

msg = "\n\nNOTICE: Due to limitations of firefox on windows it cant open graphical applications from the addon. This means that instead of directly opening another browser instance with the selected profile like on linux, it will open a folder and make a bat file there and you must execute it so it open the instance.\nPress enter to continue."
input(msg)

if BROWSER_ID != "":
    BROWSER_ID = "_" + BROWSER_ID

manifest = {
    "name": f"profile_launcher{BROWSER_ID}",
    "description": "Launch firefox with selected profile",
    "path": f"{home}\\AppData\\Local\\profile_launcher\\profile_launcher{BROWSER_ID}.bat",
    "type": "stdio",
    "allowed_extensions": ["profile_launcherv1@hyseki.com"]
}

native_dir = f"{home}\\AppData\\Local\\profile_launcher"
os.makedirs(native_dir, exist_ok=True)
os.makedirs(os.path.join(native_dir, "launchers"), exist_ok=True)


manifest_file = os.path.join(native_dir, f"profile_launcher{BROWSER_ID}.json")

with open(manifest_file, "w") as f:
    json.dump(manifest, f, indent=2)


with open(f"{native_dir}\\profile_launcher{BROWSER_ID}.bat", "w") as f:
    f.write("@echo off\n")
    f.write(f"python.exe {home}\\AppData\\Local\\profile_launcher\\profile_launcher{BROWSER_ID}.py")

key_path = f"SOFTWARE\\Mozilla\\NativeMessagingHosts\\profile_launcher{BROWSER_ID}"
try:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, manifest_file)
except Exception as e:
    print(f"Failed to create registry entry: {e}")

this_file = os.path.abspath(__file__)
with open(this_file, "r") as f:
    s = f.read().split("//--//PROFILE_LAUNCHER_CONTENT//--//")[2]

script_dir = f"{home}\\AppData\\Local\\profile_launcher"
os.makedirs(script_dir, exist_ok=True)
script = os.path.join(script_dir, f"profile_launcher{BROWSER_ID}.py")
with open(script, "w") as f:
    s = s.split("# //SEPARATOR_FOR_PATH//")
    f.write(s[0])
    if PROFILES_DIR == "":
        PROFILES_DIR = f"{appdata}\\zen"
    if BROWSER_DIR == "":
        BROWSER_DIR = r"C:\Program Files\Zen Browser\zen.exe"
    if BROWSER_ID == "":
        BROWSER_ID = "Default"
    PROFILES_DIR = PROFILES_DIR.replace("%APPDATA%", appdata)
    f.write(f"PROFILES_DIR = r\"{PROFILES_DIR}\"\n")
    f.write(f"BROWSER_DIR = r\"{BROWSER_DIR}\"\n")
    f.write(f"BROWSER_ID = r\"{BROWSER_ID}\"\n")
    f.write(s[1])

os.chmod(script, 0o755)

quit()

# //--//PROFILE_LAUNCHER_CONTENT//--//

import sys, json, os

# //SEPARATOR_FOR_PATH//

def list_profiles():
    profiles = []
    inBlock = False

    prof_location = os.path.join(PROFILES_DIR, "profiles.ini")
    with open(prof_location, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                block = line[1:-1]
                inBlock = "Profile" in block
            elif inBlock:
                if line.startswith("Name="):
                    profiles.append(line.split("=", 1)[1])
    return profiles


def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if len(raw_length) == 0:
        return None
    message_length = int.from_bytes(raw_length, byteorder="little")
    message = sys.stdin.buffer.read(message_length).decode("utf-8")
    return json.loads(message)


def send_message(msg):
    encoded = json.dumps(msg).encode("utf-8")
    sys.stdout.buffer.write(len(encoded).to_bytes(4, byteorder="little"))
    sys.stdout.buffer.write(encoded)
    sys.stdout.buffer.flush()


msg = read_message()
if msg:
    if msg.get("command") == "list":
        send_message({"profiles": list_profiles()})
    elif msg.get("command") == "launch":
        profile = msg.get("profile")
        try:
            with open(f"launchers\\launcher{BROWSER_ID}_{profile}.bat","w")as f:
                f.write("@echo off\n")
                f.write(f"\"{BROWSER_DIR}\" -P \"{profile}\"\n")
                f.write("cmd /c del \"%~f0\"")
            os.startfile("launchers")
            send_message({"status": "ok", "launched": profile})
        except Exception as e:
            send_message({"status": "error", "message": str(e)})
