from lib2to3.fixes.fix_input import context
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import requests
from datetime import datetime

# Load API keys from environment variables
TMDB_API_KEY = '69084ded6889a849708077681bd5dd7f'
BOT_TOKEN = '7501751569:AAETZdiv2Er_l8YVSciALtEzvY5ic12figo'
BASE_URL = 'https://image.tmdb.org/t/p/w300'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

async def start(update: Update, context):
    await update.message.reply_text("Welcome to the Movie Explorer Bot! 🎬\nType /search [movie name] to find movies or TV shows.")

async def search(update: Update, context):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("Please provide a search query. Example: /search Inception")
        return
    await handle_search(update.message.chat_id, query, context)

async def handle_search(chat_id, query, context, page=1):
    apiUrl = f'https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={query}&page={page}'
    response = requests.get(apiUrl)
    data = response.json()
    total_pages = data.get('total_pages', 0)

    if data.get('results') and len(data['results']) > 0:
        results = data['results'][:5]
        buttons = []
        for result in results:
            title = result.get('title') or result.get('name')  # Safely getting title or name
            media_type = result.get('media_type', 'movie')    # Default to 'movie' if not specified
            if title:  # Ensure there's a title or name to create a button
                buttons.append([InlineKeyboardButton(text=title, callback_data=f"detail_{result['id']}_{media_type}")])

        navigation_buttons = []
        if page > 1:
            navigation_buttons.append(InlineKeyboardButton(text='← Prev', callback_data=f"change_{query}_{page - 1}"))
        navigation_buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data='noop'))
        if page < total_pages:
            navigation_buttons.append(InlineKeyboardButton(text='Next →', callback_data=f"change_{query}_{page + 1}"))

        if navigation_buttons:
            buttons.append(navigation_buttons)

        reply_markup = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id, 'Select a title to get more details:', reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id, f'No results found for "{query}".')

async def handle_details(chat_id, id, type, context):
    apiUrl = f'https://api.themoviedb.org/3/{type}/{id}?api_key={TMDB_API_KEY}&append_to_response=images'
    response = requests.get(apiUrl)
    data = response.json()

    title = data.get('title') or data.get('name')  # Safely getting title or name
    release_date = data.get('release_date') or data.get('first_air_date')
    vote_average = data.get('vote_average', 'N/A')
    overview = data.get('overview', 'No description available.')
    posterUrl = f"{BASE_URL}{data.get('backdrop_path')}" if data.get('backdrop_path') else None

    release_datetime = datetime.strptime(release_date, '%Y-%m-%d') if release_date else None
    today = datetime.today()

    if release_datetime and release_datetime < today:
        message_text = f"The movie or TV show has already been released on {release_date}."
        reply_markup = None  # Ensure reply_markup is always defined
    else:
        message_text = (
            f"*{title}*\n"
            f"📅 Release Date: {release_date}\n"
            f"⭐ Rating: {vote_average}/10\n"
            f"{overview}"
        )
        if release_datetime:
            buttons = [[InlineKeyboardButton(text="🔔 Remind Me", callback_data=f"remind_{chat_id}_{id}_{release_date}")]]
            reply_markup = InlineKeyboardMarkup(buttons)
        else:
            reply_markup = None  # Define reply_markup even if there's no future release date

    if posterUrl:
        await context.bot.send_message(chat_id, f'<a href="{posterUrl}">&#8205;</a>{message_text}', parse_mode='HTML', reply_markup=reply_markup)
    else:
        await context.bot.send_message(chat_id, message_text, parse_mode='Markdown', reply_markup=reply_markup)

async def callback_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data.split('_')
    action = data[0]
    param1 = data[1]
    if action == 'detail':
        await handle_details(query.message.chat_id, param1, data[2], context)
    elif action == 'change':
        await handle_search(query.message.chat_id, param1, context, int(data[2]))

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
