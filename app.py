import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

logging.basicConfig(level=logging.INFO)

# Загружаем чанки
try:
    with open('knowledge_base.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        KNOWLEDGE_BASE = data['knowledge_base']
    logging.info(f"Загружено {len(KNOWLEDGE_BASE)} чанков")
except Exception as e:
    logging.error(f"Ошибка загрузки: {e}")
    KNOWLEDGE_BASE = []

# Подключаем DeepSeek
DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY')
if DEEPSEEK_API_KEY:
    deepseek_client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com/v1")
    logging.info("DeepSeek подключён")
else:
    deepseek_client = None
    logging.warning("DeepSeek не настроен")

SYSTEM_PROMPT = """Ты — Николай Яковлевич Данилевский, русский философ, автор книги "Россия и Европа".

Твои убеждения:
- Европа враждебна России не случайно, а системно
- Россия не принадлежит к Европе как культурно-историческому типу
- Православие — единственная истинная форма христианства
- Всеславянская федерация под гегемонией России — единственное решение
- Царьград должен быть столицей Всеславянского союза

Твой стиль:
- Говори уверенно, с иронией
- Используй метафоры ("прививка", "гниение Запада", "Марья Алексеевна")
- Ссылайся на исторические примеры (1864 и 1854 годы, Греция, Рим, Наполеон)
- Отвечай на любой вопрос как Данилевский, даже если вопрос не о политике"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Здравствуйте. Я Николай Яковлевич Данилевский, автор книги "Россия и Европа".\n\n'
        'Спрашивайте что угодно — я отвечу как философ.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text
    
    # Если DeepSeek не настроен — используем старый поиск
    if not deepseek_client:
        await update.message.reply_text("DeepSeek не настроен. Добавьте API ключ в переменные окружения.")
        return
    
    await update.message.reply_text("Размышляю...")
    
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Вопрос: {user_question}\n\nОтветь как Данилевский."}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)
    except Exception as e:
        logging.error(f"DeepSeek error: {e}")
        await update.message.reply_text(
            "Сударь, что-то с моей связью. Попробуйте ещё раз позже."
        )

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logging.error('Нет TELEGRAM_BOT_TOKEN')
        return
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info('Данилевский запущен')
    app.run_polling()

if __name__ == '__main__':
    main()
