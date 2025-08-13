#!/usr/bin/env python3
# QuickBackup Tool — Final Termux Version
# No root required, encrypted RAR + Base64 backup
# Internal and External storage support

import os
import sys
import time
import base64
import subprocess
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

DEFAULT_PASSWORD = "QuickBackup"

# Clear screen
def clear():
    os.system("clear")

# Logo
def logo():
    clear()
    print(Fore.CYAN + "╔" + "═"*50 + "╗")
    print(Fore.GREEN + "║" + " " * 16 + "🔥 QuickBackup Tool 🔥" + " " * 16 + "║")
    print(Fore.CYAN + "╚" + "═"*50 + "╝")
    print()

# Tiny spinner animation
def tiny_anim(text, duration=0.9):
    chars = "|/-\\"
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write("\r" + text + " " + chars[i % len(chars)])
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 2) + "\r")

# Progress bar
def progress_bar(duration=2.0, width=30):
    steps = width
    delay = duration / steps
    for i in range(steps + 1):
        filled = "█" * i
        empty = "░" * (steps - i)
        pct = (i * 100) // steps
        print(f"[{filled}{empty}] {pct}%", end="\r")
        time.sleep(delay)
    print()

# Check command exists
def shutil_which(cmd):
    return any(
        os.access(os.path.join(path, cmd), os.X_OK)
        for path in os.environ["PATH"].split(os.pathsep)
    )

# Run terminal command
def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return (result.returncode, result.stdout.strip(), result.stderr.strip())
    except subprocess.CalledProcessError as e:
        return (e.returncode, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else "")

# Ensure directory exists and writeable
def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
        return os.access(path, os.W_OK)
    except Exception:
        return False

# Find external mounts (writeable only)
def find_external_mounts():
    mounts = []
    storage_dir = "/storage"
    if os.path.exists(storage_dir):
        for name in os.listdir(storage_dir):
            p = os.path.join(storage_dir, name)
            if name in ("emulated", "self"):
                continue
            if os.path.ismount(p) and os.access(p, os.W_OK):
                mounts.append(p)
    common = ["/mnt/media_rw", "/mnt/sdcard", "/sdcard"]
    for c in common:
        if os.path.exists(c) and os.path.ismount(c) and os.access(c, os.W_OK) and c not in mounts:
            mounts.append(c)
    return mounts

# Select storage path safely
def select_storage(purpose="backup"):
    print(Fore.YELLOW + f"Select storage for {purpose}:")
    print(Fore.YELLOW + "1) Internal Storage (Termux safe path)")
    print(Fore.YELLOW + "2) Termux Home (~)")
    externals = find_external_mounts()
    if externals:
        for idx, path in enumerate(externals, start=3):
            print(Fore.YELLOW + f"{idx}) External Storage ({path})")
    choice = input(Fore.CYAN + "[?] Select option (Enter=default 1): ").strip()
    if choice == "2":
        return os.path.expanduser("~")
    elif choice.isdigit() and int(choice) >= 3 and externals:
        return externals[int(choice)-3]
    else:
        # Default internal safe
        termux_shared = os.path.expanduser("~/storage/shared/QuickBackup")
        if ensure_dir(termux_shared):
            return termux_shared
        else:
            print(Fore.RED + "[!] Cannot write to internal storage. Using Home (~).")
            return os.path.expanduser("~")

# Ask password securely
def ask_password(prompt):
    try:
        import getpass
        return getpass.getpass(prompt)
    except Exception:
        return input(prompt)

# Create RAR with password
def create_rar_with_password(src_path, out_rar, password):
    if not password:
        password = DEFAULT_PASSWORD
    if not os.path.exists(src_path):
        print(Fore.RED + f"[!] Source path does not exist: {src_path}")
        return False
    if shutil_which("rar"):
        cmd = f'rar a -r -p"{password}" "{out_rar}" "{src_path}"'
        code, _, _ = run_cmd(cmd)
        return code == 0
    elif shutil_which("7z"):
        cmd = f'7z a -t7z -p"{password}" -mhe=on "{out_rar}" "{src_path}"'
        code, _, _ = run_cmd(cmd)
        return code == 0
    else:
        print(Fore.RED + "[!] No RAR or 7z command found.")
        return False

# Base64 encode/decode
def base64_encode_file(src_file, out_b64):
    try:
        with open(src_file, "rb") as f:
            data = f.read()
        with open(out_b64, "wb") as f:
            f.write(base64.b64encode(data))
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Encoding error: {e}")
        return False

def base64_decode_file(src_b64, out_file):
    try:
        with open(src_b64, "rb") as f:
            data = f.read()
        with open(out_file, "wb") as f:
            f.write(base64.b64decode(data))
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Decoding error: {e}")
        return False

# Extract RAR with password
def extract_rar_with_password(rar_file, dest, password):
    if not password:
        password = DEFAULT_PASSWORD
    ensure_dir(dest)
    if shutil_which("unrar"):
        cmd = f'unrar x -y -p"{password}" "{rar_file}" "{dest}"'
        code, _, _ = run_cmd(cmd)
        return code == 0
    elif shutil_which("7z"):
        cmd = f'7z x -y -p"{password}" "{rar_file}" -o"{dest}"'
        code, _, _ = run_cmd(cmd)
        return code == 0
    else:
        print(Fore.RED + "[!] No unrar or 7z command found.")
        return False

# Backup flow
def backup_flow():
    src = select_storage("backup")
    logo()
    print(Fore.CYAN + "[*] Backup source path (Enter=Termux default folder):")
    src_path = input(Fore.CYAN + "> ").strip()
    if not src_path:
        src_path = os.path.expanduser("~/storage/shared/QuickBackup")
    if not ensure_dir(src_path):
        print(Fore.RED + "[!] Cannot write to selected path. Using Home (~).")
        src_path = os.path.expanduser("~")
    out_rar = os.path.join(src_path, "backup.rar")
    out_b64 = os.path.join(src_path, "backup.b64")
    pwd = ask_password(Fore.CYAN + "[?] Enter password for RAR (Enter=default): ")
    if not pwd:
        pwd = DEFAULT_PASSWORD
        print(Fore.YELLOW + f"[!] Using default password: {pwd}")
    tiny_anim("Creating RAR...")
    if create_rar_with_password(src_path, out_rar, pwd):
        progress_bar()
        print(Fore.GREEN + "[✔] RAR created.")
        tiny_anim("Encoding Base64...")
        if base64_encode_file(out_rar, out_b64):
            progress_bar()
            os.remove(out_rar)
            print(Fore.GREEN + f"[✔] Backup completed: {out_b64}")
    else:
        print(Fore.RED + "[!] Backup failed.")

# Restore flow
def restore_flow():
    dest = select_storage("restore")
    logo()
    b64_path = input(Fore.CYAN + "[?] Enter path to .b64 backup file: ").strip()
    if not os.path.exists(b64_path):
        print(Fore.RED + "[!] File not found.")
        return
    tmp_rar = os.path.join(os.path.expanduser("~"), "tmp_quickbackup_restore.rar")
    if base64_decode_file(b64_path, tmp_rar):
        pwd = ask_password(Fore.CYAN + "[?] Enter password for RAR (Enter=default): ")
        if not pwd:
            pwd = DEFAULT_PASSWORD
        tiny_anim("Extracting RAR...")
        if extract_rar_with_password(tmp_rar, dest, pwd):
            progress_bar()
            os.remove(tmp_rar)
            print(Fore.GREEN + f"[✔] Restore completed to: {dest}")
        else:
            print(Fore.RED + "[!] Restore failed.")
    else:
        print(Fore.RED + "[!] Base64 decoding failed.")

# Main menu
def main_menu():
    while True:
        logo()
        print(Fore.MAGENTA + "1) Backup Files")
        print(Fore.MAGENTA + "2) Restore Backup")
        print(Fore.MAGENTA + "3) Exit")
        choice = input(Fore.CYAN + "[?] Select option: ").strip()
        if choice == "1":
            backup_flow()
        elif choice == "2":
            restore_flow()
        elif choice == "3":
            break

# Entry point
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Exiting... bye.")
