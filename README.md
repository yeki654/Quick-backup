# QuickBackup 🔥

QuickBackup is a lightweight **Termux** backup tool for Android that:
- Creates **password-protected RAR** archives of chosen folders.
- **Base64 encodes** the archive for safer transport/storage (`*.rar.b64`).
- Restores backups by decoding and extracting with the original password.
- Supports saving/restoring to:
  - Internal Storage (`/sdcard`)
  - Termux Home (`~`)
  - External SD Card (if detected)
- No root required

> ⚠️ If no password is provided at backup/restore, a default password `QuickBackup` is used.

## Features
- Colorful interactive menu and nice logo for terminal UX.
- Smart installer (`install.sh`) that checks & installs missing dependencies.
- Supports `rar`/`unrar` or `7z` as fallback.
- All operations are offline — works entirely on-device.
- Open Source (MIT) — copy, modify, distribute. Use responsibly.

## Files
- `install.sh` — smart installer (applies `chmod 777` to project files, installs deps, sets up storage).
- `run.sh` — simple launcher for the Python tool.
- `quickbackup.py` — main program (backup & restore).
- `LICENSE` — MIT license.
- `README.md` — this file.

## Installation & Usage
1. Place all files in one folder on your Termux device.
2. Than run these commands:
```bash
pkg install git
git clone https://github.com/yeki654/Quick-backup
cd Quick-backup
chmod 777 install.sh run.sh
chmod +x install.sh run.sh
bash install.sh
bash run.sh


