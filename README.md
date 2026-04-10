# 🍱 今天吃什麼 — Telegram Bot

## 目前功能（Step 1）
- ✅ 對話式詢問（自己煮/外食、疲憊度、用餐對象、預算、小酌）
- ✅ AI 綜合推薦用餐與運動建議
- ✅ 飲食記錄（傳「記錄 滷肉飯」即可儲存）
- ✅ 近 7 天飲食紀錄分析，避免重複推薦

---

## 部署步驟（第一次從零開始）

### Step A：建立 Telegram Bot

1. 打開 Telegram，搜尋 **@BotFather**
2. 傳 `/newbot`
3. 輸入 Bot 的**名稱**（例如：今天吃什麼助理）
4. 輸入 Bot 的**帳號**（英文，必須以 `bot` 結尾，例如：`WhatToEatTodayBot`）
5. BotFather 會給你一串 **Token**，格式像：
   ```
   7123456789:AAFxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   **複製保存好，等一下要用。**

---

### Step B：取得 Anthropic API Key

1. 前往 [console.anthropic.com](https://console.anthropic.com/)
2. 登入後點 **API Keys** → **Create Key**
3. 複製保存好

---

### Step C：推上 GitHub

1. 在 GitHub 建立一個新的 **private repo**（例如 `food-bot`）
2. 把這個資料夾的內容推上去：
   ```bash
   git init
   git add .
   git commit -m "init"
   git remote add origin https://github.com/你的帳號/food-bot.git
   git push -u origin main
   ```

---

### Step D：部署到 Railway

1. 前往 [railway.app](https://railway.app/) → 用 GitHub 登入
2. **New Project** → **Deploy from GitHub repo** → 選你的 repo
3. 部署完成後，點左側 **Variables**，加入以下三個環境變數：

   | 變數名稱 | 值 |
   |---|---|
   | `TELEGRAM_BOT_TOKEN` | BotFather 給你的 token |
   | `ANTHROPIC_API_KEY` | Anthropic 的 API key |
   | `DB_PATH` | `/data/food_bot.db` |

4. 點 **Settings** → **Networking** → **Generate Domain**
5. 複製你的網址，格式像：`https://food-bot-xxxx.railway.app`

---

### Step E：設定 Telegram Webhook

打開瀏覽器，把下面這個網址貼上去（替換成你的資訊）：

```
https://api.telegram.org/bot【你的TOKEN】/setWebhook?url=https://【你的Railway網址】/webhook
```

例如：
```
https://api.telegram.org/bot7123456789:AAFxxx/setWebhook?url=https://food-bot-xxxx.railway.app/webhook
```

看到 `{"ok":true}` 就代表成功了！

---

### Step F：測試

1. 在 Telegram 搜尋你的 Bot 帳號
2. 傳 `/start` 或「今天吃什麼」
3. 開始對話！

---

## 使用說明

| 指令 | 說明 |
|------|------|
| 今天吃什麼 / /start | 開始詢問流程 |
| 重來 | 重新開始 |
| 記錄 [食物] | 記錄今天吃了什麼，例：`記錄 滷肉飯、燙青菜` |
| /help | 顯示說明 |

---

## 下一步計畫（Step 2+）
- [ ] 天氣串接（OpenWeatherMap）
- [ ] 廚具清單設定
- [ ] 餐廳清單管理
- [ ] 定時主動提醒
- [ ] 熱量分析
