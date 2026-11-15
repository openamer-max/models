#!/data/data/com.termux/files/usr/bin/bash
# OpenAmer direkt auf dem Android-Geraet installieren (Termux-Userspace).
#
# Warum Termux und keine normale APK: der Agent braucht ein PTY, ein echtes
# Dateisystem und Python 3.11+. Android-Apps bekommen ohne Linux-Userspace kein
# PTY - deshalb laeuft der Agent hier WIRKLICH auf dem Telefon, statt nur
# ferngesteuert zu werden.
#
# Geprueft: alle 27 Abhaengigkeiten liegen als aarch64-Rad vor (manylinux2014),
# es muss also nichts auf dem Geraet kompiliert werden.
#
# Was laeuft: Chat, Skills, Erinnerungen, Zeitplaene, Dateien, Shell, Git.
# Was nicht laeuft: Desktop-Oberflaeche (Electron gibt es nicht fuer Android),
# Browser-Steuerung ueber CDP, GPU-Inferenz. Grosse Modelle sind auf der CPU
# unbrauchbar; realistisch ist die kleinste Stufe.
set -u

REPO="https://github.com/openamer-max/openamer"
ZIEL="$HOME/openamer"

echo "=== OpenAmer auf Android (Termux)"
echo

echo "[1/4] Pakete"
pkg update -y >/dev/null 2>&1 || true
pkg install -y python git >/dev/null 2>&1 || echo "  Warnung: pkg install unvollstaendig"
python -c "import sys; print('  Python', sys.version.split()[0])"

echo "[2/4] Quellcode"
if [ -d "$ZIEL" ]; then
    git -C "$ZIEL" pull --ff-only 2>&1 | tail -1
else
    git clone --depth 1 "$REPO" "$ZIEL" 2>&1 | tail -1 || {
        echo "  FEHLER: Repository nicht erreichbar"; exit 1; }
fi

echo "[3/4] Installieren (dauert einige Minuten)"
cd "$ZIEL" || exit 1
# Der Testlauf zeigte: ohne OPENAMER_HOME raet der Agent sein Datenverzeichnis
# und warnt, dass Daten am falschen Ort landen koennen. Unter Termux ist
# $HOME/.openamer der richtige Ort - deshalb ausdruecklich setzen.
export OPENAMER_HOME="${OPENAMER_HOME:-$HOME/.openamer}"
mkdir -p "$OPENAMER_HOME"
echo "  Datenverzeichnis: $OPENAMER_HOME"
pip install --upgrade pip >/dev/null 2>&1
pip install -e . 2>&1 | tail -4

echo "[4/4] Probe"
if command -v openamer >/dev/null 2>&1; then
    openamer --version 2>&1 | head -1
    echo
    echo "  Fertig. Start:   openamer chat"
    echo "  Hilfe:           openamer --help"
    echo
    echo "  Laeuft: Chat, Skills, Erinnerungen, Zeitplaene, Dateien, Shell, Git."
    echo "  Laeuft nicht: Desktop-Oberflaeche, Browser-Steuerung, GPU."
    echo "  Modell: kleinste Stufe (0,6B) ist auf der CPU das einzig Sinnvolle."
else
    echo "  FEHLER: 'openamer' nicht gefunden."
    echo "  Haeufigste Ursache: eine Abhaengigkeit ohne ARM64-Rad - Ausgabe oben pruefen."
    echo "  Alternative: pip install --no-build-isolation -e ."
fi
