const TelegramBot = require('node-telegram-bot-api');
const OpenAI = require('openai');

// Telegram bot token
const BOT_TOKEN = '7166361802:AAHXt3FTy2VBo0HcI2Xhv6Eh114G5Ze1X10';

// Nvidia API key
const NVIDIA_API_KEY = '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';

// Initialize OpenAI
const openai = new OpenAI({
  apiKey: NVIDIA_API_KEY,
  baseURL: 'https://integrate.api.nvidia.com/v1',
});

// Initialize Telegram bot
const bot = new TelegramBot(BOT_TOKEN, { polling: true });

// Handle the /start command
bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  bot.sendMessage(chatId, 'Hello! I am an AI assistant. How can I help you today?');
});

// Handle other messages
bot.on('message', async (msg) => {
  const chatId = msg.chat.id;

  try {
    const completion = await openai.chat.completions.create({
      model: 'meta/llama-3.1-405b-instruct',
      messages: [{ role: 'user', content: msg.text }],
      temperature: 0.2,
      top_p: 0.7,
      max_tokens: 1024,
      stream: true,
    });

    let response = '';
    for await (const chunk of completion) {
      response += chunk.choices[0]?.delta?.content || '';
    }

    bot.sendMessage(chatId, response);
  } catch (error) {
    console.error('Error:', error);
    bot.sendMessage(chatId, 'Oops, something went wrong. Please try again later.');
  }
});
