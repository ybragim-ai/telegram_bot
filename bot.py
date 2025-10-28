import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Твой ID в Telegram (замени на свои цифры из @userinfobot!)
ADMIN_ID = 731452613

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния для диалога
BUSINESS_NAME, BUSINESS_TYPE, AUTOMATION_GOAL, CONTACT_INFO = range(4)

# Глобальные переменные для корзин
user_carts = {}

# ========== КЛАВИАТУРЫ ==========
def get_main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🤖 Демо-боты", callback_data='demo_bots')],
        [InlineKeyboardButton("💼 Услуги и цены", callback_data='services')],
        [InlineKeyboardButton("💬 Оставить заявку", callback_data='leave_request')],
        [InlineKeyboardButton("📞 Контакты", callback_data='contacts')]
    ])

def get_demo_bots_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🍕 Пиццерия", callback_data='demo_pizza')],
        [InlineKeyboardButton("☕ Кофейня", callback_data='demo_coffee')],
        [InlineKeyboardButton("💇 Салон красоты", callback_data='demo_salon')],
        [InlineKeyboardButton("🚚 Служба доставки", callback_data='demo_delivery')],
        [InlineKeyboardButton("🏪 Магазин продуктов", callback_data='demo_store')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ])

def get_cancel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отменить заявку", callback_data='cancel')]
    ])

# ========== ГЛАВНОЕ МЕНЮ ==========
async def start(update: Update, context):
    if update.message:
        await update.message.reply_text(
            "👋 Привет! Я демо-бот NeiraLab Digital Tehnology:\n"
            "• Автоматизировать заказы 24/7\n"  
            "• Увеличить продажи на 15-30%\n"
            "• Снизить нагрузку на staff\n"
            "• Принимать оплаты онлайн\n\n"
            "Выберите опцию:",
            reply_markup=get_main_menu_keyboard()
        )

# ========== ОБРАБОТЧИК КНОПОК ==========
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    # Основное меню
    if query.data == 'demo_bots':
        await show_demo_bots(query)
    elif query.data == 'services':
        await show_services(query)
    elif query.data == 'leave_request':
        await start_leave_request(update, context)
    elif query.data == 'contacts':
        await show_contacts(query)
    elif query.data == 'back_to_main':
        await back_to_main(query)
    elif query.data == 'back_to_demos':
        await show_demo_bots(query)
    
    # Демо-боты
    elif query.data == 'demo_pizza':
        await demo_pizza_bot(query)
    elif query.data == 'demo_coffee':
        await demo_coffee_bot(query)
    elif query.data == 'demo_salon':
        await demo_salon_bot(query)
    elif query.data == 'demo_delivery':
        await demo_delivery_bot(query)
    elif query.data == 'demo_store':
        await demo_store_bot(query)
    
    # Пиццерия
    elif query.data == 'pizza_menu':
        await show_pizza_menu(query)
    elif query.data == 'pizza_cart':
        await show_pizza_cart(query)
    elif query.data == 'pizza_clear':
        await clear_pizza_cart(query)
    elif query.data == 'pizza_order':
        await process_pizza_order(query)
    elif query.data.startswith('add_pizza_'):
        pizza_type = query.data.replace('add_pizza_', '')
        await add_pizza_to_cart(query, pizza_type)
    elif query.data == 'pizza_promo':
        await show_pizza_promo(query)
    
    # Кофейня
    elif query.data == 'coffee_menu':
        await show_coffee_menu(query)
    elif query.data == 'coffee_cart':
        await show_coffee_cart(query)
    elif query.data == 'coffee_clear':
        await clear_coffee_cart(query)
    elif query.data == 'coffee_order':
        await process_coffee_order(query)
    elif query.data.startswith('add_coffee_'):
        coffee_type = query.data.replace('add_coffee_', '')
        await add_coffee_to_cart(query, coffee_type)
    elif query.data == 'coffee_loyalty':
        await show_coffee_loyalty(query)
    
    # Салон красоты
    elif query.data == 'salon_services':
        await show_salon_services(query)
    elif query.data == 'salon_booking':
        await start_salon_booking(query)
    elif query.data == 'salon_masters':
        await show_salon_masters(query)
    
    # Доставка
    elif query.data == 'delivery_order':
        await start_delivery_order(query)
    elif query.data == 'delivery_tracking':
        await show_delivery_tracking(query)
    
    # Магазин
    elif query.data == 'store_catalog':
        await show_store_catalog(query)
    elif query.data == 'store_cart':
        await show_store_cart(query)
    elif query.data.startswith('add_store_'):
        item = query.data.replace('add_store_', '')
        await add_store_to_cart(query, item)
    
    elif query.data == 'cancel':
        await cancel_conversation(update, context)

# ========== ВЫБОР ДЕМО-БОТОВ ==========
async def show_demo_bots(query):
    await query.edit_message_text(
        "🤖 Выберите демо-бот для вашей сферы:\n\n"
        "Посмотрите как работают чат-боты в разных бизнесах:",
        reply_markup=get_demo_bots_keyboard()
    )

# ========== ДЕМО ПИЦЦЕРИЯ ==========
async def demo_pizza_bot(query):
    user_id = query.from_user.id
    if user_id not in user_carts:
        user_carts[user_id] = {'pizza': {}}
    elif 'pizza' not in user_carts[user_id]:
        user_carts[user_id]['pizza'] = {}
    
    keyboard = [
        [InlineKeyboardButton("🍕 Посмотреть меню", callback_data='pizza_menu')],
        [InlineKeyboardButton("🛒 Корзина", callback_data='pizza_cart')],
        [InlineKeyboardButton("🎁 Акции", callback_data='pizza_promo')],
        [InlineKeyboardButton("📦 Оформить заказ", callback_data='pizza_order')],
        [InlineKeyboardButton("↩️ К выбору ботов", callback_data='back_to_demos')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "🍕 Добро пожаловать в виртуальную пиццерию!\n\n"
        "Здесь вы можете:\n"
        "• Выбрать пиццу из меню\n"
        "• Добавить в корзину\n"
        "• Посмотреть акции\n"
        "• Оформить заказ\n\n"
        "Выберите опцию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_pizza_menu(query):
    keyboard = [
        [InlineKeyboardButton("🍕 Маргарита - 450 руб.", callback_data='add_pizza_margarita')],
        [InlineKeyboardButton("🍕 Пепперони - 500 руб.", callback_data='add_pizza_pepperoni')],
        [InlineKeyboardButton("🍕 Гавайская - 550 руб.", callback_data='add_pizza_hawaiian')],
        [InlineKeyboardButton("🍕 Четыре сыра - 600 руб.", callback_data='add_pizza_cheese')],
        [InlineKeyboardButton("🛒 Корзина", callback_data='pizza_cart')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_pizza')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "🍕 Меню пиццерии:\n\n"
        "Выберите пиццу для добавления в корзину:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_pizza_to_cart(query, pizza_type):
    user_id = query.from_user.id
    
    # Инициализируем корзину если нужно
    if user_id not in user_carts:
        user_carts[user_id] = {'pizza': {}}
    elif 'pizza' not in user_carts[user_id]:
        user_carts[user_id]['pizza'] = {}
    
    pizza_names = {
        'margarita': 'Маргарита',
        'pepperoni': 'Пепперони',
        'hawaiian': 'Гавайская',
        'cheese': 'Четыре сыра'
    }
    
    if pizza_type in user_carts[user_id]['pizza']:
        user_carts[user_id]['pizza'][pizza_type] += 1
    else:
        user_carts[user_id]['pizza'][pizza_type] = 1
    
    await query.answer(f"✅ {pizza_names[pizza_type]} добавлена в корзину!")
    await show_pizza_menu(query)

async def show_pizza_cart(query):
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {}).get('pizza', {})
    
    if not cart:
        text = "🛒 Ваша корзина пуста"
    else:
        text = "🛒 Ваша корзина:\n\n"
        total = 0
        pizza_names = {
            'margarita': 'Маргарита',
            'pepperoni': 'Пепперони',
            'hawaiian': 'Гавайская',
            'cheese': 'Четыре сыра'
        }
        pizza_prices = {
            'margarita': 450,
            'pepperoni': 500,
            'hawaiian': 550,
            'cheese': 600
        }
        
        for pizza_type, quantity in cart.items():
            price = pizza_prices[pizza_type] * quantity
            total += price
            text += f"• {pizza_names[pizza_type]} - {quantity} шт. = {price} руб.\n"
        
        text += f"\n💰 Итого: {total} руб."
    
    keyboard = [
        [InlineKeyboardButton("🍕 Продолжить покупки", callback_data='pizza_menu')],
        [InlineKeyboardButton("🗑 Очистить корзину", callback_data='pizza_clear')],
        [InlineKeyboardButton("📦 Оформить заказ", callback_data='pizza_order')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_pizza')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def clear_pizza_cart(query):
    user_id = query.from_user.id
    if user_id in user_carts and 'pizza' in user_carts[user_id]:
        user_carts[user_id]['pizza'] = {}
    await query.answer("🗑 Корзина очищена!")
    await show_pizza_cart(query)

async def process_pizza_order(query):
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {}).get('pizza', {})
    
    if not cart:
        await query.answer("❌ Корзина пуста!")
        return
    
    await query.edit_message_text(
        "🎉 Отлично! Вы протестировали функционал бота для пиццерии!\n\n"
        "В реальном боте:\n"
        "• Заказ был бы отправлен на кухню\n"
        "• Вы получили бы номер заказа\n"
        "• Можно было бы отслеживать статус\n"
        "• Оплата прошла бы онлайн\n\n"
        "Хотите такой же бот для вашего бизнеса?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Рассчитать стоимость", callback_data='leave_request')],
            [InlineKeyboardButton("📞 Связаться сейчас", callback_data='contacts')],
            [InlineKeyboardButton("🍕 Вернуться в пиццерию", callback_data='demo_pizza')],
            [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
        ])
    )

async def show_pizza_promo(query):
    await query.edit_message_text(
        "🎁 Акции в пиццерии:\n\n"
        "🔥 2 пиццы по цене 1\n"
        "Промокод: PIZZA2\n\n"
        "🎉 Скидка 20% на первый заказ\n"
        "Промокод: WELCOME20\n\n"
        "👑 Каждый 5-й заказ бесплатно!\n\n"
        "В реальном боте промокоды применяются автоматически!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🍕 Перейти к меню", callback_data='pizza_menu')],
            [InlineKeyboardButton("↩️ Назад", callback_data='demo_pizza')]
        ])
    )

# ========== ДЕМО КОФЕЙНЯ ==========
async def demo_coffee_bot(query):
    user_id = query.from_user.id
    if user_id not in user_carts:
        user_carts[user_id] = {'coffee': {}}
    elif 'coffee' not in user_carts[user_id]:
        user_carts[user_id]['coffee'] = {}
    
    keyboard = [
        [InlineKeyboardButton("☕ Меню напитков", callback_data='coffee_menu')],
        [InlineKeyboardButton("🛒 Корзина", callback_data='coffee_cart')],
        [InlineKeyboardButton("👑 Программа лояльности", callback_data='coffee_loyalty')],
        [InlineKeyboardButton("📦 Оформить заказ", callback_data='coffee_order')],
        [InlineKeyboardButton("↩️ К выбору ботов", callback_data='back_to_demos')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "☕ Добро пожаловать в виртуальную кофейню!\n\n"
        "Здесь вы можете:\n"
        "• Выбрать кофе и напитки\n"
        "• Добавить в корзину\n"
        "• Участвовать в программе лояльности\n"
        "• Оформить предзаказ\n\n"
        "Выберите опцию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_coffee_menu(query):
    keyboard = [
        [InlineKeyboardButton("☕ Эспрессо - 150 руб.", callback_data='add_coffee_espresso')],
        [InlineKeyboardButton("☕ Американо - 180 руб.", callback_data='add_coffee_americano')],
        [InlineKeyboardButton("☕ Капучино - 220 руб.", callback_data='add_coffee_cappuccino')],
        [InlineKeyboardButton("☕ Латте - 240 руб.", callback_data='add_coffee_latte')],
        [InlineKeyboardButton("🍵 Чай - 120 руб.", callback_data='add_coffee_tea')],
        [InlineKeyboardButton("🛒 Корзина", callback_data='coffee_cart')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_coffee')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "☕ Меню кофейни:\n\n"
        "Выберите напиток для добавления в корзину:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_coffee_to_cart(query, coffee_type):
    user_id = query.from_user.id
    
    # Инициализируем корзину если нужно
    if user_id not in user_carts:
        user_carts[user_id] = {'coffee': {}}
    elif 'coffee' not in user_carts[user_id]:
        user_carts[user_id]['coffee'] = {}
    
    coffee_names = {
        'espresso': 'Эспрессо',
        'americano': 'Американо',
        'cappuccino': 'Капучино',
        'latte': 'Латте',
        'tea': 'Чай'
    }
    
    if coffee_type in user_carts[user_id]['coffee']:
        user_carts[user_id]['coffee'][coffee_type] += 1
    else:
        user_carts[user_id]['coffee'][coffee_type] = 1
    
    await query.answer(f"✅ {coffee_names[coffee_type]} добавлен в корзину!")
    await show_coffee_menu(query)

async def show_coffee_cart(query):
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {}).get('coffee', {})
    
    if not cart:
        text = "🛒 Ваша корзина пуста"
    else:
        text = "🛒 Ваша корзина:\n\n"
        total = 0
        coffee_names = {
            'espresso': 'Эспрессо',
            'americano': 'Американо',
            'cappuccino': 'Капучино',
            'latte': 'Латте',
            'tea': 'Чай'
        }
        coffee_prices = {
            'espresso': 150,
            'americano': 180,
            'cappuccino': 220,
            'latte': 240,
            'tea': 120
        }
        
        for coffee_type, quantity in cart.items():
            price = coffee_prices[coffee_type] * quantity
            total += price
            text += f"• {coffee_names[coffee_type]} - {quantity} шт. = {price} руб.\n"
        
        text += f"\n💰 Итого: {total} руб."
    
    keyboard = [
        [InlineKeyboardButton("☕ Продолжить покупки", callback_data='coffee_menu')],
        [InlineKeyboardButton("🗑 Очистить корзину", callback_data='coffee_clear')],
        [InlineKeyboardButton("📦 Оформить заказ", callback_data='coffee_order')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_coffee')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def clear_coffee_cart(query):
    user_id = query.from_user.id
    if user_id in user_carts and 'coffee' in user_carts[user_id]:
        user_carts[user_id]['coffee'] = {}
    await query.answer("🗑 Корзина очищена!")
    await show_coffee_cart(query)

async def process_coffee_order(query):
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {}).get('coffee', {})
    
    if not cart:
        await query.answer("❌ Корзина пуста!")
        return
    
    await query.edit_message_text(
        "🎉 Отлично! Вы протестировали функционал бота для кофейни!\n\n"
        "В реальном боте:\n"
        "• Заказ был бы передан бариста\n"
        "• Вы получили бы номер заказа\n"
        "• Можно было бы указать время готовности\n"
        "• Начислены бонусные баллы\n\n"
        "Хотите такой же бот для вашего бизнеса?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Рассчитать стоимость", callback_data='leave_request')],
            [InlineKeyboardButton("📞 Связаться сейчас", callback_data='contacts')],
            [InlineKeyboardButton("☕ Вернуться в кофейню", callback_data='demo_coffee')],
            [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
        ])
    )

async def show_coffee_loyalty(query):
    await query.edit_message_text(
        "👑 Программа лояльности:\n\n"
        "⭐ Ваш статус: Золотой клиент\n"
        "🎯 Накоплено: 8 из 10 звезд\n\n"
        "🎁 Ваши привилегии:\n"
        "• Скидка 10% на все заказы\n"
        "• Бесплатная добавка сиропа\n"
        "• Приоритетное приготовление\n\n"
        "🔥 Ближайшая награда:\n"
        "Ещё 2 звезды до бесплатного кофе!\n\n"
        "В реальном боте баллы начисляются автоматически!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("☕ Перейти к меню", callback_data='coffee_menu')],
            [InlineKeyboardButton("↩️ Назад", callback_data='demo_coffee')]
        ])
    )

# ========== ДЕМО МАГАЗИНА ПРОДУКТОВ ==========
async def demo_store_bot(query):
    user_id = query.from_user.id
    if user_id not in user_carts:
        user_carts[user_id] = {'store': {}}
    elif 'store' not in user_carts[user_id]:
        user_carts[user_id]['store'] = {}
    
    keyboard = [
        [InlineKeyboardButton("🛒 Каталог товаров", callback_data='store_catalog')],
        [InlineKeyboardButton("📦 Корзина", callback_data='store_cart')],
        [InlineKeyboardButton("↩️ К выбору ботов", callback_data='back_to_demos')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "🏪 Добро пожаловать в виртуальный продуктовый магазин!\n\n"
        "Здесь вы можете:\n"
        "• Посмотреть каталог товаров\n"
        "• Добавить товары в корзину\n"
        "• Оформить заказ с доставкой\n"
        "• Использовать промокоды\n\n"
        "Выберите опцию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_store_catalog(query):
    keyboard = [
        [InlineKeyboardButton("🥛 Молоко - 80 руб.", callback_data='add_store_milk')],
        [InlineKeyboardButton("🍞 Хлеб - 45 руб.", callback_data='add_store_bread')],
        [InlineKeyboardButton("🥚 Яйца - 120 руб.", callback_data='add_store_eggs')],
        [InlineKeyboardButton("🍬 Сахар - 65 руб.", callback_data='add_store_sugar')],
        [InlineKeyboardButton("📦 Корзина", callback_data='store_cart')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_store')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "🛒 Каталог товаров:\n\n"
        "Выберите товар для добавления в корзину:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def add_store_to_cart(query, item):
    user_id = query.from_user.id
    
    # Инициализируем корзину если нужно
    if user_id not in user_carts:
        user_carts[user_id] = {'store': {}}
    elif 'store' not in user_carts[user_id]:
        user_carts[user_id]['store'] = {}
    
    item_names = {
        'milk': 'Молоко',
        'bread': 'Хлеб',
        'eggs': 'Яйца',
        'sugar': 'Сахар'
    }
    
    if item in user_carts[user_id]['store']:
        user_carts[user_id]['store'][item] += 1
    else:
        user_carts[user_id]['store'][item] = 1
    
    await query.answer(f"✅ {item_names[item]} добавлен в корзину!")
    await show_store_catalog(query)

async def show_store_cart(query):
    user_id = query.from_user.id
    cart = user_carts.get(user_id, {}).get('store', {})
    
    if not cart:
        text = "🛒 Ваша корзина пуста"
    else:
        text = "🛒 Ваша корзина:\n\n"
        total = 0
        item_names = {
            'milk': 'Молоко',
            'bread': 'Хлеб',
            'eggs': 'Яйца',
            'sugar': 'Сахар'
        }
        item_prices = {
            'milk': 80,
            'bread': 45,
            'eggs': 120,
            'sugar': 65
        }
        
        for item, quantity in cart.items():
            price = item_prices[item] * quantity
            total += price
            text += f"• {item_names[item]} - {quantity} шт. = {price} руб.\n"
        
        delivery = 150 if total < 1500 else 0
        final_total = total + delivery
        
        text += f"\n💰 Товары: {total} руб."
        text += f"\n🚚 Доставка: {delivery} руб."
        text += f"\n💎 Итого: {final_total} руб."
        
        if total < 1500:
            text += f"\n\n🎁 Добавьте товаров на {1500 - total} руб. для бесплатной доставки!"
    
    keyboard = [
        [InlineKeyboardButton("🛒 Продолжить покупки", callback_data='store_catalog')],
        [InlineKeyboardButton("📦 Оформить заказ", callback_data='delivery_order')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_store')]
    ]
    
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== ОСТАЛЬНЫЕ ДЕМО-БОТЫ (без изменений) ==========
async def demo_salon_bot(query):
    keyboard = [
        [InlineKeyboardButton("💇 Услуги и цены", callback_data='salon_services')],
        [InlineKeyboardButton("👩‍💼 Наши мастера", callback_data='salon_masters')],
        [InlineKeyboardButton("📅 Записаться онлайн", callback_data='salon_booking')],
        [InlineKeyboardButton("↩️ К выбору ботов", callback_data='back_to_demos')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "💇 Добро пожаловать в виртуальный салон красоты!\n\n"
        "Здесь вы можете:\n"
        "• Посмотреть услуги и цены\n"
        "• Выбрать мастера\n"
        "• Записаться на удобное время\n"
        "• Получить напоминание о визите\n\n"
        "Выберите опцию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_salon_services(query):
    services_text = (
        "💇 Наши услуги:\n\n"
        "Парикмахерские услуги:\n"
        "• Стрижка женская - 1200 руб.\n"
        "• Стрижка мужская - 800 руб.\n" 
        "• Окрашивание - от 2500 руб.\n"
        "• Укладка - 600 руб.\n\n"
        "Ногтевой сервис:\n"
        "• Маникюр - 900 руб.\n"
        "• Педикюр - 1200 руб.\n"
        "• Покрытие гель-лак - 600 руб.\n\n"
        "🎁 Акция: Приведи подругу - получи скидку 20%!"
    )
    
    keyboard = [
        [InlineKeyboardButton("📅 Записаться", callback_data='salon_booking')],
        [InlineKeyboardButton("👩‍💼 Наши мастера", callback_data='salon_masters')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_salon')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(services_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def show_salon_masters(query):
    masters_text = (
        "👩‍💼 Наша команда:\n\n"
        "💎 Анна - топ-стилист\n"
        "Стаж: 8 лет\n"
        "Специализация: окрашивание, сложные стрижки\n\n"
        "💎 Мария - мастер ногтевого сервиса\n"
        "Стаж: 5 лет\n"
        "Специализация: аппаратный маникюр\n\n"
        "💎 Елена - визажист\n"
        "Стаж: 6 лет\n"
        "Специализация: вечерний макияж\n\n"
        "Клиенты могут выбирать мастера при записи"
    )
    
    keyboard = [
        [InlineKeyboardButton("📅 Записаться", callback_data='salon_booking')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_salon')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(masters_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_salon_booking(query):
    await query.edit_message_text(
        "🎉 Отлично! Вы протестировали функционал бота для салона красоты!\n\n"
        "В реальном боте:\n"
        "• Выбрали бы мастера и услугу\n"
        "• Выбрали удобное время\n"
        "• Получили подтверждение записи\n"
        "• Получили напоминание за день и за час\n\n"
        "Хотите такой же бот для вашего бизнеса?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Рассчитать стоимость", callback_data='leave_request')],
            [InlineKeyboardButton("📞 Связаться сейчас", callback_data='contacts')],
            [InlineKeyboardButton("💇 Вернуться в салон", callback_data='demo_salon')],
            [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
        ])
    )

async def demo_delivery_bot(query):
    keyboard = [
        [InlineKeyboardButton("🚚 Сделать заказ", callback_data='delivery_order')],
        [InlineKeyboardButton("📊 Отследить заказ", callback_data='delivery_tracking')],
        [InlineKeyboardButton("↩️ К выбору ботов", callback_data='back_to_demos')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(
        "🚚 Добро пожаловать в виртуальную службу доставки!\n\n"
        "Здесь вы можете:\n"
        "• Рассчитать стоимость доставки\n"
        "• Создать заказ на доставку\n"
        "• Отслеживать заказ в реальном времени\n"
        "• Связаться с курьером\n\n"
        "Выберите опцию:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_delivery_tracking(query):
    tracking_text = (
        "📊 Отслеживание заказа:\n\n"
        "🟢 Заказ #12345\n"
        "Статус: Курьер в пути\n"
        "Курьер: Дмитрий\n"
        "Телефон: +7 XXX XXX-XX-XX\n"
        "Примерное время: 15-20 минут\n\n"
        "Маршрут:\n"
        "ул. Пушкина, 10 → ул. Ленина, 25\n\n"
        "В реальном боте отслеживание работает в реальном времени"
    )
    
    keyboard = [
        [InlineKeyboardButton("🚚 Сделать заказ", callback_data='delivery_order')],
        [InlineKeyboardButton("↩️ Назад", callback_data='demo_delivery')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(tracking_text, reply_markup=InlineKeyboardMarkup(keyboard))

async def start_delivery_order(query):
    await query.edit_message_text(
        "🎉 Отлично! Вы протестировали функционал бота для службы доставки!\n\n"
        "В реальном боте:\n"
        "• Указали бы адрес забора и доставки\n"
        "• Выбрали тип доставки (эконом/экспресс)\n"
        "• Рассчитали стоимость\n"
        "• Отслеживали заказ на карте\n\n"
        "Хотите такой же бот для вашего бизнеса?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Рассчитать стоимость", callback_data='leave_request')],
            [InlineKeyboardButton("📞 Связаться сейчас", callback_data='contacts')],
            [InlineKeyboardButton("🚚 Вернуться в доставку", callback_data='demo_delivery')],
            [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
        ])
    )

# ========== УСЛУГИ И ЦЕНЫ ==========
async def show_services(query):
    services_text = (
        "💼 Наши услуги:\n\n"
        "Чат-боты для бизнеса\n"
        "• Прием заказов и записей\n"
        "• Автоответчик на вопросы\n"
        "• Интеграция с CRM\n"
        "• Онлайн-оплата\n"
        "• Аналитика и отчеты\n\n"
        "Стоимость:\n"
        "• Базовый бот - от 15 000 руб.\n"
        "• Продвинутый бот - от 25 000 руб.\n"
        "• Интеграции - от 10 000 руб.\n"
        "• Срок: 8-14 дней\n\n"
        "Что входит:\n"
        "• Настройка и запуск\n"
        "• Обучение управлению\n" 
        "• Поддержка 1 месяц\n"
        "• Доработки в течение 1 недели\n\n"
        "Бесплатная консультация и демо!"
    )
    
    keyboard = [
        [InlineKeyboardButton("💬 Оставить заявку", callback_data='leave_request')],
        [InlineKeyboardButton("📞 Контакты", callback_data='contacts')],
        [InlineKeyboardButton("🤖 Посмотреть демо-боты", callback_data='demo_bots')],
        [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
    ]
    
    await query.edit_message_text(services_text, reply_markup=InlineKeyboardMarkup(keyboard))

# ========== КОНТАКТЫ ==========
async def show_contacts(query):
    await query.edit_message_text(
        "📞 Контакты\n\n"
        "Telegram: @your_username\n"
        "Телефон: +7 (XXX) XXX-XX-XX\n"
        "Email: your@email.com\n"
        "Время работы: 9:00-21:00\n\n"
        "Бесплатная консультация - ответим на все вопросы!\n"
        "Срок разработки: 8-14 дней\n"
        "Гарантия: 1 месяц\n\n"
        "Хотите узнать больше?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Оставить заявку", callback_data='leave_request')],
            [InlineKeyboardButton("🤖 Посмотреть демо-боты", callback_data='demo_bots')],
            [InlineKeyboardButton("🏠 В главное меню", callback_data='back_to_main')]
        ])
    )

# ========== СБОР ЗАЯВОК (ИСПРАВЛЕННЫЙ) ==========
async def start_leave_request(update: Update, context):
    query = update.callback_query
    
    # Очищаем предыдущие данные
    context.user_data.clear()
    
    await query.edit_message_text(
        "📝 Оставить заявку\n\n"
        "Ответьте на 4 простых вопроса для расчета стоимости:\n\n"
        "Вопрос 1/4:\nКак называется ваш бизнес?",
        reply_markup=get_cancel_keyboard()
    )
    
    return BUSINESS_NAME

async def get_business_name(update: Update, context):
    # Сохраняем ответ в user_data
    context.user_data['business_name'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Принято: {update.message.text}\n\n"
        "Вопрос 2/4:\nКакая у вас сфера? (ресторан, салон красоты, доставка...)",
        reply_markup=get_cancel_keyboard()
    )
    return BUSINESS_TYPE

async def get_business_type(update: Update, context):
    # Сохраняем ответ в user_data
    context.user_data['business_type'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Принято: {update.message.text}\n\n"
        "Вопрос 3/4:\nЧто хотите автоматизировать? (прием заказов, запись клиентов...)",
        reply_markup=get_cancel_keyboard()
    )
    return AUTOMATION_GOAL

async def get_automation_goal(update: Update, context):
    # Сохраняем ответ в user_data
    context.user_data['automation_goal'] = update.message.text
    
    await update.message.reply_text(
        f"✅ Принято: {update.message.text}\n\n"
        "Вопрос 4/4:\nВаш номер Telegram для связи?",
        reply_markup=get_cancel_keyboard()
    )
    return CONTACT_INFO

async def get_contact_info(update: Update, context):
    # Сохраняем ответ
    context.user_data['contact_info'] = update.message.text
    user_data = context.user_data

    # 🔔 Отправка админу
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=(
                "🚀 НОВАЯ ЗАЯВКА!\n"
                f"Бизнес: {user_data.get('business_name')}\n"
                f"Сфера: {user_data.get('business_type')}\n"
                f"Задача: {user_data.get('automation_goal')}\n"
                f"Контакты: {user_data.get('contact_info')}"
            )
        )
        print("✅ Оповещение админу отправлено!")
    except Exception as e:
        print(f"❌ Ошибка отправки админу: {e}")

    # Подтверждение пользователю
    await update.message.reply_text("✅ Заявка принята! Админ уведомлен.")

    context.user_data.clear()
    return ConversationHandler.END

# ========== НАВИГАЦИЯ ==========
async def back_to_main(query):
    await query.edit_message_text(
        "👋 Главное меню. Выберите опцию:",
        reply_markup=get_main_menu_keyboard()
    )

async def cancel_conversation(update: Update, context):
    query = update.callback_query
    
    await query.edit_message_text(
        '❌ Заявка отменена.',
        reply_markup=get_main_menu_keyboard()
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel_command(update: Update, context):
    await update.message.reply_text(
        '❌ Заявка отменена.',
        reply_markup=get_main_menu_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    if not BOT_TOKEN:
        print("❌ ОШИБКА: Не найден BOT_TOKEN!")
        return
    
    print("🤖 Бот запускается...")
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # ConversationHandler ДОЛЖЕН БЫТЬ ПЕРВЫМ!
        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(start_leave_request, pattern='^leave_request$')],
            states={
                BUSINESS_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_business_name)],
                BUSINESS_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_business_type)],
                AUTOMATION_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_automation_goal)],
                CONTACT_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_contact_info)],
            },
            fallbacks=[
                CallbackQueryHandler(cancel_conversation, pattern='^cancel$'),
                CommandHandler('cancel', cancel_command)
            ],
            allow_reentry=True
        )
        
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        print("✅ Бот успешно запущен!")
        print("⏹ Для остановки нажмите Ctrl+C")
        
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    main()

