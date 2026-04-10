"""
SQLite 資料層
儲存：對話 session、飲食紀錄、廚具清單
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.environ.get("DB_PATH", "food_bot.db")


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS meal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            meal TEXT NOT NULL,
            date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS kitchen_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            tool TEXT NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS restaurant_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            cuisine TEXT,
            price_range TEXT,
            note TEXT
        )
    """)

    conn.commit()
    conn.close()


# ── Session ──

def get_session(user_id: str) -> dict:
    conn = get_conn()
    row = conn.execute(
        "SELECT data FROM sessions WHERE user_id = ?", (user_id,)
    ).fetchone()
    conn.close()
    return json.loads(row["data"]) if row else {}


def save_session(user_id: str, data: dict):
    conn = get_conn()
    conn.execute("""
        INSERT INTO sessions (user_id, data, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            data = excluded.data,
            updated_at = excluded.updated_at
    """, (user_id, json.dumps(data, ensure_ascii=False), datetime.now().isoformat()))
    conn.commit()
    conn.close()


# ── Meal Logs ──

def log_meal(user_id: str, meal: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO meal_logs (user_id, meal, date, created_at) VALUES (?, ?, ?, ?)",
        (user_id, meal, datetime.now().strftime("%Y-%m-%d"), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def get_recent_meals(user_id: str, limit: int = 7) -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT meal, date FROM meal_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return [{"meal": r["meal"], "date": r["date"]} for r in rows]


# ── Kitchen Tools ──

def set_kitchen_tools(user_id: str, tools: list):
    conn = get_conn()
    conn.execute("DELETE FROM kitchen_tools WHERE user_id = ?", (user_id,))
    conn.executemany(
        "INSERT INTO kitchen_tools (user_id, tool) VALUES (?, ?)",
        [(user_id, t) for t in tools]
    )
    conn.commit()
    conn.close()


def get_kitchen_tools(user_id: str) -> list:
    conn = get_conn()
    rows = conn.execute(
        "SELECT tool FROM kitchen_tools WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return [r["tool"] for r in rows]
