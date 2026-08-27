#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Проверка уникальности имён через GitHub API (без токена)."""
import json
import time
import urllib.request

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "name-check", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:
        return None, None

print("=== Никнеймы: пользователь GitHub (404 = свободен) ===")
for nick in ["Nyvella", "Zyphara", "Kaelvor", "Drivane", "Orelith", "Syndrix", "Varnix", "Quorvan", "Lyrith", "Noxvale", "Zelvyn", "Erovane", "Vaxyl", "Nymvar", "Sylvo", "Drekan"]:
    status, _ = get("https://api.github.com/users/" + nick)
    mark = "СВОБОДЕН" if status == 404 else ("ЗАНЯТ" if status == 200 else f"ошибка({status})")
    print(f"  {nick:10s} -> {mark}")
    time.sleep(0.3)

print()
print("=== Имя инструмента: репозитории GitHub ===")
for name in ["TermuGram", "GramLoom", "TeleWisp", "GramWisp"]:
    status, data = get("https://api.github.com/search/repositories?q=" + name)
    if status == 200:
        total = data.get("total_count", 0)
        top = [r["full_name"] for r in data.get("items", [])[:3]]
        print(f"  {name:10s} -> найдено репозиториев: {total}  {top}")
    else:
        print(f"  {name:10s} -> ошибка({status})")
    time.sleep(0.3)
