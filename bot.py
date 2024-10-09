from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# Telegram bot token
BOT_TOKEN = '7166361802:AAHXt3FTy2VBo0HcI2Xhv6Eh114G5Ze1X10'

# Nvidia API key
NVIDIA_API_KEY = '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'

# Initialize OpenAI
from openai import OpenAI
openai = OpenAI(api_key=NVIDIA_API_KEY, base_url='https://integrate.api.nvidia.com/v1')

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I am an AI assistant. How can I help you today?")

async def handle_message(update, context):
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
        async for chunk in response:
            result += chunk.choices[0].delta.content or ""

        await context.bot.send_message(chat_id=update.effective_chat.id, text=result)
    except Exception as e:
        print(f"Error: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops, something went wrong. Please try again later.")

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start)
    message_handler = MessageHandler(filters.Text() & ~filters.Command(), handle_message)

    application.add_handler(start_handler)
    application.add_handler(message_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
