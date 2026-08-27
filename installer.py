#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TermuGram — установщик с РЕАЛЬНЫМ входом в Telegram (Telethon).

Запуск:
  python3 installer.py          — интерактивно (стрелки ↑/↓, Enter)
  python3 installer.py --auto   — автопроход (для теста; реальный вход не выполнится)

Перед запуском:  pip install telethon
Нужны API ID и API hash:  my.telegram.org -> API development tools

После успешного входа создаются:
  tgtool_session.session  — сессия (файл авторизации)
  config.json             — настройки (язык, тема, телефон, API-ключи)
"""
import sys
import os
import json
import re
import time

from demo_installer import (
    THEMES, STRINGS, LANG_NAMES, paint, cls, select_menu,
    ask_text, ask_secret, show_banner, wait_enter, RESET, DIM,
)

AUTO = "--auto" in sys.argv
SESSION_FILE = "tgtool_session"
CONFIG_FILE = "config.json"

INSTALL = {
    "ru": {
        "api_intro": "Данные приложения Telegram (API)",
        "api_howto": (
            "Чтобы войти, нужны API ID и API hash — ключи приложения.\n"
            "  1) Откройте my.telegram.org и войдите по номеру телефона\n"
            "  2) Нажмите 'API development tools'\n"
            "  3) Создайте приложение — получите api_id (число) и api_hash (строка)"
        ),
        "api_id_prompt": "Введите API ID (число):",
        "api_id_example": "например 1234567",
        "api_id_bad": "API ID должен быть числом (обычно 6–9 цифр). Попробуйте ещё раз.",
        "api_hash_prompt": "Введите API hash (строка):",
        "api_hash_example": "например a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "connecting": "Подключаемся к Telegram",
        "phone_sent": "Код отправлен! Откройте Telegram на телефоне — там придёт сообщение с кодом.",
        "code_prompt_real": "Введите код из Telegram:",
        "twofa_needed": "Включена двухфакторка — введите пароль:",
        "retry_code": "Попробовать ещё раз?",
        "already_logged": "Сессия уже есть — вход не нужен.",
        "success_title": "Вход выполнен!",
        "success_hello": "Добро пожаловать, {name}!",
        "session_saved": "Сессия сохранена в файл: {file}",
        "config_saved": "Настройки сохранены: {file}",
        "err": "Ошибка: {msg}",
        "bye": "Нажмите Enter, чтобы выйти",
    },
    "en": {
        "api_intro": "Telegram app credentials (API)",
        "api_howto": (
            "To log in you need API ID and API hash:\n"
            "  1) Open my.telegram.org and sign in with your phone\n"
            "  2) Click 'API development tools'\n"
            "  3) Create an app — you'll get api_id (number) and api_hash (string)"
        ),
        "api_id_prompt": "Enter API ID (number):",
        "api_id_example": "e.g. 1234567",
        "api_id_bad": "API ID must be a number (usually 6–9 digits). Try again.",
        "api_hash_prompt": "Enter API hash (string):",
        "api_hash_example": "e.g. a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "connecting": "Connecting to Telegram",
        "phone_sent": "Code sent! Open Telegram on your phone — the code message is there.",
        "code_prompt_real": "Enter the code from Telegram:",
        "twofa_needed": "Two-factor auth is on — enter your password:",
        "retry_code": "Try again?",
        "already_logged": "Session already exists — no login needed.",
        "success_title": "Logged in!",
        "success_hello": "Welcome, {name}!",
        "session_saved": "Session saved to file: {file}",
        "config_saved": "Settings saved: {file}",
        "err": "Error: {msg}",
        "bye": "Press Enter to exit",
    },
    "uk": {
        "api_intro": "Дані застосунку Telegram (API)",
        "api_howto": (
            "Для входу потрібні API ID та API hash:\n"
            "  1) Відкрийте my.telegram.org та увійдіть за номером телефону\n"
            "  2) Натисніть 'API development tools'\n"
            "  3) Створіть застосунок — отримаєте api_id (число) та api_hash (рядок)"
        ),
        "api_id_prompt": "Введіть API ID (число):",
        "api_id_example": "наприклад 1234567",
        "api_id_bad": "API ID має бути числом (зазвичай 6–9 цифр). Спробуйте ще раз.",
        "api_hash_prompt": "Введіть API hash (рядок):",
        "api_hash_example": "наприклад a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "connecting": "Підключаємось до Telegram",
        "phone_sent": "Код надіслано! Відкрийте Telegram на телефоні — там повідомлення з кодом.",
        "code_prompt_real": "Введіть код із Telegram:",
        "twofa_needed": "Увімкнено двофакторку — введіть пароль:",
        "retry_code": "Спробувати ще раз?",
        "already_logged": "Сесія вже є — вхід не потрібен.",
        "success_title": "Вхід виконано!",
        "success_hello": "Ласкаво просимо, {name}!",
        "session_saved": "Сесію збережено у файл: {file}",
        "config_saved": "Налаштування збережено: {file}",
        "err": "Помилка: {msg}",
        "bye": "Натисніть Enter, щоб вийти",
    },
}


def friendly_error(e):
    """Переводит ошибку Telethon в понятное сообщение."""
    msg = str(e)
    name = type(e).__name__
    if "API_ID_INVALID" in msg or "API_ID_PUBLISHED_FLOOD" in msg:
        return "Неверный API ID или API hash. Проверьте данные на my.telegram.org"
    if "PHONE_NUMBER_INVALID" in msg or "PHONE_NUMBER_BANNED" in msg:
        return "Номер телефона не подходит (неверный формат или недоступен)"
    if "PHONE_CODE_INVALID" in msg:
        return "Неверный код"
    if "PHONE_CODE_EXPIRED" in msg:
        return "Код истёк — запросите новый (перезапустите установщик)"
    if "PASSWORD_HASH_INVALID" in msg or "InvalidPasswordError" in name:
        return "Неверный пароль двухфакторки"
    if "SESSION_PASSWORD_NEEDED" in msg or "SessionPasswordNeededError" in name:
        return "Нужен пароль двухфакторки"
    if "FLOOD_WAIT" in msg:
        m = re.search(r"(\d+)", msg)
        wait = m.group(1) if m else "немного"
        return f"Слишком много попыток. Подождите {wait} сек."
    if "AUTH_KEY_UNREGISTERED" in msg:
        return "Файл сессии недействителен — удалите tgtool_session.session и запустите заново"
    if "ConnectionError" in name or "TimeoutError" in name or "timed out" in msg:
        return "Нет связи с Telegram. Проверьте интернет"
    return f"{name}: {msg}"


def main():
    # Проверка зависимости
    try:
        from telethon.sync import TelegramClient
        from telethon import errors as tg_errors
    except ImportError:
        print("Ошибка: библиотека telethon не установлена.")
        print("Установите:  pip install telethon")
        return 1

    banner_theme = THEMES[0]
    show_banner(banner_theme)
    wait_enter(banner_theme, "Нажмите Enter, чтобы начать / Press Enter to start")

    # 1. Язык
    lang_keys = ["ru", "en", "uk"]
    li = select_menu(STRINGS["ru"]["select_lang"], [LANG_NAMES[k] for k in lang_keys], banner_theme)
    lang = lang_keys[li]
    S = STRINGS[lang]
    SI = INSTALL[lang]

    # 2. Тема с предпросмотром
    while True:
        ti = select_menu(S["select_theme"], [t["name"] for t in THEMES], banner_theme)
        theme = THEMES[ti]
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

    # 3. API ID / API hash
    cls()
    print()
    print(paint(theme, "primary", SI["api_intro"], bold=True))
    print(DIM + SI["api_howto"] + RESET)
    print()
    while True:
        api_id = ask_text(theme, SI["api_id_prompt"], SI["api_id_example"])
        try:
            api_id_int = int(api_id.strip())
        except ValueError:
            api_id_int = 0
        if 0 < api_id_int < 2**31:
            break
        print()
        print(paint(theme, "err", "  ✗ " + SI["api_id_bad"]))
        if AUTO:
            return 1
    api_hash = ask_text(theme, SI["api_hash_prompt"], SI["api_hash_example"])

    # 4. Телефон
    phone = ask_text(theme, S["phone_prompt"], S["phone_example"])
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if not phone.startswith("+"):
        phone = "+" + phone

    # 5. Реальный вход
    cls()
    print()
    print(paint(theme, "primary", SI["connecting"] + "...", bold=True))
    client = TelegramClient(SESSION_FILE, api_id_int, api_hash.strip())
    try:
        client.connect()
        if client.is_user_authorized():
            print(paint(theme, "ok", "  ✓ " + SI["already_logged"], bold=True))
        else:
            try:
                client.send_code_request(phone)
            except Exception as e:
                print()
                print(paint(theme, "err", "  ✗ " + SI["err"].format(msg=friendly_error(e))))
                return 1
            print()
            print(paint(theme, "ok", "  ✓ " + SI["phone_sent"], bold=True))
            print()
            while True:
                code = ask_text(theme, SI["code_prompt_real"], S["code_example"])
                try:
                    client.sign_in(phone=phone, code=code)
                    break
                except tg_errors.SessionPasswordNeededError:
                    while True:
                        pwd = ask_secret(theme, SI["twofa_needed"])
                        try:
                            client.sign_in(password=pwd)
                            break
                        except Exception as e2:
                            print()
                            print(paint(theme, "err", "  ✗ " + SI["err"].format(msg=friendly_error(e2))))
                            if AUTO:
                                return 1
                            again = select_menu(SI["retry_code"], [S["yes"], S["no"]], theme)
                            if again == 1:
                                return 1
                    break
                except Exception as e:
                    print()
                    print(paint(theme, "err", "  ✗ " + SI["err"].format(msg=friendly_error(e))))
                    if AUTO:
                        return 1
                    again = select_menu(SI["retry_code"], [S["yes"], S["no"]], theme)
                    if again == 1:
                        return 1

        me = client.get_me()
        name = (me.first_name or "") if me else ""
        if me and me.last_name:
            name += " " + me.last_name
        name = name.strip() or phone

        # 6. Сохраняем настройки
        config = {
            "lang": lang,
            "theme": theme["id"],
            "phone": phone,
            "api_id": api_id_int,
            "api_hash": api_hash.strip(),
            "session": SESSION_FILE,
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        os.chmod(CONFIG_FILE, 0o600)

        # 7. Итог
        cls()
        print()
        print(paint(theme, "ok", "  " + "=" * 40, bold=True))
        print(paint(theme, "ok", "  " + SI["success_title"], bold=True))
        print(paint(theme, "ok", "  " + "=" * 40, bold=True))
        print()
        print("  " + paint(theme, "primary", SI["success_hello"].format(name=name), bold=True))
        print()
        print("  " + paint(theme, "primary", SI["session_saved"].format(file=SESSION_FILE + ".session")))
        print("  " + paint(theme, "primary", SI["config_saved"].format(file=CONFIG_FILE)))
        print()
        wait_enter(theme, S["bye"])
        return 0
    except Exception as e:
        print()
        print(paint(theme, "err", "  ✗ " + SI["err"].format(msg=friendly_error(e))))
        return 1
    finally:
        try:
            client.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
