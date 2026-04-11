"""
對話狀態管理 + 訊息處理核心（Telegram + Gemini 版）
"""

import os
import google.generativeai as genai
from app.database import get_session, save_session, get_recent_meals, log_meal

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-flash")

QUICK_REPLY_MAP = {
    "ask_cook_or_eat_out": {
        "text": "嗨！吃飯時間快到了 🍽️\n\n今天打算自己煮，還是外食／外送呢？",
        "options": [["🍳 自己煮", "🏪 外食／外送"]]
    },
    "ask_fatigue": {
        "text": "今天的狀態怎麼樣？",
        "options": [["😴 很累，不想動", "😐 普通", "💪 精力充沛"]]
    },
    "ask_who": {
        "text": "今天幾個人吃飯？",
        "options": [["🙋 只有我", "👨‍👩‍👧 和家人", "👫 和朋友"]]
    },
    "ask_budget": {
        "text": "預算大概是？",
        "options": [["💰 100以下", "💰💰 100–300"], ["💰💰💰 300以上", "沒限制"]]
    },
    "ask_drink": {
        "text": "今天想小酌一下嗎？🍺",
        "options": [["🍺 想喝一點", "🚫 不喝"]]
    },
}

STEP_FLOW = {
    "ask_cook_or_eat_out": ("mode",    "ask_fatigue"),
    "ask_fatigue":          ("fatigue", "ask_who"),
    "ask_who":              ("who",     "ask_budget"),
    "ask_budget":           ("budget",  "ask_drink"),
    "ask_drink":            ("drink",   "generating"),
}

RECORD_PREFIXES = ["記錄 ", "記錄：", "記錄:"]
TRIGGER_WORDS = ["開始", "今天吃什麼", "吃什麼", "/start", "重來", "hi", "哈囉", "你好"]

HELP_TEXT = """🍱 *今天吃什麼 Bot 使用說明*

*指令：*
• 傳任何話 → 開始詢問今天吃什麼
• `記錄 [食物]` → 記錄你吃了什麼
  例：`記錄 滷肉飯、燙青菜`
• `/start` 或「重來」→ 重新開始
• `/help` → 顯示此說明
"""


def handle_message(user_id: str, text: str) -> list:
    if text in ["/help", "help", "說明"]:
        return [make_text(HELP_TEXT, parse_mode="Markdown")]

    for prefix in RECORD_PREFIXES:
        if text.startswith(prefix):
            meal = text[len(prefix):].strip()
            if meal:
                log_meal(user_id, meal)
                return [make_text(
                    f"✅ 已記錄：{meal}\n\n累積的飲食紀錄會在下次推薦時幫你參考 🙌\n\n傳「今天吃什麼」可以重新詢問！"
                )]
            return [make_text("請在「記錄」後面加上你吃的東西，例如：記錄 滷肉飯")]

    if any(text.lower() == w.lower() for w in TRIGGER_WORDS):
        save_session(user_id, {"step": "ask_cook_or_eat_out", "answers": {}})
        return [make_keyboard(**QUICK_REPLY_MAP["ask_cook_or_eat_out"])]

    session = get_session(user_id)

    if not session or session.get("step") in ("done", None):
        save_session(user_id, {"step": "ask_cook_or_eat_out", "answers": {}})
        return [make_keyboard(**QUICK_REPLY_MAP["ask_cook_or_eat_out"])]

    step = session["step"]
    answers = session.get("answers", {})

    if step in STEP_FLOW:
        key, next_step = STEP_FLOW[step]
        answers[key] = text
        session["step"] = next_step
        session["answers"] = answers
        save_session(user_id, session)

        if next_step == "generating":
            thinking = make_text("⏳ 幫你想最適合今天的吃法，稍等一下…")
            result = generate_recommendation(user_id, answers)
            session["step"] = "done"
            save_session(user_id, session)
            return [thinking, make_text(result)]

        return [make_keyboard(**QUICK_REPLY_MAP[next_step])]

    save_session(user_id, {"step": "ask_cook_or_eat_out", "answers": {}})
    return [make_keyboard(**QUICK_REPLY_MAP["ask_cook_or_eat_out"])]


def generate_recommendation(user_id: str, answers: dict) -> str:
    recent_meals = get_recent_meals(user_id, limit=7)
    recent_str = "（尚無紀錄）" if not recent_meals else "\n".join(
        f"- {m['date']}: {m['meal']}" for m in recent_meals
    )

    mode    = answers.get("mode", "")
    fatigue = answers.get("fatigue", "")
    who     = answers.get("who", "")
    budget  = answers.get("budget", "")
    drink   = answers.get("drink", "")
    is_cooking = "自己煮" in mode

    prompt = f"""你是一個貼心的飲食助理，請根據以下條件給出今天的用餐建議：

【今天狀況】
- 用餐方式：{mode}
- 疲憊程度：{fatigue}
- 用餐對象：{who}
- 預算：{budget}
- 小酌意願：{drink}

【近七天飲食紀錄】
{recent_str}

請提供：
1. 🍽️ 今天的用餐建議（{"2–3 道菜食譜方向" if is_cooking else "具體推薦 2–3 種料理選擇"}）
2. 💡 選擇理由（結合疲憊度、用餐對象、近期飲食避免重複）
3. 🏃 用餐前後可以做的簡單運動建議
{"4. 🍺 小酌搭配建議" if "想喝" in drink else ""}

語氣輕鬆像朋友，繁體中文，300字以內。"""

    response = model.generate_content(prompt)
    suggestion = response.text
    suggestion += "\n\n---\n💬 用完餐後記得告訴我：\n「記錄 [吃了什麼]」\n例如：記錄 滷肉飯、燙青菜"
    return suggestion


def make_text(text: str, parse_mode: str = None) -> dict:
    msg = {"text": text}
    if parse_mode:
        msg["parse_mode"] = parse_mode
    return msg


def make_keyboard(text: str, options: list) -> dict:
    keyboard = [
        [{"text": opt} for opt in row]
        for row in options
    ]
    return {
        "text": text,
        "reply_markup": {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
    }
