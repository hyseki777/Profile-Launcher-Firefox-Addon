#!/usr/bin/env python3

import sys, json, os, subprocess

PROFILES_DIR = os.path.expanduser("~/.zen")
BROWSER_DIR = os.path.expanduser("~/.local/share/applications/zen/zen")

def list_profiles():
    return [d.split('.')[1] for d in os.listdir(PROFILES_DIR) if (os.path.isdir(os.path.join(PROFILES_DIR, d))) and ('.' in d) ]

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
