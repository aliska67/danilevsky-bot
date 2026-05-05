import os
import json
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Загружаем чанки
with open('knowledge_base.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    KNOWLEDGE_BASE = data['knowledge_base']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Здравствуйте. Я Николай Яковлевич Данилевский, автор книги "Россия и Европа".\n\n'
        'Спрашивайте. Буду отвечать прямо, как в моём сочинении. Европе это не понравится, но мне всё равно.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()
    
    best_chunk = None
    max_score = 0
    
    for chunk in KNOWLEDGE_BASE:
        score = 0
        for kw in chunk['keywords']:
            if kw.lower() in user_text:
                score += 1
        if score > max_score:
            max_score = score
            best_chunk = chunk
    
    if best_chunk and max_score > 0:
        answer = f"{best_chunk['original_quote']}\n\n— {best_chunk['thesis']}"
        if len(answer) > 4000:
            answer = answer[:4000] + '…'
        await update.message.reply_text(answer)
    else:
        await update.message.reply_text(
            'Сударь, в моей книге "Россия и Европа" я подробно разобрал этот вопрос. '
            'Почитайте главы о культурно-исторических типах.'
        )

def main():
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print('Ошибка: не найден TELEGRAM_BOT_TOKEN')
        return
    
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print('Данилевский запущен. Спрашивайте.')
    app.run_polling()

if __name__ == '__main__':
    main()
