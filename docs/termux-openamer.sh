#!/data/data/com.termux/files/usr/bin/bash
# OpenAmer auf Android - vollstaendiger Agent im Debian-Userspace.
#
# Warum Debian in proot und nicht direkt in Termux (im Emulator gemessen):
#   1. Termux laeuft auf Androids libc (bionic). manylinux-Raeder verlangen glibc
#      - pip bricht daher bei "cryptography" ab (Bau aus Rust scheitert).
#   2. Termux' Python ist 3.14, der Agent verlangt <3.14.
#   Debian in proot bringt glibc und Python 3.13: dort greifen die fertigen
#   Raeder, und der Agent startet (geprueft: v2026.11.16, Python 3.13.5).
#
# Was laeuft danach: Chat, Skills, Erinnerungen, Zeitplaene, Dateien, Shell, Git,
# Selbstkuratierung - derselbe Code wie unter Windows und Linux.
# Was nicht laeuft: Desktop-Fenster, Browser-Steuerung (CDP), computer_use.
set -u

echo "=== OpenAmer auf Android (Debian-Userspace)"
echo

echo "[1/3] proot-distro und Debian"
pkg install -y proot-distro >/dev/null 2>&1 || echo "  Warnung: proot-distro nicht installiert"
proot-distro install debian >/dev/null 2>&1 || true

echo "[2/3] Agent installieren (Debian, manylinux-Raeder)"
proot-distro login debian -- bash -c '
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3-full python3-venv git >/dev/null
cd /root
if [ ! -d openamer ]; then
  git clone --depth 1 https://github.com/openamer-max/openamer openamer
fi
cd openamer
[ -d /root/venv ] || python3 -m venv /root/venv
/root/venv/bin/pip install -q --upgrade pip
/root/venv/bin/pip install -e . 2>&1 | tail -3
'

echo "[3/3] Probe"
proot-distro login debian -- env OPENAMER_HOME=/root/.openamer \
  /root/venv/bin/openamer --version 2>&1 | head -4

echo
echo "  Fertig. Starten mit:"
echo "    proot-distro login debian -- /root/venv/bin/openamer chat"
echo
echo "  Laeuft: Chat, Skills, Erinnerungen, Zeitplaene, Dateien, Shell, Git."
echo "  Laeuft nicht: Desktop-Fenster, Browser-Steuerung, GPU."
