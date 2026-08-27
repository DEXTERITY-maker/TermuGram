#!/usr/bin/env bash
# TermuGram — установщик.
# Клонировали репозиторий -> запустили install.sh -> команда TermuGram готова.
#
# Установщик САМ проверяет окружение и чинит его:
#   • Termux (менеджер пакетов pkg)
#   • python3 (нужен для работы) — если нет или слишком старый, установит
#   • pip (ставится вместе с python3)
#   • telethon (движок для Telegram) — если нет или устарел, установит/обновит
#   • git (рекомендуется, для обновлений)
# Ничего вручную искать и доустанавливать не нужно — просто запустите install.sh.
set -e

INSTALL_DIR="$HOME/.terminugram"
BIN_DIR="$HOME/.local/bin"
SRC_DIR="$(cd "$(dirname "$0")" && pwd)"

MIN_PYTHON="3.8"     # минимальная версия Python (нужна для telethon)
MIN_TELETHON="1.34"  # минимальная версия telethon (см. requirements.txt)

echo "======================================"
echo "  TermuGram — установка"
echo "======================================"
echo

# ---------------------------------------------------------------------------
# [1/6] Окружение: Termux?
# ---------------------------------------------------------------------------
echo "[1/6] Проверяем окружение..."

HAS_PKG=0
if [ -n "$PREFIX" ] && command -v pkg >/dev/null 2>&1; then
  HAS_PKG=1
  echo "      Termux: обнаружен (есть менеджер пакетов pkg) ✓"
else
  echo "      ВНИМАНИЕ: Termux не обнаружен (нет команды pkg)."
  echo "      TermuGram рассчитан на Termux (Android)."
  echo "      Если python3 уже есть — продолжим; если нет, установите вручную:"
  echo "        Termux:       pkg install python git"
  echo "        Debian/Ubuntu: sudo apt install python3 python3-pip git"
fi

# ---------------------------------------------------------------------------
# Сравнение версий: вер_ge A B -> 0, если A >= B (по первым двум числам)
# ---------------------------------------------------------------------------
ver_ge() {
  python3 -c "
import sys
a = [int(x) for x in sys.argv[1].split('.')[:2]]
b = [int(x) for x in sys.argv[2].split('.')[:2]]
sys.exit(0 if a >= b else 1)
" "$1" "$2" 2>/dev/null
}

# ---------------------------------------------------------------------------
# [2/6] Python 3 + pip
# ---------------------------------------------------------------------------
echo "[2/6] Python 3 и pip..."

if command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
  if ver_ge "$PY_VER" "$MIN_PYTHON"; then
    echo "      python3 $PY_VER: OK ✓"
  else
    echo "      python3 $PY_VER: СЛИШКОМ СТАРАЯ (нужно >= $MIN_PYTHON)"
    if [ "$HAS_PKG" = "1" ]; then
      echo "      Обновляем python3 (pkg install python)..."
      pkg install -y python || { echo "      Не удалось обновить python3."; exit 1; }
      PY_VER=$(python3 --version 2>&1 | awk '{print $2}')
      echo "      python3 $PY_VER: обновлена ✓"
    else
      echo "      Установите python3 версии $MIN_PYTHON или новее и запустите install.sh снова."
      exit 1
    fi
  fi
else
  echo "      python3: НЕ НАЙДЕН — TermuGram без него не работает"
  if [ "$HAS_PKG" = "1" ]; then
    echo "      Устанавливаем python3 (pkg install python)..."
    pkg install -y python || { echo "      Не удалось установить python3."; exit 1; }
    echo "      python3: установлен ✓"
  else
    echo "      Termux не найден — установить python3 автоматически нельзя."
    echo "      Установите его и запустите install.sh снова."
    exit 1
  fi
fi

if python3 -m pip --version >/dev/null 2>&1; then
  echo "      pip $(python3 -m pip --version 2>/dev/null | awk '{print $2}'): OK ✓"
else
  echo "      pip: НЕ НАЙДЕН — пытаемся создать..."
  python3 -m ensurepip --upgrade >/dev/null 2>&1 || python3 -m ensurepip >/dev/null 2>&1 || {
    echo "      Не удалось настроить pip. В Termux:  pkg install python-pip"
    exit 1
  }
  echo "      pip: создан ✓"
fi

# ---------------------------------------------------------------------------
# [3/6] telethon (библиотека для работы с Telegram)
# ---------------------------------------------------------------------------
echo "[3/6] Библиотека telethon (движок Telegram)..."

TELETHON_VER=$(python3 -c "import telethon; print(telethon.__version__)" 2>/dev/null || true)
if [ -z "$TELETHON_VER" ]; then
  echo "      telethon: НЕ УСТАНОВЛЕНА — устанавливаем (pip)..."
  python3 -m pip install --user "telethon>=${MIN_TELETHON}" >/dev/null 2>&1 \
    || python3 -m pip install "telethon>=${MIN_TELETHON}" >/dev/null 2>&1 \
    || { echo "      Не удалось установить telethon. Проверьте интернет и повторите."; exit 1; }
  TELETHON_VER=$(python3 -c "import telethon; print(telethon.__version__)" 2>/dev/null || echo "?")
  echo "      telethon $TELETHON_VER: установлена ✓"
elif ver_ge "$TELETHON_VER" "$MIN_TELETHON"; then
  echo "      telethon $TELETHON_VER: OK ✓"
else
  echo "      telethon $TELETHON_VER: УСТАРЕЛА (нужно >= $MIN_TELETHON) — обновляем..."
  python3 -m pip install --user --upgrade "telethon>=${MIN_TELETHON}" >/dev/null 2>&1 \
    || python3 -m pip install --upgrade "telethon>=${MIN_TELETHON}" >/dev/null 2>&1 \
    || { echo "      Не удалось обновить telethon. Проверьте интернет и повторите."; exit 1; }
  TELETHON_VER=$(python3 -c "import telethon; print(telethon.__version__)" 2>/dev/null || echo "?")
  echo "      telethon $TELETHON_VER: обновлена ✓"
fi

# ---------------------------------------------------------------------------
# [4/6] git (рекомендуется — для обновлений)
# ---------------------------------------------------------------------------
echo "[4/6] git (рекомендуется, для обновлений)..."

if command -v git >/dev/null 2>&1; then
  echo "      git $(git --version 2>/dev/null | awk '{print $3}'): OK ✓"
elif [ "$HAS_PKG" = "1" ]; then
  echo "      git: НЕ НАЙДЕН — устанавливаем..."
  pkg install -y git >/dev/null 2>&1 \
    && echo "      git: установлен ✓" \
    || echo "      Не удалось установить git (не критично)."
else
  echo "      git: не найден (не критично, но без него не будет обновлений)."
fi

# ---------------------------------------------------------------------------
# [5/6] Файлы
# ---------------------------------------------------------------------------
echo "[5/6] Копируем файлы в $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp "$SRC_DIR/demo_installer.py" "$SRC_DIR/installer.py" \
   "$SRC_DIR/main_menu.py" "$SRC_DIR/version.py" \
   "$SRC_DIR/requirements.txt" "$SRC_DIR/TermuGram" "$INSTALL_DIR/"

# ---------------------------------------------------------------------------
# [6/6] Команда в PATH
# ---------------------------------------------------------------------------
echo "[6/6] Создаём команду TermuGram в $BIN_DIR"
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
echo "  Готово! Всё необходимое на месте."
echo "  Запустите:  TermuGram"
echo "======================================"
