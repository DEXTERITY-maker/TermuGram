#!/usr/bin/env bash
# TermuGram — установщик.
# Клонировали репозиторий -> запустили install.sh -> команда TermuGram готова.
set -e

INSTALL_DIR="$HOME/.terminugram"
BIN_DIR="$HOME/.local/bin"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "======================================"
echo "  TermuGram — установка"
echo "======================================"

# 1. python3
if ! command -v python3 >/dev/null 2>&1; then
  echo "[1/4] python3 не найден. Установите:  pkg install python"
  exit 1
fi
echo "[1/4] python3: OK ($(python3 --version 2>&1))"

# 2. telethon
echo "[2/4] проверяем telethon..."
if python3 -c "import telethon" 2>/dev/null; then
  echo "      telethon уже установлен"
else
  echo "      устанавливаем telethon..."
  python3 -m pip install --user telethon 2>/dev/null || python3 -m pip install telethon
fi

# 3. файлы
echo "[3/4] копируем файлы в $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp "$SRC_DIR/demo_installer.py" "$SRC_DIR/installer.py" \
   "$SRC_DIR/main_menu.py" "$SRC_DIR/version.py" \
   "$SRC_DIR/requirements.txt" "$SRC_DIR/TermuGram" "$INSTALL_DIR/"

# 4. команда в PATH
echo "[4/4] создаём команду TermuGram в $BIN_DIR"
mkdir -p "$BIN_DIR"
cp "$INSTALL_DIR/TermuGram" "$BIN_DIR/TermuGram"
chmod +x "$BIN_DIR/TermuGram"

if ! command -v TermuGram >/dev/null 2>&1; then
  echo
  echo "      ВНИМАНИЕ: $BIN_DIR не в PATH."
  echo "      Добавьте в ~/.bashrc строку:"
  echo "      export PATH=\"$BIN_DIR:\$PATH\""
fi

echo
echo "======================================"
echo "  Готово! Запустите:  TermuGram"
echo "======================================"
