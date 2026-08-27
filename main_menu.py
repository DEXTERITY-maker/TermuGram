#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TermuGram — главное меню (основной функционал).

Запуск:
  python3 main_menu.py          — интерактивно (стрелки ↑/↓, Enter)

Работает после установки (есть config.json + сессия):
  • Инфо об аккаунте
  • Мои диалоги (первые 15) + последние сообщения выбранного
  • Скачивание медиа (фото/видео/голосовые/файлы) из диалога
  • Отправка сообщения: себе, из списка диалогов или по username/телефону
"""
import os
import platform
import re
import sys

from demo_installer import (
    THEMES, paint, cls, select_menu, ask_text, wait_enter, RESET, DIM,
)
from installer import friendly_error
from version import VERSION

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(APP_DIR, "config.json")

# Куда сохраняются скачанные медиа
MEDIA_DIR = os.path.join(os.path.expanduser("~"), "TermuGramDownloads")

# Куда приходит обратная связь из меню (username разработчика)
FEEDBACK_TARGET = "BENJAMIN_ALL"

MENU = {
    "ru": {
        "title": "TermuGram — главное меню",
        "item_info": "Инфо об аккаунте",
        "item_dialogs": "Мои диалоги",
        "item_send": "Отправить сообщение",
        "item_exit": "Выход",
        "back": "← Назад",
        "connecting": "Подключаемся к Telegram...",
        "no_config": "TermuGram не настроен. Запустите установку:  TermuGram --setup",
        "bad_session": "Сессия недействительна. Перенастройте вход:  TermuGram --setup",
        "info_title": "Информация об аккаунте",
        "info_name": "Имя",
        "info_username": "Username",
        "info_phone": "Телефон",
        "info_id": "ID",
        "dialogs_title": "Мои диалоги (первые 15)",
        "no_dialogs": "Диалогов пока нет",
        "msgs_title": "Последние сообщения: {name}",
        "no_msgs": "В этом диалоге пока нет сообщений",
        "media": "(медиа)",
        "unread": " ({n} новых)",
        "item_dl": "Скачать медиа",
        "dl_title": "Скачать медиа — выберите диалог",
        "dl_scan": "Ищем медиа в диалоге",
        "dl_none": "Медиа не найдено (просмотрены последние 200 сообщений)",
        "dl_pick": "Медиа в диалоге: {name} (выберите одно или скачайте всё)",
        "dl_all": "Скачать всё ({n})",
        "dl_confirm": "Скачать выбранное?",
        "dl_start": "Скачиваем",
        "dl_done": "Скачано: {ok} из {n}\n  Папка: {dir}",
        "dl_kind_photo": "фото",
        "dl_kind_video": "видео",
        "dl_kind_voice": "голосовое",
        "dl_kind_audio": "аудио",
        "dl_kind_video_note": "кружок",
        "dl_kind_sticker": "стикер",
        "dl_kind_document": "файл",
        "dl_kind_other": "медиа",
        "send_who": "Кому отправить?",
        "send_to_self": "Себе (Saved Messages)",
        "send_to_dialog": "Из списка диалогов",
        "send_to_manual": "Ввести username или телефон",
        "send_target_prompt": "Введите username (например @nick) или номер телефона:",
        "send_target_example": "пример: @durov или +79123456789",
        "send_text_prompt": "Текст сообщения:",
        "send_empty": "Пустое сообщение — ничего не отправлено.",
        "send_confirm": "Отправить?",
        "yes": "Да",
        "no": "Нет",
        "sent_ok": "Сообщение отправлено!",
        "err": "Ошибка: {msg}",
        "bye": "До свидания!",
        "item_feedback": "Обратная связь",
        "fb_cat_title": "Тип обращения",
        "fb_bug": "Ошибка (баг)",
        "fb_idea": "Улучшение / доработка",
        "fb_other": "Другое",
        "fb_bug_template": "Опишите ошибку конкретно:\n  1) Что вы делали?\n  2) Что ожидали увидеть?\n  3) Что произошло на самом деле?",
        "fb_idea_template": "Опишите идею конкретно:\n  1) Что хотите улучшить?\n  2) Как это работает сейчас?\n  3) Ваш вариант решения (если есть)",
        "fb_other_template": "Опишите ваш вопрос или пожелание подробнее.",
        "fb_hint": "Пишите конкретно — так быстрее поможем. После текста оставьте пустую строку и нажмите Enter.",
        "fb_prompt": "Ваше сообщение:",
        "fb_empty": "Сообщение пустое — ничего не отправлено.",
        "fb_confirm": "Отправить разработчику?",
        "fb_sent": "Спасибо! Сообщение ушло разработчику.",
        "fb_from": "От",
        "fb_cat": "Категория",
        "fb_version": "Версия",
        "fb_lang_theme": "Язык/тема",
        "fb_device": "Устройство",
        "fb_block": "Обратная связь TermuGram",
        "fb_device_ask": "Разрешить прикрепить отчёт об устройстве?",
        "fb_device_yes": "Да, прикрепить отчёт",
        "fb_device_no": "Нет, только текст",
        "fb_device_title": "Отчёт об устройстве",
        "fb_device_manuf": "Производитель",
        "fb_device_model": "Модель",
        "fb_device_android": "Android",
        "fb_device_build": "Сборка",
        "fb_device_kernel": "Ядро",
        "fb_device_arch": "Архитектура",
        "fb_device_python": "Python",
        "item_bot": "Режим бота",
        "bot_howto": "Токен бота выдаёт @BotFather (команда /newbot). Скопируйте токен вида 123456789:ABC...",
        "bot_token_prompt": "Введите токен бота:",
        "bot_token_example": "пример: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        "bot_token_saved": "Токен сохранён.",
        "bot_connecting": "Подключаемся как бот",
        "bot_bad_token": "Неверный токен бота. Проверьте его у @BotFather.",
        "bot_title": "Режим бота: {name}",
        "bot_info": "Инфо о боте",
        "bot_send": "Отправить сообщение",
        "bot_change_token": "Сменить токен",
        "bot_send_who": "Куда отправить? (username или ID чата/канала)",
        "bot_send_who_example": "пример: @my_channel или -1001234567890",
        "press_enter": "Нажмите Enter, чтобы продолжить",
    },
    "en": {
        "title": "TermuGram — main menu",
        "item_info": "Account info",
        "item_dialogs": "My dialogs",
        "item_send": "Send message",
        "item_exit": "Exit",
        "back": "← Back",
        "connecting": "Connecting to Telegram...",
        "no_config": "TermuGram is not set up. Run the installer:  TermuGram --setup",
        "bad_session": "Session is invalid. Re-run setup:  TermuGram --setup",
        "info_title": "Account info",
        "info_name": "Name",
        "info_username": "Username",
        "info_phone": "Phone",
        "info_id": "ID",
        "dialogs_title": "My dialogs (first 15)",
        "no_dialogs": "No dialogs yet",
        "msgs_title": "Latest messages: {name}",
        "no_msgs": "No messages in this dialog yet",
        "media": "(media)",
        "unread": " ({n} new)",
        "item_dl": "Download media",
        "dl_title": "Download media — pick a dialog",
        "dl_scan": "Looking for media in the dialog",
        "dl_none": "No media found (last 200 messages checked)",
        "dl_pick": "Media in: {name} (pick one or download all)",
        "dl_all": "Download all ({n})",
        "dl_confirm": "Download selected?",
        "dl_start": "Downloading",
        "dl_done": "Downloaded: {ok} of {n}\n  Folder: {dir}",
        "dl_kind_photo": "photo",
        "dl_kind_video": "video",
        "dl_kind_voice": "voice",
        "dl_kind_audio": "audio",
        "dl_kind_video_note": "video note",
        "dl_kind_sticker": "sticker",
        "dl_kind_document": "file",
        "dl_kind_other": "media",
        "send_who": "Send to whom?",
        "send_to_self": "Me (Saved Messages)",
        "send_to_dialog": "From my dialogs",
        "send_to_manual": "Enter username or phone",
        "send_target_prompt": "Enter username (e.g. @nick) or phone number:",
        "send_target_example": "e.g. @durov or +79123456789",
        "send_text_prompt": "Message text:",
        "send_empty": "Empty message — nothing sent.",
        "send_confirm": "Send?",
        "yes": "Yes",
        "no": "No",
        "sent_ok": "Message sent!",
        "err": "Error: {msg}",
        "bye": "Goodbye!",
        "item_feedback": "Feedback",
        "fb_cat_title": "Type of request",
        "fb_bug": "Bug",
        "fb_idea": "Improvement / idea",
        "fb_other": "Other",
        "fb_bug_template": "Describe the bug specifically:\n  1) What were you doing?\n  2) What did you expect?\n  3) What actually happened?",
        "fb_idea_template": "Describe the idea specifically:\n  1) What do you want to improve?\n  2) How does it work now?\n  3) Your proposed solution (if any)",
        "fb_other_template": "Describe your question or wish in detail.",
        "fb_hint": "Be specific — it helps us help you faster. After the text leave an empty line and press Enter.",
        "fb_prompt": "Your message:",
        "fb_empty": "Empty message — nothing sent.",
        "fb_confirm": "Send to the developer?",
        "fb_sent": "Thanks! The message was sent to the developer.",
        "fb_from": "From",
        "fb_cat": "Category",
        "fb_version": "Version",
        "fb_lang_theme": "Lang/theme",
        "fb_device": "Device",
        "fb_block": "TermuGram feedback",
        "fb_device_ask": "Allow attaching a device report?",
        "fb_device_yes": "Yes, attach the report",
        "fb_device_no": "No, text only",
        "fb_device_title": "Device report",
        "fb_device_manuf": "Manufacturer",
        "fb_device_model": "Model",
        "fb_device_android": "Android",
        "fb_device_build": "Build",
        "fb_device_kernel": "Kernel",
        "fb_device_arch": "Architecture",
        "fb_device_python": "Python",
        "item_bot": "Bot mode",
        "bot_howto": "Get a bot token from @BotFather (/newbot). Copy the token like 123456789:ABC...",
        "bot_token_prompt": "Enter the bot token:",
        "bot_token_example": "e.g. 123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        "bot_token_saved": "Token saved.",
        "bot_connecting": "Connecting as bot",
        "bot_bad_token": "Invalid bot token. Check it with @BotFather.",
        "bot_title": "Bot mode: {name}",
        "bot_info": "Bot info",
        "bot_send": "Send message",
        "bot_change_token": "Change token",
        "bot_send_who": "Send to? (username or chat/channel ID)",
        "bot_send_who_example": "e.g. @my_channel or -1001234567890",
        "press_enter": "Press Enter to continue",
    },
    "uk": {
        "title": "TermuGram — головне меню",
        "item_info": "Інформація про акаунт",
        "item_dialogs": "Мої діалоги",
        "item_send": "Надіслати повідомлення",
        "item_exit": "Вихід",
        "back": "← Назад",
        "connecting": "Підключаємось до Telegram...",
        "no_config": "TermuGram не налаштовано. Запустіть установку:  TermuGram --setup",
        "bad_session": "Сесія недійсна. Переналаштуйте вхід:  TermuGram --setup",
        "info_title": "Інформація про акаунт",
        "info_name": "Ім'я",
        "info_username": "Username",
        "info_phone": "Телефон",
        "info_id": "ID",
        "dialogs_title": "Мої діалоги (перші 15)",
        "no_dialogs": "Діалогів поки немає",
        "msgs_title": "Останні повідомлення: {name}",
        "no_msgs": "У цьому діалозі поки немає повідомлень",
        "media": "(медіа)",
        "unread": " ({n} нових)",
        "item_dl": "Завантажити медіа",
        "dl_title": "Завантажити медіа — оберіть діалог",
        "dl_scan": "Шукаємо медіа в діалозі",
        "dl_none": "Медіа не знайдено (переглянуто останні 200 повідомлень)",
        "dl_pick": "Медіа в діалозі: {name} (оберіть одне або завантажте все)",
        "dl_all": "Завантажити все ({n})",
        "dl_confirm": "Завантажити вибране?",
        "dl_start": "Завантажуємо",
        "dl_done": "Завантажено: {ok} з {n}\n  Папка: {dir}",
        "dl_kind_photo": "фото",
        "dl_kind_video": "відео",
        "dl_kind_voice": "голосове",
        "dl_kind_audio": "аудіо",
        "dl_kind_video_note": "кружечок",
        "dl_kind_sticker": "стікер",
        "dl_kind_document": "файл",
        "dl_kind_other": "медіа",
        "send_who": "Кому надіслати?",
        "send_to_self": "Собі (Saved Messages)",
        "send_to_dialog": "Зі списку діалогів",
        "send_to_manual": "Ввести username або телефон",
        "send_target_prompt": "Введіть username (наприклад @nick) або номер телефону:",
        "send_target_example": "приклад: @durov або +79123456789",
        "send_text_prompt": "Текст повідомлення:",
        "send_empty": "Порожнє повідомлення — нічого не надіслано.",
        "send_confirm": "Надіслати?",
        "yes": "Так",
        "no": "Ні",
        "sent_ok": "Повідомлення надіслано!",
        "err": "Помилка: {msg}",
        "bye": "До побачення!",
        "item_feedback": "Зворотний зв'язок",
        "fb_cat_title": "Тип звернення",
        "fb_bug": "Помилка (баг)",
        "fb_idea": "Покращення / доопрацювання",
        "fb_other": "Інше",
        "fb_bug_template": "Опишіть помилку конкретно:\n  1) Що ви робили?\n  2) Що очікували побачити?\n  3) Що сталося насправді?",
        "fb_idea_template": "Опишіть ідею конкретно:\n  1) Що хочете покращити?\n  2) Як це працює зараз?\n  3) Ваш варіант рішення (якщо є)",
        "fb_other_template": "Опишіть ваше питання або побажання детальніше.",
        "fb_hint": "Пишіть конкретно — так швидше допоможемо. Після тексту залиште порожній рядок і натисніть Enter.",
        "fb_prompt": "Ваше повідомлення:",
        "fb_empty": "Порожнє повідомлення — нічого не надіслано.",
        "fb_confirm": "Надіслати розробнику?",
        "fb_sent": "Дякуємо! Повідомлення надіслано розробнику.",
        "fb_from": "Від",
        "fb_cat": "Категорія",
        "fb_version": "Версія",
        "fb_lang_theme": "Мова/тема",
        "fb_device": "Пристрій",
        "fb_block": "Зворотний зв'язок TermuGram",
        "fb_device_ask": "Дозволити прикріпити звіт про пристрій?",
        "fb_device_yes": "Так, прикріпити звіт",
        "fb_device_no": "Ні, лише текст",
        "fb_device_title": "Звіт про пристрій",
        "fb_device_manuf": "Виробник",
        "fb_device_model": "Модель",
        "fb_device_android": "Android",
        "fb_device_build": "Збірка",
        "fb_device_kernel": "Ядро",
        "fb_device_arch": "Архітектура",
        "fb_device_python": "Python",
        "item_bot": "Режим бота",
        "bot_howto": "Токен бота видає @BotFather (команда /newbot). Скопіюйте токен виду 123456789:ABC...",
        "bot_token_prompt": "Введіть токен бота:",
        "bot_token_example": "приклад: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz",
        "bot_token_saved": "Токен збережено.",
        "bot_connecting": "Підключаємось як бот",
        "bot_bad_token": "Невірний токен бота. Перевірте його у @BotFather.",
        "bot_title": "Режим бота: {name}",
        "bot_info": "Інформація про бота",
        "bot_send": "Надіслати повідомлення",
        "bot_change_token": "Змінити токен",
        "bot_send_who": "Куди надіслати? (username або ID чату/каналу)",
        "bot_send_who_example": "приклад: @my_channel або -1001234567890",
        "press_enter": "Натисніть Enter, щоб продовжити",
    },
}


def load_config():
    try:
        import json
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def theme_by_id(tid):
    for t in THEMES:
        if t["id"] == tid:
            return t
    return THEMES[0]


def short_name(sender):
    """Имя отправителя сообщения, если доступно."""
    if sender is None:
        return "?"
    first = getattr(sender, "first_name", None) or ""
    last = getattr(sender, "last_name", None) or ""
    title = getattr(sender, "title", None) or ""
    uname = getattr(sender, "username", None) or ""
    name = (first + " " + last).strip() or title or ("@" + uname if uname else "?")
    return name


def fmt_date(dt):
    try:
        return dt.strftime("%d.%m %H:%M")
    except Exception:
        return ""


def ask_multiline(theme, prompt, hint=None):
    """Многострочный ввод: строки до пустой (Enter на пустой строке — конец)."""
    cls()
    print()
    print(paint(theme, "primary", prompt, bold=True))
    if hint:
        print(DIM + "   " + hint + RESET)
    print()
    lines = []
    while True:
        sys.stdout.write(paint(theme, "accent", "> ", bold=True))
        sys.stdout.flush()
        line = input().strip()
        print(RESET, end="")
        if not line:
            break
        lines.append(line)
    return "\n".join(lines)


def getprop(key):
    """Читает свойство Android (getprop). Вне Android вернёт ''."""
    try:
        import subprocess
        r = subprocess.run(["getprop", key], capture_output=True, text=True, timeout=5)
        return r.stdout.strip()
    except Exception:
        return ""


def collect_device_report(S):
    """Полный отчёт об устройстве: производитель, модель, Android, сборка, ядро."""
    manuf = getprop("ro.product.manufacturer")
    model = getprop("ro.product.model")
    rel = getprop("ro.build.version.release")
    sdk = getprop("ro.build.version.sdk")
    build = getprop("ro.build.display.id")
    android = rel + (" (SDK " + sdk + ")" if sdk else "")
    report = (
        "📱 " + S["fb_device_title"] + "\n"
        + S["fb_device_manuf"] + ": " + (manuf or "—") + "\n"
        + S["fb_device_model"] + ": " + (model or "—") + "\n"
        + S["fb_device_android"] + ": " + (android or "—") + "\n"
        + S["fb_device_build"] + ": " + (build or "—") + "\n"
        + S["fb_device_kernel"] + ": " + os.uname().release + "\n"
        + S["fb_device_arch"] + ": " + platform.machine() + "\n"
        + S["fb_device_python"] + ": " + platform.python_version()
    )
    return report, model


def show_info(client, theme, S):
    me = client.get_me()
    cls()
    print()
    print(paint(theme, "primary", S["info_title"], bold=True))
    print()
    rows = [
        (S["info_name"], (me.first_name or "") + (" " + me.last_name if me.last_name else "")),
        (S["info_username"], "@" + me.username if me.username else "—"),
        (S["info_phone"], me.phone or "—"),
        (S["info_id"], str(me.id)),
    ]
    for k, v in rows:
        print("  " + paint(theme, "primary", k + ":") + "  " + paint(theme, "fg", v.strip()))
    print()
    wait_enter(theme, S["press_enter"])


def list_dialogs(client, limit=15):
    """Возвращает список (dialog, имя_для_показа) — без unread-бейджа (его добавим в меню)."""
    out = []
    for d in client.get_dialogs(limit=limit):
        name = (d.name or "").strip()
        if not name:
            name = "ID " + str(getattr(d.entity, "id", ""))
        if len(name) > 42:
            name = name[:41] + "…"
        out.append((d, name))
    return out


def pick_dialog(client, theme, S, title):
    """Меню выбора диалога. Возвращает (entity, имя) или None при «Назад»."""
    dialogs = list_dialogs(client)
    if not dialogs:
        cls()
        print()
        print(paint(theme, "warn", "  ! " + S["no_dialogs"]))
        print()
        wait_enter(theme, S["press_enter"])
        return None
    options = []
    for d, name in dialogs:
        badge = ""
        if getattr(d, "unread_count", 0):
            badge = DIM + S["unread"].format(n=d.unread_count) + RESET
        options.append(name + badge)
    options.append(S["back"])
    idx = select_menu(title, options, theme)
    if idx >= len(dialogs):
        return None
    d, name = dialogs[idx]
    return (d.entity, name)


def show_dialogs(client, theme, S):
    picked = pick_dialog(client, theme, S, S["dialogs_title"])
    if picked is None:
        return
    entity, name = picked
    msgs = list(client.get_messages(entity, limit=5))
    cls()
    print()
    print(paint(theme, "primary", S["msgs_title"].format(name=name), bold=True))
    print()
    if not msgs:
        print("  " + DIM + S["no_msgs"] + RESET)
    for m in msgs:
        text = m.message or m.text
        if not text:
            text = S["media"]
        text = text.replace("\n", " ")[:80]
        sender = short_name(m.sender)
        date = fmt_date(m.date)
        line = f"  {date}  {sender}:  {text}"
        if getattr(m, "out", False):
            line = "  → " + date + "  " + text
        print(paint(theme, "fg", line))
    print()
    wait_enter(theme, S["press_enter"])


SKIP_MEDIA_TYPES = {
    "MessageMediaEmpty", "MessageMediaGeo", "MessageMediaGeoLive",
    "MessageMediaVenue", "MessageMediaContact", "MessageMediaPoll",
    "MessageMediaDice", "MessageMediaGame", "MessageMediaGiveaway",
    "MessageMediaGiveawayResults",
}

MEDIA_ICONS = {
    "photo": "🖼", "video": "🎬", "voice": "🎤", "audio": "🎵",
    "video_note": "🎞", "sticker": "🃏", "document": "📄", "other": "📎",
}


def media_kind(m):
    """Тип медиа сообщения: photo/video/voice/audio/video_note/sticker/document/other."""
    for attr, kind in (
        ("photo", "photo"), ("video", "video"), ("voice", "voice"),
        ("audio", "audio"), ("video_note", "video_note"),
        ("sticker", "sticker"), ("document", "document"),
    ):
        if getattr(m, attr, None):
            return kind
    return "other"


def fmt_size(n):
    if not n:
        return ""
    if n >= 1024 * 1024:
        return f"{n / 1024 / 1024:.1f} МБ"
    if n >= 1024:
        return f"{n / 1024:.0f} КБ"
    return f"{n} Б"


def media_label(m, S):
    """Строка для меню: дата, иконка, тип, имя файла, размер."""
    kind = media_kind(m)
    icon = MEDIA_ICONS.get(kind, "📎")
    kind_name = S.get("dl_kind_" + kind, S.get("dl_kind_other", kind))
    fname = getattr(getattr(m, "file", None), "name", None) or ""
    size = getattr(getattr(m, "file", None), "size", None)
    label = f"{fmt_date(m.date)}  {icon} {kind_name}"
    if fname:
        label += "  " + fname
    if size:
        label += "  (" + fmt_size(size) + ")"
    if len(label) > 66:
        label = label[:65] + "…"
    return label


def safe_dir_name(name):
    """Имя папки из имени диалога (без недопустимых символов)."""
    s = re.sub(r'[\\/:*?"<>|]', "_", (name or "").strip()).strip(" .")
    return s or "dialog"


def media_filename(m):
    """Имя файла для скачивания: дата_тип или дата_имя_файла."""
    kind = media_kind(m)
    try:
        date = m.date.strftime("%d-%m_%H-%M")
    except Exception:
        date = "no_date"
    fname = getattr(getattr(m, "file", None), "name", None) or ""
    if not fname:
        ext = {"photo": ".jpg", "voice": ".ogg", "video_note": ".mp4",
               "video": ".mp4", "audio": ".mp3", "sticker": ".webp"}.get(kind, "")
        fname = kind + ext
    else:
        fname = re.sub(r'[\\/:*?"<>|]', "_", fname)
    return f"{date}_{fname}"


def unique_path(directory, fname):
    """Путь без перезаписи: при совпадении добавляет _1, _2..."""
    path = os.path.join(directory, fname)
    if not os.path.exists(path):
        return path
    base, ext = os.path.splitext(fname)
    i = 1
    while os.path.exists(os.path.join(directory, f"{base}_{i}{ext}")):
        i += 1
    return os.path.join(directory, f"{base}_{i}{ext}")


def download_flow(client, theme, S):
    """Скачивание медиа: диалог -> список медиа -> одно или всё."""
    picked = pick_dialog(client, theme, S, S["dl_title"])
    if picked is None:
        return
    entity, name = picked

    cls()
    print()
    print(paint(theme, "primary", S["dl_scan"] + "…", bold=True))
    items = []
    for m in client.iter_messages(entity, limit=200):
        if not m.media or getattr(m.media, "webpage", None):
            continue
        if type(m.media).__name__ in SKIP_MEDIA_TYPES:
            continue
        items.append(m)
        if len(items) >= 20:
            break

    if not items:
        print()
        print(paint(theme, "warn", "  ! " + S["dl_none"]))
        print()
        wait_enter(theme, S["press_enter"])
        return

    labels = [media_label(m, S) for m in items]
    options = labels + [S["dl_all"].format(n=len(items)), S["back"]]
    idx = select_menu(S["dl_pick"].format(name=name), options, theme)
    if idx >= len(items) + 1:  # «Назад»
        return
    selected = items if idx == len(items) else [items[idx]]

    confirm = select_menu(S["dl_confirm"], [S["yes"], S["no"]], theme)
    if confirm == 1:
        return

    out_dir = os.path.join(MEDIA_DIR, safe_dir_name(name))
    os.makedirs(out_dir, exist_ok=True)
    cls()
    print()
    print(paint(theme, "primary", S["dl_start"] + "…", bold=True))
    ok_count = 0
    for m in selected:
        fname = media_filename(m)
        path = unique_path(out_dir, fname)
        try:
            client.download_media(m, file=path)
            ok_count += 1
            print("  " + paint(theme, "ok", "✓ " + fname))
        except Exception as e:
            print("  " + paint(theme, "err", "✗ " + fname + " — " + friendly_error(e)))
    print()
    print(paint(theme, "ok", "  " + S["dl_done"].format(ok=ok_count, n=len(selected), dir=out_dir), bold=True))
    print()
    wait_enter(theme, S["press_enter"])


def send_flow(client, theme, S):
    target_opt = select_menu(
        S["send_who"],
        [S["send_to_self"], S["send_to_dialog"], S["send_to_manual"], S["back"]],
        theme,
    )
    if target_opt == 3:
        return
    if target_opt == 0:
        entity, name = "me", "Saved Messages"
    elif target_opt == 1:
        picked = pick_dialog(client, theme, S, S["send_who"])
        if picked is None:
            return
        entity, name = picked
    else:
        target = ask_text(theme, S["send_target_prompt"], S["send_target_example"])
        if not target:
            return
        entity, name = target, target

    text = ask_text(theme, S["send_text_prompt"])
    if not text.strip():
        cls()
        print()
        print(paint(theme, "warn", "  ! " + S["send_empty"]))
        print()
        wait_enter(theme, S["press_enter"])
        return

    confirm = select_menu(S["send_confirm"], [S["yes"], S["no"]], theme)
    if confirm == 1:
        return

    cls()
    print()
    print(paint(theme, "primary", S["connecting"] + "…", bold=True))
    try:
        client.send_message(entity, text.strip())
        print()
        print(paint(theme, "ok", "  ✓ " + S["sent_ok"], bold=True))
    except Exception as e:
        print()
        print(paint(theme, "err", "  ✗ " + S["err"].format(msg=friendly_error(e))))
    print()
    wait_enter(theme, S["press_enter"])


def feedback_flow(client, theme, S, cfg):
    """Обратная связь: категория -> шаблон -> текст -> отправка разработчику."""
    cats = [S["fb_bug"], S["fb_idea"], S["fb_other"], S["back"]]
    ci = select_menu(S["fb_cat_title"], cats, theme)
    if ci == 3:
        return
    if ci == 0:
        cat, template = S["fb_bug"], S["fb_bug_template"]
    elif ci == 1:
        cat, template = S["fb_idea"], S["fb_idea_template"]
    else:
        cat, template = S["fb_other"], S["fb_other_template"]

    cls()
    print()
    print(paint(theme, "primary", S["item_feedback"], bold=True))
    print()
    print(DIM + template.replace("\n", "\n  ") + RESET)
    print()
    text = ask_multiline(theme, S["fb_prompt"], S["fb_hint"])
    if not text.strip():
        cls()
        print()
        print(paint(theme, "warn", "  ! " + S["fb_empty"]))
        print()
        wait_enter(theme, S["press_enter"])
        return

    confirm = select_menu(S["fb_confirm"], [S["yes"], S["no"]], theme)
    if confirm == 1:
        return

    # Разрешение на отчёт об устройстве (диалог в стиле Android)
    with_report = select_menu(
        S["fb_device_ask"], [S["fb_device_yes"], S["fb_device_no"]], theme
    ) == 0

    me = client.get_me()
    sender = (me.first_name or "")
    if me.last_name:
        sender += " " + me.last_name
    sender = sender.strip() or "?"
    if me.username:
        sender += " (@" + me.username + ")"

    report = ""
    model = ""
    if with_report:
        report, model = collect_device_report(S)
    device = model if model else platform.platform()

    msg = (
        "📬 " + S["fb_block"] + "\n"
        + "━━━━━━━━━━━━━━━━━━━━\n"
        + S["fb_cat"] + ": " + cat + "\n"
        + S["fb_from"] + ": " + sender + "\n"
        + S["fb_version"] + ": " + VERSION + "\n"
        + S["fb_lang_theme"] + ": " + str(cfg.get("lang", "?")) + " / " + str(cfg.get("theme", "?")) + "\n"
        + S["fb_device"] + ": " + device + "\n"
        + "━━━━━━━━━━━━━━━━━━━━\n"
        + text
    )
    if report:
        msg += "\n\n" + report
    cls()
    print()
    print(paint(theme, "primary", S["connecting"] + "…", bold=True))
    try:
        client.send_message(FEEDBACK_TARGET, msg)
        print()
        print(paint(theme, "ok", "  ✓ " + S["fb_sent"], bold=True))
    except Exception as e:
        print()
        print(paint(theme, "err", "  ✗ " + S["err"].format(msg=friendly_error(e))))
    print()
    wait_enter(theme, S["press_enter"])


def save_config(cfg):
    import json
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
    os.chmod(CONFIG_FILE, 0o600)


def bot_error_msg(e, S):
    """Понятное сообщение об ошибке бота."""
    msg = str(e)
    name = type(e).__name__
    if "access token" in msg.lower() or "ACCESS_TOKEN_INVALID" in msg or "AccessTokenInvalidError" in name:
        return S["bot_bad_token"]
    return S["err"].format(msg=friendly_error(e))


def bot_connect(token, api_id, api_hash):
    """Подключает бота по токену. Возвращает (client, me) или (None, error)."""
    from telethon.sync import TelegramClient
    bot = TelegramClient(os.path.join(APP_DIR, "tgtool_bot"), api_id, api_hash)
    try:
        bot.connect()
        bot.start(bot_token=token)
        me = bot.get_me()
        return bot, me, None
    except Exception as e:
        try:
            bot.disconnect()
        except Exception:
            pass
        return None, None, e


def bot_flow(theme, S, cfg):
    """Режим бота: токен -> подключение -> инфо/отправка/смена токена."""
    from telethon.sync import TelegramClient  # noqa: F401 (для типов)

    api_id = cfg.get("api_id")
    api_hash = cfg.get("api_hash")
    if not api_id or not api_hash:
        print()
        print("  ✗ " + S["err"].format(msg="нет API-ключей в config.json"))
        print()
        return

    token = str(cfg.get("bot_token", "")).strip()
    if not token:
        cls()
        print()
        print(paint(theme, "primary", S["item_bot"], bold=True))
        print(DIM + "   " + S["bot_howto"] + RESET)
        print()
        token = ask_text(theme, S["bot_token_prompt"], S["bot_token_example"]).strip()
        if not token:
            return

    cls()
    print()
    print(paint(theme, "primary", S["bot_connecting"] + "…", bold=True))
    bot, me, err = bot_connect(token, api_id, api_hash)
    if bot is None:
        print()
        print(paint(theme, "err", "  ✗ " + bot_error_msg(err, S)))
        print()
        wait_enter(theme, S["press_enter"])
        return

    if "bot_token" not in cfg:
        cfg["bot_token"] = token
        save_config(cfg)
        print()
        print(paint(theme, "ok", "  ✓ " + S["bot_token_saved"], bold=True))
        print()
        wait_enter(theme, S["press_enter"])

    while True:
        name = (me.first_name or "?").strip()
        idx = select_menu(
            S["bot_title"].format(name=name),
            [S["bot_info"], S["bot_send"], S["bot_change_token"], S["back"]],
            theme,
        )
        if idx == 0:
            cls()
            print()
            print(paint(theme, "primary", S["bot_info"], bold=True))
            print()
            rows = [
                (S["info_name"], me.first_name or "?"),
                (S["info_username"], "@" + me.username if me.username else "—"),
                (S["info_id"], str(me.id)),
            ]
            for k, v in rows:
                print("  " + paint(theme, "primary", k + ":") + "  " + paint(theme, "fg", v))
            print()
            wait_enter(theme, S["press_enter"])
        elif idx == 1:
            target = ask_text(theme, S["bot_send_who"], S["bot_send_who_example"])
            if not target:
                continue
            text = ask_text(theme, S["send_text_prompt"])
            if not text.strip():
                continue
            confirm = select_menu(S["send_confirm"], [S["yes"], S["no"]], theme)
            if confirm == 1:
                continue
            cls()
            print()
            print(paint(theme, "primary", S["bot_connecting"] + "…", bold=True))
            try:
                bot.send_message(target.strip(), text.strip())
                print()
                print(paint(theme, "ok", "  ✓ " + S["sent_ok"], bold=True))
            except Exception as e:
                print()
                print(paint(theme, "err", "  ✗ " + bot_error_msg(e, S)))
            print()
            wait_enter(theme, S["press_enter"])
        elif idx == 2:
            new_token = ask_text(theme, S["bot_token_prompt"], S["bot_token_example"]).strip()
            if not new_token:
                continue
            try:
                bot.disconnect()
            except Exception:
                pass
            sess_path = os.path.join(APP_DIR, "tgtool_bot.session")
            bak_path = sess_path + ".bak"
            try:
                os.replace(sess_path, bak_path)
            except OSError:
                pass
            cls()
            print()
            print(paint(theme, "primary", S["bot_connecting"] + "…", bold=True))
            bot, me, err = bot_connect(new_token, api_id, api_hash)
            if bot is None:
                try:
                    os.remove(sess_path)
                except OSError:
                    pass
                try:
                    os.replace(bak_path, sess_path)
                except OSError:
                    pass
                print()
                print(paint(theme, "err", "  ✗ " + bot_error_msg(err, S)))
                print()
                wait_enter(theme, S["press_enter"])
                return
            try:
                os.remove(bak_path)
            except OSError:
                pass
            cfg["bot_token"] = new_token
            save_config(cfg)
            print()
            print(paint(theme, "ok", "  ✓ " + S["bot_token_saved"], bold=True))
            print()
            wait_enter(theme, S["press_enter"])
        else:
            break

    try:
        bot.disconnect()
    except Exception:
        pass


def main():
    try:
        cfg = load_config()
        if cfg is None:
            print()
            print("  ✗ " + MENU["ru"]["no_config"])
            print()
            return 1
        lang = cfg.get("lang", "ru")
        if lang not in MENU:
            lang = "ru"
        S = MENU[lang]
        theme = theme_by_id(cfg.get("theme", "dark"))

        from telethon.sync import TelegramClient
        session_file = cfg["session"]
        if not os.path.isabs(session_file):
            session_file = os.path.join(APP_DIR, session_file)
        client = TelegramClient(session_file, cfg["api_id"], cfg["api_hash"])
        client.connect()
        if not client.is_user_authorized():
            print()
            print("  ✗ " + S["bad_session"])
            print()
            client.disconnect()
            return 1

        while True:
            idx = select_menu(
                S["title"],
                [S["item_info"], S["item_dialogs"], S["item_dl"], S["item_send"], S["item_feedback"], S["item_bot"], S["item_exit"]],
                theme,
            )
            if idx == 0:
                show_info(client, theme, S)
            elif idx == 1:
                show_dialogs(client, theme, S)
            elif idx == 2:
                download_flow(client, theme, S)
            elif idx == 3:
                send_flow(client, theme, S)
            elif idx == 4:
                feedback_flow(client, theme, S, cfg)
            elif idx == 5:
                bot_flow(theme, S, cfg)
            else:
                break

        client.disconnect()
        cls()
        print()
        print("  " + paint(theme, "primary", S["bye"], bold=True))
        print()
        return 0
    except KeyboardInterrupt:
        print()
        print(RESET + DIM + "\n  Прервано. До свидания!" + RESET)
        return 130
    except Exception as e:
        print()
        print(RESET + "  ✗ " + friendly_error(e))
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
