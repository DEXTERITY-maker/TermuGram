#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PTY-тест главного меню TermuGram на ЖИВОЙ сессии:
инфо об аккаунте -> мои диалоги -> отправка сообщения себе -> выход."""
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

# 1. Меню -> Инфо об аккаунте (индекс 0, Enter)
check(read_until(["главное меню"]), "меню открылось")
check("Инфо об аккаунте".encode() in buf, "пункт «Инфо об аккаунте» есть")
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
# 5. Меню -> Отправить сообщение (индекс 2)
check(read_until(["главное меню"]), "вернулись в меню")
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
# 6. Выход (индекс 3)
check(read_until(["главное меню"]), "вернулись в меню")
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
