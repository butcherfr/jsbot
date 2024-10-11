// Constants for API keys, should be loaded from environment variables
const TMDB_API_KEY = '69084ded6889a849708077681bd5dd7f';
const BOT_TOKEN = '8153935470:AAETIPoq3zdQg2kDFvmxSgVQ9Wz_1R8ophU';
const BASE_URL = 'https://media.themoviedb.org/t/p/w300_and_h450_bestv2';

// Function to send messages to the Telegram chat
async function sendMessage(chatId, text, options = {}) {
    const url = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;
    const body = { chat_id: chatId, text, ...options };

    const response = await fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body),
    });

    return await response.json();
}

// Handle incoming messages
async function handleMessage(message) {
    const chatId = message.chat.id;
    const text = message.text;

    if (text === '/start') {
        const welcomeMessage = "Welcome to the Movie Explorer Bot! 🎬\nType /search [movie name] to find movies or TV shows.";
        await sendMessage(chatId, welcomeMessage);
    } else if (text.startsWith('/search')) {
        const query = text.split(' ').slice(1).join(' ');
        if (!query) {
            await sendMessage(chatId, "Please provide a search query. Example: /search Inception");
            return;
        }
        await handleSearch(chatId, query);
    }
}

// Function to search for media and display results with pagination
async function handleSearch(chatId, query, page = 1) {
    const apiUrl = `https://api.themoviedb.org/3/search/multi?api_key=${TMDB_API_KEY}&query=${encodeURIComponent(query)}&page=${page}`;
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        const total_pages = data.total_pages;

        if (data.results && data.results.length) {
            const results = data.results.slice(0, 5);
            const inlineKeyboard = {
                inline_keyboard: [
                    ...results.map(result => [{
                        text: result.title || result.name,
                        callback_data: `detail_${result.id}_${result.media_type}`
                    }]),
                    [
                        {text: '← Prev', callback_data: `change_${query}_${Math.max(page - 1, 1)}`},
                        {text: `${page}/${total_pages}`, callback_data: 'noop'},
                        {text: 'Next →', callback_data: `change_${query}_${Math.min(page + 1, total_pages)}`}
                    ].filter(btn => btn.callback_data.includes(String(page)) || btn.text === 'noop')
                ]
            };
            await sendMessage(chatId, 'Select a title to get more details:', {reply_markup: inlineKeyboard});
        } else {
            await sendMessage(chatId, `No results found for "${query}".`);
        }
    } catch (error) {
        await sendMessage(chatId, `Error searching for "${query}": ${error.message}`);
    }
}

// Function to display detailed information with poster
async function handleDetails(chatId, id, type) {
    const apiUrl = `https://api.themoviedb.org/3/${type}/${id}?api_key=${TMDB_API_KEY}&append_to_response=images`;
    try {
        const response = await fetch(apiUrl);
        const data = await response.json();
        const details = `*${data.title || data.name}*\n_Release Date_: ${data.release_date || data.first_air_date}\n_Rating_: ${data.vote_average}\n\n${data.overview}`;
        const posterUrl = data.backdrop_path ? `${BASE_URL}${data.backdrop_path}` : null;

        if (posterUrl) {
            await sendMessage(chatId, `<a href="${posterUrl}">&#8205;</a>${details}`, { parse_mode: 'HTML' });
        } else {
            await sendMessage(chatId, details, { parse_mode: 'Markdown' });
        }
    } catch (error) {
        await sendMessage(chatId, `Failed to fetch details: ${error.message}`);
    }
}

// Function to handle callback queries from inline keyboards
async function handleCallbackQuery(callbackQuery) {
    const chatId = callbackQuery.message.chat.id;
    const data = callbackQuery.data;
    const [action, param1, param2] = data.split('_');

    if (action === 'detail') {
        await handleDetails(chatId, param1, param2);
    } else if (action === 'change') {
        if (param2 > 0) {
            await handleSearch(chatId, param1, parseInt(param2));
        }
    }
}

// Main event listener for incoming HTTP requests
addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request));
});

// Handle incoming HTTP requests
async function handleRequest(request) {
    if (request.url.endsWith('/webhook')) {
        const update = await request.json();
        if (update.message) {
            await handleMessage(update.message);
        } else if (update.inline_query) {
            // Implement if required
        } else if (update.callback_query) {
            await handleCallbackQuery(update.callback_query);
        }
        return new Response('OK', { status: 200 });
    }
    return new Response('Not Found', { status: 404 });
        }
