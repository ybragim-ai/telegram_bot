
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

BUSINESS_NAME, BUSINESS_TYPE, AUTOMATION_GOAL, CONTACT_INFO = range(4)
ADMIN_ID = 731452613  # Твой ID

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Давай оформим заявку.\nКак называется ваш бизнес?")
    return BUSINESS_NAME

def get_business_name(update: Update, context: CallbackContext):
    context.user_data['business_name'] = update.message.text
    update.message.reply_text("Отлично! В какой сфере ваш бизнес?")
    return BUSINESS_TYPE

def get_business_type(update: Update, context: CallbackContext):
    context.user_data['business_type'] = update.message.text
    update.message.reply_text("Какая главная задача автоматизации?")
    return AUTOMATION_GOAL

def get_automation_goal(update: Update, context: CallbackContext):
    context.user_data['automation_goal'] = update.message.text
    update.message.reply_text("И ваш контакт (телефон, Telegram, email)?")
    return CONTACT_INFO

def get_contact_info(update: Update, context: CallbackContext):
    context.user_data['contact_info'] = update.message.text
    user_data = context.user_data
    admin_message = (
        "🚀 НОВАЯ ЗАЯВКА!\n"
        "====================\n"
        f"🏢 Бизнес: {user_data.get('business_name', 'Не указано')}\n"
        f"📊 Сфера: {user_data.get('business_type', 'Не указано')}\n"
        f"🎯 Задача: {user_data.get('automation_goal', 'Не указано')}\n"
        f"📞 Контакты: {user_data.get('contact_info', 'Не указано')}\n"
        "===================="
    )
    try:
        context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)
    except Exception as e:
        print(f"Ошибка отправки админу: {e}")
    with open("заявки.txt", "a", encoding="utf-8") as f:
        f.write("="*50 + "\n")
        f.write(f"Бизнес: {user_data.get('business_name', 'Не указано')}\n")
        f.write(f"Сфера: {user_data.get('business_type', 'Не указано')}\n")
        f.write(f"Задача: {user_data.get('automation_goal', 'Не указано')}\n")
        f.write(f"Контакты: {user_data.get('contact_info', 'Не указано')}\n")
        f.write("="*50 + "\n\n")
    update.message.reply_text(
        "✅ Спасибо! Заявка принята!\nНаш менеджер свяжется с вами в течение 2 часов.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🤖 Демо-боты", callback_data='demo_bots')],
            [InlineKeyboardButton("📞 Связаться сейчас", callback_data='contacts')],
            [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
        ])
    )
    context.user_data.clear()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Заявка отменена.")
    context.user_data.clear()
    return ConversationHandler.END

def main():
    updater = Updater("8318293519:AAEAgBxKW9-GvajUK586MryxOcbZ6gsIcdI", use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            BUSINESS_NAME: [MessageHandler(Filters.text & ~Filters.command, get_business_name)],
            BUSINESS_TYPE: [MessageHandler(Filters.text & ~Filters.command, get_business_type)],
            AUTOMATION_GOAL: [MessageHandler(Filters.text & ~Filters.command, get_automation_goal)],
            CONTACT_INFO: [MessageHandler(Filters.text & ~Filters.command, get_contact_info)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
