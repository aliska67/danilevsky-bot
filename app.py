import os
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Здравствуйте. Я Николай Яковлевич Данилевский, автор книги "Россия и Европа".\n\n'
        'Спрашивайте. Буду отвечать прямо, как в моём сочинении.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    
    best_chunk = None
    max_score = 0
    
    for chunk in KNOWLEDGE_BASE:
        score = sum(1 for kw in chunk.get('keywords', []) if kw.lower() in user_text)
        if score > max_score:
            max_score = score
            best_chunk = chunk
    
    if best_chunk and max_score > 0:
        answer = f"{best_chunk.get('original_quote', '')}\n\n— {best_chunk.get('thesis', '')}"
        if len(answer) > 4000:
            answer = answer[:4000] + '…'
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text(
            'Сударь, в моей книге "Россия и Европа" я подробно разобрал этот вопрос.\n\n'
            'Попробуйте спросить про: двойные стандарты Европы, всеславянскую федерацию, Царьград, православие, европейничанье.'
        )

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        logging.error('Ошибка: не найден TELEGRAM_BOT_TOKEN')
        return
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logging.info('Данилевский запущен')
    app.run_polling()

if __name__ == '__main__':
    main()
