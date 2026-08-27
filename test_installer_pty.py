#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PTY-тест реального установщика: UI + обработка ошибки API."""
import os, pty, select, time, re, sys

pid, fd = pty.fork()
if pid == 0:
    os.execvp("python3", ["python3", "installer.py"])

buf = b""
def read_until(patterns, timeout=20):
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

def clean_text():
    return re.sub(r"\x1b\[[0-9;]*m", "", buf.decode(errors="replace"))

# 1. Баннер
check(read_until(["Нажмите Enter"]), "баннер")
send("\r")
# 2. Язык -> Русский
check(read_until(["Выберите язык"]), "меню языка")
send("\r")
# 3. Тема -> Dark, предпросмотр -> Да
check(read_until(["Выберите оформление"]), "меню темы")
send("\r")
check(read_until(["Нравится эта тема"]), "предпросмотр")
send("\r")
# 4. API ID
check(read_until(["API development tools"]), "инструкция API")
read_until(["Введите API ID"])
send("1234567\r")
# 5. API hash
check(read_until(["Введите API hash"]), "запрос API hash")
send("a" * 32 + "\r")
# 6. Телефон
check(read_until(["Введите номер телефона"]), "запрос телефона")
send("79123456789\r")
# 7. Подключение -> ошибка API (фейковые ключи)
check(read_until(["Подключаемся"]), "подключение начато")
check(read_until(["Ошибка:"], timeout=25), "показана понятная ошибка")
t = clean_text()
check("Traceback" not in t, "нет трейсбека")
check("API ID" in t, "ошибка про API ID")
send("\r")  # Enter после финальной ошибки (если экран ждёт)

time.sleep(0.5)
try:
    wpid, status = os.waitpid(pid, 0)
    code = os.waitstatus_to_exitcode(status)
except ChildProcessError:
    code = -1
check(code == 1, f"код выхода 1 (получен {code})")

print()
print("ИТОГ: " + ("ВСЁ ОК" if ok else "ЕСТЬ ПРОБЛЕМЫ"))
sys.exit(0 if ok else 1)
