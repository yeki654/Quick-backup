#!/data/data/com.termux/files/usr/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RESET='\033[0m'
logo() {
    clear
    echo -e "${CYAN}"
    echo "================================="
    echo "   🔥 QuickBackup Installer 🔥"
    echo "================================="
    echo -e "${RESET}"
}
progress_bar() {
    bar="########################################"
    barlength=${#bar}
    i=0
    while [ $i -le $1 ]; do
        percent=$(( i * 100 / $1 ))
        filled=$(( i * barlength / $1 ))
        echo -ne "[${GREEN}${bar:0:filled}${RESET}${bar:filled}] $percent%\r"
        sleep 0.03
        ((i++))
    done
    echo
}
check_pkg() {
    if ! command -v $1 &> /dev/null
    then
        echo -e "${YELLOW}[+] Installing $1...${RESET}"
        pkg install $1 -y
    else
        echo -e "${GREEN}[+] $1 already installed.${RESET}"
    fi
}
check_python_pkg() {
    python3 -c "import $1" &> /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[+] Installing Python package: $1${RESET}"
        pip install $1
    else
        echo -e "${GREEN}[+] Python package $1 already installed.${RESET}"
    fi
}
logo
echo -e "${CYAN}[+] Applying 777 permissions to all files...${RESET}"
chmod -R 777 ./*
echo -e "${CYAN}[+] Updating Termux packages...${RESET}"
progress_bar 40
pkg update -y && pkg upgrade -y
check_pkg python
check_pkg unrar
check_pkg unzip
echo -e "${CYAN}[+] Upgrading pip...${RESET}"
pip install --upgrade pip
check_python_pkg patool
check_python_pkg pyunpack
check_python_pkg colorama
echo -e "${CYAN}[+] Setting up Termux storage...${RESET}"
termux-setup-storage
echo -e "${GREEN}[✓] Smart installation complete! Run ./run.sh to start QuickBackup.${RESET}"
