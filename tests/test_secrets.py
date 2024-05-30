import os

# 从环境变量中获取 Secrets
telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
weibo_id = os.environ.get("WEIBO_ID")

# 打印获取到的 Secrets
print("Telegram Bot Token:", telegram_bot_token)
print("Telegram Chat ID:", telegram_chat_id)
print("Weibo ID:", weibo_id)
