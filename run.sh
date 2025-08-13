#!/data/data/com.termux/files/usr/bin/bash
CYAN='\033[0;36m'
RESET='\033[0m'
clear
echo -e "${CYAN}"
echo "================================="
echo "      🚀 QuickBackup Runner 🚀"
echo "================================="
echo -e "${RESET}"
python3 quickbackup.py
