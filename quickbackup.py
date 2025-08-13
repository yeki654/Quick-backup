#!/usr/bin/env python3
import os
import sys
import time
import base64
import subprocess
from colorama import Fore, Style, init
init(autoreset=True)
DEFAULT_PASSWORD = "QuickBackup"
def clear():
    os.system("clear")
def logo():
    clear()
    print(Fore.CYAN + "╔" + "═"*50 + "╗")
    print(Fore.GREEN + "║" + " " * 16 + "🔥 QuickBackup Tool 🔥" + " " * 16 + "║")
    print(Fore.CYAN + "╚" + "═"*50 + "╝")
    print()
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
def find_external_mounts():
    mounts = []
    storage_dir = "/storage"
    if os.path.exists(storage_dir):
        for name in os.listdir(storage_dir):
            p = os.path.join(storage_dir, name)
            if name in ("emulated", "self"):
                continue
            if os.path.ismount(p):
                mounts.append(p)
    common = ["/mnt/media_rw", "/mnt/sdcard", "/sdcard"]
    for c in common:
        if os.path.exists(c) and os.path.ismount(c) and c not in mounts:
            mounts.append(c)
    return mounts
def select_storage(purpose="backup"):
    print(Fore.YELLOW + f"Select storage for {purpose}:")
    print(Fore.YELLOW + "1) Internal Storage (/sdcard)")
    print(Fore.YELLOW + "2) Termux Home (~)")
    externals = find_external_mounts()
    if externals:
        print(Fore.YELLOW + "3) External SD Card (detected)")
    else:
        print(Fore.YELLOW + "3) External SD Card (not detected)")
    choice = input(Fore.CYAN + "[?] Enter 1, 2, or 3: ").strip()
    if choice == "1":
        return "/sdcard"
    elif choice == "2":
        return os.path.expanduser("~")
    elif choice == "3":
        if externals:
            if len(externals) == 1:
                return externals[0]
            else:
                print(Fore.CYAN + "[?] Detected multiple external mounts:")
                for idx, m in enumerate(externals, 1):
                    print(Fore.MAGENTA + f"{idx}) {m}")
                sel = input(Fore.CYAN + "[?] Choose number: ").strip()
                try:
                    sel_i = int(sel) - 1
                    return externals[sel_i]
                except Exception:
                    print(Fore.RED + "[!] Invalid selection, defaulting to /sdcard")
                    return "/sdcard"
        else:
            print(Fore.RED + "[!] External SD card not found, defaulting to /sdcard")
            return "/sdcard"
    else:
        print(Fore.RED + "[!] Invalid choice, defaulting to /sdcard")
        return "/sdcard"
def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass
def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return (result.returncode, result.stdout.strip(), result.stderr.strip())
    except subprocess.CalledProcessError as e:
        return (e.returncode, e.stdout.strip() if e.stdout else "", e.stderr.strip() if e.stderr else "")
def create_rar_with_password(src_path, out_rar, password):
    print(Fore.GREEN + "[+] Compressing into RAR with password...")
    if password is None or password == "":
        password = DEFAULT_PASSWORD
    if not os.path.exists(src_path):
        print(Fore.RED + f"[!] Source path does not exist: {src_path}")
        return False
    if shutil_which("rar"):
        cmd = f"rar a -r -p\"{password}\" \"{out_rar}\" \"{src_path}\""
        code, out, err = run_cmd(cmd)
        if code == 0:
            return True
        else:
            print(Fore.RED + "[!] RAR creation failed:", err)
            return False
    elif shutil_which("7z"):
        cmd = f"7z a -t7z -p\"{password}\" -mhe=on \"{out_rar}\" \"{src_path}\""
        code, out, err = run_cmd(cmd)
        if code == 0:
            return True
        else:
            print(Fore.RED + "[!] 7z creation failed:", err)
            return False
    else:
        print(Fore.RED + "[!] Neither 'rar' nor '7z' found on system. Please run install.sh to install 'rar' or 'p7zip'.")
        return False
def shutil_which(name):
    from shutil import which
    return which(name)
def base64_encode_file(src_file, out_b64):
    print(Fore.GREEN + "[+] Base64-encoding archive...")
    try:
        with open(src_file, "rb") as f_in, open(out_b64, "wb") as f_out:
            data = f_in.read()
            b = base64.b64encode(data)
            f_out.write(b)
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Base64 encoding failed: {e}")
        return False
def base64_decode_file(src_b64, out_file):
    print(Fore.GREEN + "[+] Decoding base64 to archive...")
    try:
        with open(src_b64, "rb") as f_in, open(out_file, "wb") as f_out:
            b = base64.b64decode(f_in.read())
            f_out.write(b)
        return True
    except Exception as e:
        print(Fore.RED + f"[!] Base64 decode failed: {e}")
        return False
def extract_rar_with_password(rar_file, dest, password):
    if password is None or password == "":
        password = DEFAULT_PASSWORD
    print(Fore.GREEN + "[+] Extracting archive (this may ask for permission) ...")
    if shutil_which("unrar"):
        cmd = f"unrar x -y -p\"{password}\" \"{rar_file}\" \"{dest}\""
        code, out, err = run_cmd(cmd)
        if code == 0:
            return True
        else:
            print(Fore.RED + f"[!] unrar failed: {err}")
            return False
    elif shutil_which("7z"):
        cmd = f"7z x -y -p\"{password}\" \"{rar_file}\" -o\"{dest}\""
        code, out, err = run_cmd(cmd)
        if code == 0:
            return True
        else:
            print(Fore.RED + f"[!] 7z extract failed: {err}")
            return False
    else:
        print(Fore.RED + "[!] Neither 'unrar' nor '7z' found. Install them via install.sh.")
        return False
def ask_password(prompt):
    try:
        import getpass
        p = getpass.getpass(prompt)
        return p
    except Exception:
        return input(prompt)
def backup_flow():
    src = select_storage("backup")
    sub = input(Fore.CYAN + "[?] Enter path or subfolder to backup (enter for root of selected storage): ").strip()
    if sub:
        src_path = os.path.join(src, sub) if not os.path.isabs(sub) else sub
    else:
        src_path = src
    if not os.path.exists(src_path):
        print(Fore.RED + "[!] Path not found: " + src_path)
        return
    default_name = f"backup_{time.strftime('%Y%m%d_%H%M%S')}.rar"
    out_name = input(Fore.CYAN + f"[?] Enter output filename (default: {default_name}): ").strip()
    if not out_name:
        out_name = default_name
    if not out_name.lower().endswith(".rar"):
        out_name = out_name + ".rar"
    out_dir = input(Fore.CYAN + "[?] Enter directory to save backup (press enter to save in current dir): ").strip()
    if out_dir:
        ensure_dir(out_dir)
        out_rar = os.path.join(out_dir, out_name)
    else:
        out_rar = os.path.abspath(out_name)
    pwd = ask_password(Fore.CYAN + "[?] Enter password for RAR (leave empty for default): ")
    if not pwd:
        pwd = DEFAULT_PASSWORD
        print(Fore.YELLOW + f"[!] Using default password: {pwd}")
    print(Fore.GREEN + "[+] Starting backup...")
    tiny_anim("Preparing...", 0.8)
    progress_bar(1.0)
    ok = create_rar_with_password(src_path, out_rar, pwd)
    if not ok:
        print(Fore.RED + "[!] Archive creation failed.")
        return
    out_b64 = out_rar + ".b64"
    ok2 = base64_encode_file(out_rar, out_b64)
    if ok2:
        try:
            os.remove(out_rar)
        except Exception:
            pass
        print(Fore.GREEN + f"[✓] Backup complete: {out_b64}")
    else:
        print(Fore.RED + "[!] Backup encoding failed.")
def restore_flow():
    src = select_storage("restore")
    b64_path = input(Fore.CYAN + "[?] Enter path to .b64 backup file: ").strip()
    if not os.path.exists(b64_path):
        print(Fore.RED + "[!] File not found: " + b64_path)
        return
    tmp_rar = os.path.join("/data/data", "tmp_quickbackup_restore.rar")
    if os.path.exists(tmp_rar):
        try:
            os.remove(tmp_rar)
        except Exception:
            pass
    ok = base64_decode_file(b64_path, tmp_rar)
    if not ok:
        print(Fore.RED + "[!] Failed to decode backup.")
        return
    pwd = ask_password(Fore.CYAN + "[?] Enter password for RAR (leave empty for default): ")
    if not pwd:
        pwd = DEFAULT_PASSWORD
        print(Fore.YELLOW + f"[!] Using default password: {pwd}")
    ensure_dir(src)
    progress_bar(1.5)
    ok2 = extract_rar_with_password(tmp_rar, src, pwd)
    try:
        os.remove(tmp_rar)
    except Exception:
        pass
    if ok2:
        print(Fore.GREEN + f"[✓] Restore complete to: {src}")
    else:
        print(Fore.RED + "[!] Restore failed. Check password and archive.")
def main_menu():
    while True:
        logo()
        print(Fore.MAGENTA + "1) Backup Files")
        print(Fore.MAGENTA + "2) Restore Backup")
        print(Fore.MAGENTA + "3) Exit")
        choice = input(Fore.CYAN + "[?] Select option: ").strip()
        if choice == "1":
            backup_flow()
            input(Fore.CYAN + "\nPress Enter to return to menu...")
        elif choice == "2":
            restore_flow()
            input(Fore.CYAN + "\nPress Enter to return to menu...")
        elif choice == "3":
            print(Fore.CYAN + "Exiting... ⚡")
            break
        else:
            print(Fore.RED + "[!] Invalid option.")
            time.sleep(0.6)
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n" + Fore.CYAN + "Exiting... bye.")
