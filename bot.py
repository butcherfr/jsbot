from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from openai import OpenAI

# Telegram bot token
BOT_TOKEN = '7166361802:AAHXt3FTy2VBo0HcI2Xhv6Eh114G5Ze1X10'

# Nvidia API key
NVIDIA_API_KEY = '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'

# Initialize OpenAI
openai = OpenAI(api_key=NVIDIA_API_KEY, base_url='https://integrate.api.nvidia.com/v1')

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I am an AI assistant. How can I help you today?")

def handle_message(update, context):
    try:
        response = openai.chat.completions.create(
            model="meta/llama-3.1-405b-instruct",
            messages=[{"role": "user", "content": update.message.text}],
            temperature=0.2,
