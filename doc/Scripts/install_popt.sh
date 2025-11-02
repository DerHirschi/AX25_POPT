#!/bin/bash
# AX25_PoPT Universal-Installer für ALLE Linux-Systeme
# Funktioniert auf Ubuntu, Debian, Fedora, Arch, Raspberry Pi OS, etc.
# Erstellt auch update_popt.sh für automatische Updates
# by Grok3 AI

set -e

echo "🚀 AX25_PoPT Installation für Linux (alle DEs)"
echo "=============================================="

# 1. Git installieren (falls nicht vorhanden)
echo "🔍 Prüfe git..."
if ! command -v git &> /dev/null; then
    echo "❌ git nicht gefunden → installiere mit Paketmanager..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y git
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y git
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm git
    elif command -v zypper &> /dev/null; then
        sudo zypper install -y git
    else
        echo "❌ Kein bekannter Paketmanager gefunden! Bitte git manuell installieren."
        exit 1
    fi
    echo "✅ git installiert"
else
    echo "✅ git bereits vorhanden"
fi

# 2. Projektordner prüfen + klonen
PROJECT_DIR="AX25_PoPT"
REPO_URL="https://github.com/DerHirschi/AX25_POPT.git"

if [ ! -d "$PROJECT_DIR" ]; then
    echo "📥 Ordner $PROJECT_DIR nicht gefunden → klone von GitHub..."
    git clone "$REPO_URL" "$PROJECT_DIR"
    echo "✅ Repo geklont → wechsle in $PROJECT_DIR"
    cd "$PROJECT_DIR"
else
    echo "📁 Ordner $PROJECT_DIR gefunden → verwende vorhandenen"
    cd "$PROJECT_DIR"
fi

# 3. Prüfe PoPT.py
if [ ! -f "PoPT.py" ]; then
    echo "❌ PoPT.py nicht gefunden! Klonen fehlgeschlagen."
    exit 1
fi
echo "✅ PoPT.py gefunden"

# 4. Python 3.10+ prüfen
#echo "🔍 Prüfe Python-Version (mindestens 3.10)..."
#PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0")
#PYTHON_MAJOR=$(echo "$PYTHON_VER" | cut -d. -f1)
#PYTHON_MINOR=$(echo "$PYTHON_VER" | cut -d. -f2)

#if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 10 ]; then
#    echo "❌ Python 3.10+ erforderlich!"
#    echo "Aktuell: Python $PYTHON_VER"
#    echo ""
#    echo "💡 Lösung:"
#    echo "   - Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
#    echo "   - Fedora: sudo dnf install python3.11"
#    echo "   - Arch: sudo pacman -S python311"
#    exit 1
#fi
#echo "✅ Python $PYTHON_VER → alles klar!"

# 5. Systemabhängigkeiten (universell)
echo "📦 Installiere Systempakete..."
if command -v apt &> /dev/null; then
    sudo apt install -y \
        python3-tk python3-pil python3-pil.imagetk python3-matplotlib \
        python3-pip python3-venv wget unzip libnotify-bin
elif command -v dnf &> /dev/null; then
    sudo dnf install -y \
        python3-tkinter python3-pillow python3-pillow-tk python3-matplotlib \
        python3-pip python3-virtualenv wget unzip libnotify
elif command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm \
        tk python-pillow python-matplotlib python-pip python-virtualenv wget unzip libnotify
elif command -v zypper &> /dev/null; then
    sudo zypper install -y \
        python3-tk python3-Pillow python3-matplotlib python3-pip python3-virtualenv wget unzip libnotify4
else
    echo "⚠️ Unbekannter Paketmanager. Bitte Abhängigkeiten manuell installieren:"
    echo "   python3-tk, python3-pil, python3-matplotlib, python3-venv, wget, unzip"
    read -p "Drücke Enter, um fortzufahren (Risiko auf eigene Gefahr)..."
fi

# 6. Virtuelle Umgebung
echo "🌍 Erstelle virtuelle Umgebung (venv)..."
python3 -m venv venv
echo "✅ venv erstellt"

# 7. Python-Pakete
echo "📥 Installiere Python-Abhängigkeiten..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Alle Python-Pakete installiert"

# 8. Start-Script
echo "📝 Erstelle start_popt.sh..."
cat > start_popt.sh << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "🚀 Starte AX25_PoPT..."
cd "$SCRIPT_DIR"
source venv/bin/activate
python PoPT.py
deactivate 2>/dev/null || true
EOF
chmod +x start_popt.sh
echo "✅ start_popt.sh erstellt"

# 9. Optional: awthemes – fehlertolerant!
echo ""
echo "🎨 Möchtest du das schöne awthemes-Design installieren?"
echo "   (verbessert die Optik von PoPT)"
read -p "   [j/N]: " -r REPLY
echo

if [[ $REPLY =~ ^[JjYy]$ ]]; then
    echo "📥 Lade awthemes-10.4.0.zip herunter..."
    mkdir -p data

    set +e
    wget --quiet --timeout=20 --tries=2 \
        -O awthemes-10.4.0.zip \
        "https://sourceforge.net/projects/tcl-awthemes/files/awthemes/10.4.0/awthemes-10.4.0.zip/download"
    WGET_EXIT=$?
    set -e

    if [ $WGET_EXIT -eq 0 ] && [ -f "awthemes-10.4.0.zip" ] && unzip -t awthemes-10.4.0.zip >/dev/null 2>&1; then
        echo "📦 Entpacke in data/..."
        unzip -o awthemes-10.4.0.zip -d data/
        rm awthemes-10.4.0.zip
        echo "✅ awthemes installiert – sieht jetzt top aus!"
    else
        echo "⚠️ Download fehlgeschlagen (404, Timeout, etc.)"
        echo "   awthemes wird übersprungen – PoPT funktioniert trotzdem!"
        [ -f "awthemes-10.4.0.zip" ] && rm -f awthemes-10.4.0.zip
    fi
else
    echo "⏭️ awthemes übersprungen"
fi

# 10. Desktop-Icon – XDG-konform (alle DEs!)
echo "🖥️ Erstelle Desktop-Verknüpfung (XDG-konform)..."
XDG_APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$XDG_APPS_DIR"

cat > "$XDG_APPS_DIR/ax25-popt.desktop" << EOF
[Desktop Entry]
Name=AX25 PoPT
Comment=Paket-Radio Terminal für AX.25
Exec=$(pwd)/start_popt.sh
Icon=$(pwd)/popt.png
Terminal=true
Type=Application
Categories=Network;HamRadio;
StartupNotify=true
EOF

# Fallback-Icon
if [ ! -f "popt.png" ]; then
    echo "⚠️ Kein popt.png → nutze Standard-Icon"
    sed -i 's|Icon=.*|Icon=utilities-terminal|' "$XDG_APPS_DIR/ax25-popt.desktop"
fi

# Aktualisiere Desktop-Datenbank
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$XDG_APPS_DIR" 2>/dev/null || true
fi

# Optional: Kopie auf Desktop (für Desktop-Umgebungen, die es erlauben)
DESKTOP_DIR="$HOME/Desktop"
if [ -d "$DESKTOP_DIR" ] && [ "$XDG_CURRENT_DESKTOP" != "KDE" ]; then
    cp "$XDG_APPS_DIR/ax25-popt.desktop" "$DESKTOP_DIR/AX25_PoPT.desktop"
    chmod +x "$DESKTOP_DIR/AX25_PoPT.desktop"
    echo "✅ Desktop-Kopie erstellt (für direkten Zugriff)"
fi

echo "✅ Desktop-Icon installiert (Menü + ggf. Desktop)"

# 11. Update-Script erstellen
echo "🔄 Erstelle update_popt.sh..."
cat > update_popt.sh << 'EOF'
#!/bin/bash
# AX25_PoPT Update-Script
# Zieht neueste Version von GitHub (master oder dev)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "🔄 Update AX25_PoPT..."
echo "Aktueller Branch: $(git branch --show-current)"

# Backup der aktuellen venv (Sicherheit)
if [ -d "venv" ]; then
    mv venv venv_backup_$(date +%Y%m%d_%H%M%S)
    echo "💾 venv gesichert als venv_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Branch-Auswahl
echo ""
echo "Welchen Branch möchtest du updaten?"
echo "   1) master (stable)"
echo "   2) dev (Entwicklung)"
read -p "   Wähle [1/2]: " -r CHOICE
echo

case $CHOICE in
    1)
        BRANCH="master"
        ;;
    2)
        BRANCH="dev"
        ;;
    *)
        echo "❌ Ungültige Auswahl. Verwende master."
        BRANCH="master"
        ;;
esac

# Prüfe, ob Branch existiert
if ! git show-ref --verify --quiet refs/heads/$BRANCH; then
    echo "⚠️ Branch $BRANCH nicht lokal vorhanden → fetch remote..."
    git fetch origin
fi

if git show-ref --verify --quiet refs/heads/$BRANCH; then
    echo "🔀 Wechsle zu $BRANCH und update..."
    git checkout $BRANCH
    git pull origin $BRANCH
    echo "✅ Update von $BRANCH abgeschlossen!"
else
    echo "❌ Branch $BRANCH nicht verfügbar auf remote. Verwende master."
    git checkout master
    git pull origin master
    echo "✅ Update von master abgeschlossen!"
fi

# Neu installieren (venv + requirements)
echo "📦 Neu installiere venv und Abhängigkeiten..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

# Aktualisiere .desktop-Pfade (falls Ordner geändert)
XDG_APPS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
if [ -f "$XDG_APPS_DIR/ax25-popt.desktop" ]; then
    sed -i "s|Exec=.*|Exec=$(pwd)/start_popt.sh|" "$XDG_APPS_DIR/ax25-popt.desktop"
    sed -i "s|Icon=.*|Icon=$(pwd)/popt.png|" "$XDG_APPS_DIR/ax25-popt.desktop"
    update-desktop-database "$XDG_APPS_DIR" 2>/dev/null || true
fi

echo ""
echo "🎉 Update abgeschlossen! Starte mit ./start_popt.sh neu."
echo "💡 Tipp: Lösche alte venv_Backups manuell, wenn nicht mehr benötigt."
EOF
chmod +x update_popt.sh
echo "✅ update_popt.sh erstellt"

# 12. Benachrichtigung (optional)
if command -v notify-send &> /dev/null; then
    notify-send "AX25 PoPT" "Installation abgeschlossen! Starte über das Menü oder ./start_popt.sh" --icon=dialog-information
fi

# 13. Fertig!
echo ""
echo "✅ Installation abgeschlossen!"
echo ""
echo "🚀 So startest du PoPT:"
echo "   ./start_popt.sh"
echo "   oder: Über das Anwendungsmenü → 'AX25 PoPT'"
echo "   (ggf. auch auf dem Desktop)"
echo ""
echo "🔄 Update:"
echo "   ./update_popt.sh  (fragt nach master/dev)"
echo ""
echo "💡 AX.25 (optional):"
echo "   sudo apt install ax25-tools libax25-dev direwolf   (Debian/Ubuntu)"
echo "   Konfiguriere /etc/ax25/axports"
echo ""
echo "Viel Spaß mit AX25_PoPT! 🎉"
