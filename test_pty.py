#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PTY-тест демо установщика: эмулирует живого пользователя."""
import os, pty, select, time, re, sys

pid, fd = pty.fork()
if pid == 0:
    os.execvp("python3", ["python3", "demo_installer.py"])

buf = b""
def read_until(patterns, timeout=12):
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

ok = True
def check(cond, msg):
    global ok
    print(("PASS" if cond else "FAIL") + ": " + msg)
    if not cond:
        ok = False

def text():
    return buf.decode(errors="replace")

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
def clean_text():
    return ANSI_RE.sub("", text())

# 1. Баннер
check(read_until(["Нажмите Enter"]), "баннер показан")
send("\r")
# 2. Язык -> Русский (Enter)
check(read_until(["Выберите язык"]), "меню языка")
send("\r")
# 3. Тема: стрелка вниз (Neon) + Enter
check(read_until(["Выберите оформление"]), "меню темы")
send("\x1b[B\r")
check(read_until(["Предпросмотр"]), "предпросмотр темы показан")
check("Neon" in text(), "выбрана тема Neon")
send("\r")  # «Да, нравится»
# 4. Телефон
check(read_until(["Введите номер телефона"]), "запрос телефона")
send("79123456789\r")
# 5. Код из «уведомления»
check(read_until(["Ваш код входа"]), "код показан в уведомлении")
m = re.search(r"Ваш код входа[:]*\s*(\d{5})", clean_text())
check(bool(m), "код найден: " + (m.group(1) if m else "?"))
if m:
    send(m.group(1) + "\r")
# 6. 2FA -> Нет
check(read_until(["двухфакторная"]), "вопрос 2FA")
send("\r")
# 7. Итог
check(read_until(["Установка завершена"]), "итоговый экран показан")
read_until(["Телефон"])  # даём допечататься строкам итога
check("Телефон" in text() and "Neon" in text(), "итог содержит телефон и тему Neon")
send("\r")
time.sleep(0.5)
try:
    os.waitpid(pid, 0)
except ChildProcessError:
    pass

print()
print("ИТОГ: " + ("ВСЁ ОК" if ok else "ЕСТЬ ПРОБЛЕМЫ"))
sys.exit(0 if ok else 1)
