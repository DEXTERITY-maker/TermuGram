#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PTY-тест главного меню TermuGram на ЖИВОЙ сессии:
инфо об аккаунте -> мои диалоги -> скачивание медиа (без скачивания) ->
отправка сообщения себе -> обратная связь разработчику ->
режим бота (неверный токен) -> выход."""
import os, pty, select, time, re, sys

TEST_TEXT = "TermuGram PTY-тест " + str(int(time.time()))

pid, fd = pty.fork()
if pid == 0:
    os.chdir(os.path.expanduser("~/.terminugram"))
    os.execvp("python3", ["python3", "main_menu.py"])

buf = b""
def read_until(patterns, timeout=45):
    global buf
    end = time.time() + timeout
    while time.time() < end:
        r, _, _ = select.select([fd], [], [], 0.3)
        if r:
            try:
                data = os.read(fd, 4096)
            except OSError:
                break
            if not data:
                break
            buf += data
        if any(p.encode() in buf for p in patterns):
            return True
    return False

def send(s):
    os.write(fd, s.encode())

def down():
    send("\x1b[B")

def settle(sec=0.8):
    """Даём терминалу дописать экран и дочитываем остаток в buf."""
    global buf
    time.sleep(sec)
    while True:
        r, _, _ = select.select([fd], [], [], 0.1)
        if not r:
            break
        try:
            data = os.read(fd, 4096)
        except OSError:
            break
        if not data:
            break
        buf += data

ok = True
def check(cond, msg):
    global ok
    print(("PASS" if cond else "FAIL") + ": " + msg)
    if not cond:
        ok = False

def clean_text():
    return re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", buf.decode(errors="replace"))

# 1. Запуск: меню (или уведомление об обновлении -> Enter)
check(read_until(["главное меню", "Доступно обновление TermuGram!"]), "меню или уведомление об обновлении")
settle()
t = clean_text()
if "Доступно обновление TermuGram!" in t:
    check(True, "уведомление об обновлении показано")
    check("TermuGram --update" in t, "в уведомлении есть команда обновления")
    check(bool(re.search(r"\d+\.\d+\.\d+", t)), "в уведомлении есть версии")
    send("\n")  # Enter -> в меню
    check(read_until(["главное меню"]), "после уведомления открылось меню")
    settle()
    t = clean_text()
check("Инфо об аккаунте" in t, "пункт «Инфо об аккаунте» есть")
send("\n")
# 2. Инфо: ждём данные аккаунта
check(read_until(["Информация об аккаунте"]), "экран информации")
settle()
t = clean_text()
check("BENJAMIN" in t, "имя аккаунта BENJAMIN видно")
check("@" in t, "username виден")
send("\n")  # Enter -> обратно в меню
# 3. Меню -> Мои диалоги (индекс 1)
check(read_until(["главное меню"]), "вернулись в меню")
down()
send("\n")
check(read_until(["Мои диалоги (первые 15)"]), "список диалогов открылся")
settle()
t = clean_text()
check("← Назад" in t, "в списке есть диалоги (есть пункт «Назад» и, значит, варианты)")
send("\n")  # первый диалог
# 4. Сообщения выбранного диалога
if read_until(["Последние сообщения", "нет сообщений"], timeout=45):
    check(True, "сообщения диалога показаны")
else:
    check(False, "сообщения диалога показаны")
send("\n")
# 5. Меню -> Скачать медиа (индекс 2)
check(read_until(["главное меню"]), "вернулись в меню")
down()
down()
send("\n")
check(read_until(["Скачать медиа — выберите диалог"]), "меню «Скачать медиа» открылось")
settle()
send("\n")  # первый диалог
if read_until(["Медиа в диалоге:", "Медиа не найдено"], timeout=45):
    settle()
    t = clean_text()
    if "Медиа не найдено" in t:
        check(True, "медиа в диалоге нет — сообщение показано")
        send("\n")  # Enter -> обратно в меню
    else:
        # В списке медиа: идём до «← Назад» (ничего не скачивая) и выходим
        lines = [l for l in t.splitlines() if l.strip()]
        hint_i = next(i for i, l in enumerate(lines) if "выбор" in l and "Enter" in l)
        opts = len(lines[:hint_i]) - 1  # минус заголовок = число пунктов
        check(opts >= 3, f"в списке медиа есть пункты ({opts} шт.)")
        for _ in range(opts - 1):
            down()
        send("\n")
        check(read_until(["главное меню"]), "вышли из списка медиа через «Назад»")
else:
    check(False, "экран медиа не появился")
# 6. Меню -> Отправить сообщение (индекс 3)
check(read_until(["главное меню"]), "вернулись в меню")
down()
down()
down()
send("\n")
check(read_until(["Кому отправить?"]), "меню «Кому отправить»")
send("\n")  # Себе (Saved Messages) — по умолчанию
check(read_until(["Текст сообщения:"]), "запрос текста")
send(TEST_TEXT + "\n")
check(read_until(["Отправить?"]), "подтверждение отправки")
send("\n")  # Да
check(read_until(["Сообщение отправлено!"], timeout=45), "сообщение отправлено")
send("\n")
# 7. Меню -> Обратная связь (индекс 4)
check(read_until(["главное меню"]), "вернулись в меню")
down()
down()
down()
down()
send("\n")
check(read_until(["Тип обращения"]), "меню категорий")
send("\n")  # Ошибка (баг) — по умолчанию
check(read_until(["Опишите ошибку конкретно"]), "шаблон бага показан")
check(read_until(["Ваше сообщение:"]), "запрос сообщения")
send("Нашёл баг: пункт «Мои диалоги» не открывается\n")
send("Ожидал: список диалогов\n")
send("Произошло: меню зависло\n")
send("\n")  # пустая строка — конец многострочного ввода
check(read_until(["Отправить разработчику?"]), "подтверждение отправки")
send("\n")  # Да
check(read_until(["Разрешить прикрепить отчёт об устройстве?"]), "диалог разрешения на отчёт")
send("\n")  # Да, прикрепить отчёт — по умолчанию
check(read_until(["Спасибо! Сообщение ушло разработчику."], timeout=45), "фидбек отправлен")
send("\n")
# 8. Меню -> Режим бота (индекс 5): токен из конфига или запрос нового
check(read_until(["главное меню"]), "вернулись в меню")
down()
down()
down()
down()
down()
send("\n")
if read_until(["Введите токен бота:", "Режим бота:", "Неверный токен бота"], timeout=60):
    if "Введите токен бота:".encode() in buf:
        check(True, "запрошен токен бота")
        send("123456789:INVALID_TOKEN_TEST\n")
        check(read_until(["Неверный токен бота"], timeout=60), "неверный токен отклонён")
        send("\n")
    elif "Режим бота:".encode() in buf:
        check(True, "бот подключился по сохранённому токену — меню бота")
        settle()
        down()
        down()
        down()
        send("\n")  # «← Назад» — 4-й пункт меню бота
    else:
        check(True, "сохранённый токен невалиден — ошибка показана")
        send("\n")
else:
    check(False, "экран бота не появился")
# 9. Выход (индекс 6)
check(read_until(["главное меню"]), "вернулись в меню")
down()
down()
down()
down()
down()
down()
send("\n")
check(read_until(["До свидания!"]), "выход выполнен")

time.sleep(1)
try:
    wpid, status = os.waitpid(pid, 0)
    code = os.waitstatus_to_exitcode(status)
except ChildProcessError:
    code = -1
check(code == 0, f"код выхода 0 (получен {code})")

print()
print("TEST_TEXT=" + TEST_TEXT)
print("ИТОГ: " + ("ВСЁ ОК" if ok else "ЕСТЬ ПРОБЛЕМЫ"))
sys.exit(0 if ok else 1)
