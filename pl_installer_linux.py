#!/usr/bin/env python3

import subprocess
import sys
import os
import json

home = os.path.expanduser("~")

msg = "\nWelcome to the Profile Launcher installation, please enter the profiles path of your browser.\nThis is because the addon cant get this kind of information and must be set manually.\nOn linux profiles usually are on home or in ~/.config, example: ~/.zen or ~/.config/mozilla/firefox\nYou can go to about:profiles on your browser to see the paths. The path you input must be were the profiles.ini file is.\nEnter a empty line if you use zen: "
PROFILES_DIR = input(msg)

msg = "\n\nPlease input the executable path of your browser, example: ~/.local/share/applications/zen/zen or /usr/lib/firefox/firefox\nIf you installed it normally it should have added to the path so you can use that instead.\nUsually is the name of the browser in lowercase, example: firefox or librewolf\nEnter a empty line if you have the default location for Zen shown previously: "
BROWSER_DIR = input(msg)

msg = "\n\nAlmost finished, please enter a identificator for the browser, example: zen or firefox01\nThis ID will be needed on the popup of the addon.\nThis is because the script will point to only one file making it impossible to run on multiple firefox forks at the same time. With the id each script will be separated.\nDo this if you have multiple browsers and want to use the extension on more than one of them. With this you can also open one profile from other browser if both have the addon.\nIf thats not the case you can enter a empty line: "
BROWSER_ID = input(msg)

if BROWSER_ID != "":
    BROWSER_ID = "_" + BROWSER_ID

manifest = {
    "name": f"profile_launcher{BROWSER_ID}",
    "description": "Launch firefox with selected profile",
    "path": f"{home}/.local/share/applications/profile_launcher/profile_launcher{BROWSER_ID}.py",
    "type": "stdio",
    "allowed_extensions": ["profile_launcherv1@hyseki.com"]
}

native_dir = os.path.expanduser("~/.mozilla/native-messaging-hosts")

os.makedirs(native_dir, exist_ok=True)
file = os.path.join(native_dir, f"profile_launcher{BROWSER_ID}.json")

with open(file, "w") as f:
    json.dump(manifest, f, indent=2)

this_file = os.path.abspath(__file__)
with open(this_file, "r") as f:
    s = f.read().split("//--//PROFILE_LAUNCHER_CONTENT//--//")[2]

script_dir = f"{home}/.local/share/applications/profile_launcher"
os.makedirs(script_dir, exist_ok=True)
script = os.path.join(script_dir, f"profile_launcher{BROWSER_ID}.py")
with open(script, "w") as f:
    s = s.split("# //SEPARATOR_FOR_PATH//")
    f.write(s[0])
    if PROFILES_DIR == "":
        PROFILES_DIR = "~/.zen/"
    if BROWSER_DIR == "":
        BROWSER_DIR = "~/.local/share/applications/zen/zen"
    f.write(f"PROFILES_DIR = os.path.expanduser(\"{PROFILES_DIR}\")\n")
    f.write(f"BROWSER_DIR = os.path.expanduser(\"{BROWSER_DIR}\")\n")
    f.write(s[1])

os.chmod(script, 0o755)

quit()

# //--//PROFILE_LAUNCHER_CONTENT//--//#!/usr/bin/env python3

import sys, json, os, subprocess

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
        subprocess.Popen([BROWSER_DIR, "-P", profile])
    elif msg.get("command") == "create":
        profile = msg.get("profile")
        subprocess.Popen([BROWSER_DIR, "-CreateProfile", profile])
