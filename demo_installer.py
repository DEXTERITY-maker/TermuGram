#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TermuGram — ДЕМО интерактивного установщика.
Работает в Termux и любом другом терминале (чистый Python, без зависимостей).

Запуск:
  python3 demo_installer.py          — интерактивно (стрелки ↑/↓, Enter)
  python3 demo_installer.py --auto   — автопроход (для теста / витрины)

Это только макет интерфейса. Вход в Telegram НЕ выполняется:
код в демо показывается на экране, а не приходит в приложение.
"""
import os
import sys
import time
import random
import termios
import tty

AUTO = "--auto" in sys.argv

# ----------------------------------------------------------------------------
# ANSI-помощники
# ----------------------------------------------------------------------------
def esc(*codes):
    return "\x1b[" + ";".join(str(c) for c in codes) + "m"

RESET = esc(0)
BOLD = esc(1)
DIM = esc(2)
INV = esc(7)

def cls():
    if not AUTO:
        print(esc(2, "J") + esc(1, 1), end="", flush=True)

# ----------------------------------------------------------------------------
# Темы оформления
# ----------------------------------------------------------------------------
THEMES = [
    {"id": "dark",   "name": "Dark   — тёмная классика", "fg": 37, "primary": 36, "accent": 35, "ok": 32, "warn": 33, "err": 31},
    {"id": "neon",   "name": "Neon   — яркий неон",       "fg": 37, "primary": 92, "accent": 95, "ok": 92, "warn": 93, "err": 91},
    {"id": "light",  "name": "Light  — светлая",          "fg": 30, "primary": 34, "accent": 35, "ok": 32, "warn": 33, "err": 31},
    {"id": "minimal", "name": "Minimal — без цветов",     "fg": 37, "primary": 37, "accent": 37, "ok": 37, "warn": 37, "err": 37},
]

def paint(theme, key, text, bold=False):
    codes = [theme[key]]
    if bold:
        codes.insert(0, 1)
    return esc(*codes) + text + RESET

# ----------------------------------------------------------------------------
# Языки
# ----------------------------------------------------------------------------
STRINGS = {
    "ru": {
        "welcome": "Добро пожаловать! Это установщик TermuGram.",
        "continue": "Нажмите Enter, чтобы начать",
        "select_lang": "Выберите язык / Choose language:",
        "select_theme": "Выберите оформление (тему):",
        "preview_title": "Предпросмотр темы: {name}",
        "like_theme": "Нравится эта тема?",
        "yes": "Да",
        "no": "Нет",
        "phone_prompt": "Введите номер телефона (с кодом страны):",
        "phone_example": "пример: +79123456789",
        "sending_code": "Отправляем код в Telegram",
        "code_label": "Ваш код входа:",
        "fake_notice": "(в демо код показывается здесь; в реальной версии придёт в Telegram)",
        "code_prompt": "Введите код из Telegram:",
        "code_example": "5 цифр, например 48152",
        "twofa_q": "Включена двухфакторная защита (пароль)?",
        "twofa_pwd": "Введите пароль двухфакторки:",
        "summary_title": "Установка завершена!",
        "summary_lang": "Язык",
        "summary_theme": "Тема",
        "summary_phone": "Телефон",
        "summary_code": "Код подтверждён",
        "summary_session": "Сессия сохранена в файл",
        "demo_note": "Это демо-версия интерфейса. Реальный вход в Telegram появится позже.",
        "bye": "Нажмите Enter, чтобы выйти",
    },
    "en": {
        "welcome": "Welcome! This is the TermuGram installer.",
        "continue": "Press Enter to start",
        "select_lang": "Choose language:",
        "select_theme": "Choose a theme:",
        "preview_title": "Theme preview: {name}",
        "like_theme": "Do you like this theme?",
        "yes": "Yes",
        "no": "No",
        "phone_prompt": "Enter your phone number (with country code):",
        "phone_example": "e.g. +79123456789",
        "sending_code": "Sending code to Telegram",
        "code_label": "Your login code:",
        "fake_notice": "(demo: the code is shown here; in the real version it arrives in Telegram)",
        "code_prompt": "Enter the code from Telegram:",
        "code_example": "5 digits, e.g. 48152",
        "twofa_q": "Is two-factor auth (password) enabled?",
        "twofa_pwd": "Enter your 2FA password:",
        "summary_title": "Installation complete!",
        "summary_lang": "Language",
        "summary_theme": "Theme",
        "summary_phone": "Phone",
        "summary_code": "Code confirmed",
        "summary_session": "Session saved to file",
        "demo_note": "This is a UI demo. Real Telegram login comes later.",
        "bye": "Press Enter to exit",
    },
    "uk": {
        "welcome": "Ласкаво просимо! Це інсталятор TermuGram.",
        "continue": "Натисніть Enter, щоб почати",
        "select_lang": "Оберіть мову:",
        "select_theme": "Оберіть оформлення (тему):",
        "preview_title": "Попередній перегляд теми: {name}",
        "like_theme": "Подобається ця тема?",
        "yes": "Так",
        "no": "Ні",
        "phone_prompt": "Введіть номер телефону (з кодом країни):",
        "phone_example": "приклад: +380501234567",
        "sending_code": "Надсилаємо код у Telegram",
        "code_label": "Ваш код входу:",
        "fake_notice": "(у демо код показано тут; у реальній версії прийде в Telegram)",
        "code_prompt": "Введіть код із Telegram:",
        "code_example": "5 цифр, наприклад 48152",
        "twofa_q": "Увімкнено двофакторний захист (пароль)?",
        "twofa_pwd": "Введіть пароль двофакторки:",
        "summary_title": "Встановлення завершено!",
        "summary_lang": "Мова",
        "summary_theme": "Тема",
        "summary_phone": "Телефон",
        "summary_code": "Код підтверджено",
        "summary_session": "Сесію збережено у файл",
        "demo_note": "Це демо інтерфейсу. Справжній вхід у Telegram з'явиться пізніше.",
        "bye": "Натисніть Enter, щоб вийти",
    },
}

LANG_NAMES = {"ru": "Русский", "en": "English", "uk": "Українська"}

# ----------------------------------------------------------------------------
# Ввод с клавиатуры (стрелки) и текстовые поля
# ----------------------------------------------------------------------------
def read_key():
    """Читает одну клавишу: 'up', 'down', 'enter' или обычный символ."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            seq = sys.stdin.read(2)
            if seq == "[A":
                return "up"
            if seq == "[B":
                return "down"
            if seq == "[C":
                return "right"
            if seq == "[D":
                return "left"
            return "esc"
        if ch in ("\r", "\n"):
            return "enter"
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def select_menu(title, options, theme):
    """Меню со стрелками ↑/↓ и Enter. Возвращает индекс выбранного."""
    idx = 0
    while True:
        cls()
        print()
        print(paint(theme, "primary", title, bold=True))
        print()
        for i, opt in enumerate(options):
            if i == idx:
                print("  " + INV + " " + opt + " " + RESET)
            else:
                print("   " + opt)
        print()
        print(DIM + "   ↑/↓ — выбор, Enter — подтвердить" + RESET)
        if AUTO:
            time.sleep(0.4)
            return 0
        k = read_key()
        if k == "up":
            idx = (idx - 1) % len(options)
        elif k == "down":
            idx = (idx + 1) % len(options)
        elif k == "enter":
            return idx

def ask_text(theme, prompt, example=None):
    """Стилизованный текстовый ввод."""
    cls()
    print()
    print(paint(theme, "primary", prompt, bold=True))
    if example:
        print(DIM + "   " + example + RESET)
    sys.stdout.write(paint(theme, "accent", "> ", bold=True))
    sys.stdout.flush()
    if AUTO:
        val = "79123456789"
        print(val + RESET)
        time.sleep(0.4)
        return val
    val = input().strip()
    print(RESET, end="")
    return val

def ask_secret(theme, prompt):
    """Ввод пароля без эха (звёздочки)."""
    cls()
    print()
    print(paint(theme, "primary", prompt, bold=True))
    if AUTO:
        val = "secret123"
        print(DIM + "   (auto: secret123)" + RESET)
        time.sleep(0.4)
        return val
    import getpass
    val = getpass.getpass(paint(theme, "accent", "> ", bold=True))
    return val.strip()

# ----------------------------------------------------------------------------
# Экран баннера
# ----------------------------------------------------------------------------
def show_banner(theme):
    cls()
    W = 40
    def line(inner, accent=False, dim=False):
        pad = W - len(inner)
        if accent:
            body = paint(theme, "accent", inner, bold=True)
        elif dim:
            body = DIM + inner + RESET
        else:
            body = inner
        return paint(theme, "primary", "│" + body + " " * pad + "│", bold=True)
    print()
    print(paint(theme, "primary", "╔" + "═" * W + "╗", bold=True))
    print(line("            T E R M U G R A M            ", accent=True))
    print(line("        интерактивный установщик        "))
    print(line("              by Nyvella               ", dim=True))
    print(paint(theme, "primary", "╚" + "═" * W + "╝", bold=True))
    print()

def fake_code_box(theme, code, label):
    """Рисует «уведомление Telegram» с кодом (только для демо)."""
    W = 40
    def line(*parts):
        plain_len = sum(len(p[0]) for p in parts)
        inner = "".join(p[1] for p in parts)
        return paint(theme, "accent", "│" + inner + " " * (W - plain_len) + "│")
    print()
    print(paint(theme, "accent", "┌" + "─" * W + "┐", bold=True))
    print(line((" Telegram", " Telegram")))
    print(line(("", "")))
    print(line(("  " + label, "  " + label), (code, paint(theme, "ok", code, bold=True))))
    print(line(("", "")))
    print(paint(theme, "accent", "└" + "─" * W + "┘", bold=True))
    print()

def wait_enter(theme, msg):
    print(paint(theme, "warn", msg, bold=True))
    if AUTO:
        time.sleep(0.4)
        return
    sys.stdin.read(1)

# ----------------------------------------------------------------------------
# Основной поток
# ----------------------------------------------------------------------------
def main():
    try:
        # Стартовый баннер — в нейтральной теме, язык ещё не выбран
        banner_theme = THEMES[0]
        show_banner(banner_theme)
        wait_enter(banner_theme, "Нажмите Enter, чтобы начать / Press Enter to start")

        # 1. Язык
        lang_keys = ["ru", "en", "uk"]
        li = select_menu(STRINGS["ru"]["select_lang"], [LANG_NAMES[k] for k in lang_keys], banner_theme)
        lang = lang_keys[li]
        S = STRINGS[lang]

        # 2. Тема с предпросмотром и подтверждением
        while True:
            ti = select_menu(S["select_theme"], [t["name"] for t in THEMES], banner_theme)
            theme = THEMES[ti]
            # предпросмотр
            cls()
            print()
            print(paint(theme, "primary", S["preview_title"].format(name=theme["name"]), bold=True))
            print()
            print(paint(theme, "primary", "  Пример заголовка", bold=True))
            print(paint(theme, "fg", "  Обычный текст: установщик TermuGram готов к работе."))
            print(paint(theme, "ok", "  ✓ Успешно — всё работает"))
            print(paint(theme, "warn", "  ! Внимание — проверьте настройки"))
            print(paint(theme, "accent", "  → Следующий шаг"))
            print()
            choice = select_menu(S["like_theme"], [S["yes"], S["no"]], theme)
            if choice == 0:
                break

        # 3. Телефон
        phone = ask_text(theme, S["phone_prompt"], S["phone_example"])
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not phone.startswith("+"):
            phone = "+" + phone

        # 4. «Отправка кода»
        cls()
        print()
        print(paint(theme, "primary", S["sending_code"] + "...", bold=True))
        for _ in range(3):
            time.sleep(0.5)
            sys.stdout.write(". ")
            sys.stdout.flush()
        print()
        code = "".join(random.choices("0123456789", k=5))
        fake_code_box(theme, code, S["code_label"])
        print(DIM + "   " + S["fake_notice"] + RESET)
        print()
        entered = ask_text(theme, S["code_prompt"], S["code_example"])
        if AUTO:
            entered = code  # в авто-режиме «вводим» правильный код
        if entered != code:
            print()
            print(paint(theme, "err", "  ✗ Неверный код. (В демо код показан выше — введите его.)"))
            wait_enter(theme, S["continue"])
            entered = ask_text(theme, S["code_prompt"], S["code_example"])
            if AUTO:
                entered = code
        if entered != code:
            print(paint(theme, "err", "  ✗ Код снова неверный. Выход из демо."))
            return 1

        # 5. Двухфакторка
        twofa = select_menu(S["twofa_q"], [S["no"], S["yes"]], theme)
        twofa_pwd = None
        if twofa == 1:
            twofa_pwd = ask_secret(theme, S["twofa_pwd"])

        # 6. Итог
        cls()
        print()
        print(paint(theme, "ok", "  " + "=" * 40, bold=True))
        print(paint(theme, "ok", "  " + S["summary_title"], bold=True))
        print(paint(theme, "ok", "  " + "=" * 40, bold=True))
        print()
        mask = phone[:4] + " *** " + phone[-2:]
        rows = [
            (S["summary_lang"], LANG_NAMES[lang]),
            (S["summary_theme"], theme["name"].split("—")[0].strip()),
            (S["summary_phone"], mask),
            (S["summary_code"], "✓ " + code),
            (S["summary_session"], "session.demo (файл создастся в реальной версии)"),
        ]
        for k, v in rows:
            print("  " + paint(theme, "primary", k + ":") + "  " + paint(theme, "fg", v))
        if twofa_pwd:
            print("  " + paint(theme, "primary", "2FA:") + "  " + paint(theme, "fg", "установлен пароль"))
        print()
        print(DIM + "  " + S["demo_note"] + RESET)
        print()
        wait_enter(theme, S["bye"])
        return 0
    except KeyboardInterrupt:
        print()
        print(RESET + DIM + "\n  Прервано. До свидания!" + RESET)
        return 130

if __name__ == "__main__":
    sys.exit(main())
