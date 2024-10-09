from telegram.ext import Updater, CommandHandler, MessageHandler, filters
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
            top_p=0.7,
            max_tokens=1024,
            stream=True
        )

        result = ""
        for chunk in response:
            result += chunk.choices[0].delta.content or ""

        context.bot.send_message(chat_id=update.effective_chat.id, text=result)
    except Exception as e:
        print(f"Error: {e}")
        context.bot.send_message(chat_id=update.effective_chat.id, text="Oops, something went wrong. Please try again later.")

def main():
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.text & ~filters.command, handle_message)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(message_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
