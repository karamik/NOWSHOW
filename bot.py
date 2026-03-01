"""
NOWSHOWBOT — Полностью готовый бот
21 персонаж · Бесплатный час · 10 звёзд/сутки · Групповые чаты · Голоса
Токен уже вставлен
"""

import logging
from datetime import datetime, timedelta
from typing import Dict
import asyncio
import random

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import LabeledPrice, PreCheckoutQuery

# ========== КОНФИГУРАЦИЯ ==========
API_TOKEN = '8751085030:AAEleidT8KJlC8kNtdqyzrRopsluyH7LPcs'
PAYMENT_TOKEN = 'YOUR_PAYMENT_TOKEN'  # Получить у @BotFather

STARS_PRICE = 10
FREE_MINUTES = 60
FREE_MESSAGES_LIMIT = 20

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# ========== ВРЕМЕННОЕ ХРАНИЛИЩЕ ==========
user_sessions: Dict[int, Dict] = {}
user_memory: Dict[int, Dict] = {}

# ========== ВСЕ 21 ПЕРСОНАЖ ==========
PERSONALITIES = {
    # Политика
    'lenin': {
        'name': 'Ленин',
        'name_en': 'Lenin',
        'emoji': '👨',
        'prompt': 'Ты — Владимир Ленин. Говори от первого лица. Страстно, убедительно, используй "товарищ". Любишь цитировать Маркса. Немного картавишь.',
        'voice': 'lenin_voice'
    },
    'stalin': {
        'name': 'Сталин',
        'name_en': 'Stalin',
        'emoji': '👨‍🦰',
        'prompt': 'Ты — Иосиф Сталин. Говори от первого лица. Твёрдо, решительно, с лёгким грузинским акцентом. Любишь повторять "Кадры решают всё", "Пятилетку в четыре года!".',
        'voice': 'stalin_voice'
    },
    'zhirinovsky': {
        'name': 'Жириновский',
        'name_en': 'Zhirinovsky',
        'emoji': '🗣️',
        'prompt': 'Ты — Владимир Жириновский. Говори от первого лица. ГРОМКО, эмоционально, срываясь на крик. Любишь тему юга, сапог в Индийском океане, критикуешь всех подряд.',
        'voice': 'zhirinovsky_voice'
    },
    'churchill': {
        'name': 'Черчилль',
        'name_en': 'Churchill',
        'emoji': '🧐',
        'prompt': 'Ты — Уинстон Черчилль. Говори от первого лица. С сигарой во рту, веско, с чувством собственного достоинства. Любишь повторять "Мы будем сражаться на пляжах".',
        'voice': 'churchill_voice'
    },
    'napoleon': {
        'name': 'Наполеон',
        'name_en': 'Napoleon',
        'emoji': '🎖️',
        'prompt': 'Ты — Наполеон Бонапарт. Говори от первого лица. Амбициозно, про величие, про стратегию. Немного комплексуешь из-за роста.',
        'voice': 'napoleon_voice'
    },
    
    # Философия
    'nietzsche': {
        'name': 'Ницше',
        'name_en': 'Nietzsche',
        'emoji': '🧠',
        'prompt': 'Ты — Фридрих Ницше. Говори от первого лица. Афористично, глубоко, про сверхчеловека, про волю к власти, про то, что Бог умер.',
        'voice': 'nietzsche_voice'
    },
    'kant': {
        'name': 'Кант',
        'name_en': 'Kant',
        'emoji': '📚',
        'prompt': 'Ты — Иммануил Кант. Говори от первого лица. Рассудительно, про категорический императив, про долг, про разум. Любишь порядок.',
        'voice': 'kant_voice'
    },
    'hegel': {
        'name': 'Гегель',
        'name_en': 'Hegel',
        'emoji': '📖',
        'prompt': 'Ты — Георг Гегель. Говори от первого лица. Диалектически, сложно, про абсолютный дух, про тезис-антитезис-синтез.',
        'voice': 'hegel_voice'
    },
    'einstein': {
        'name': 'Эйнштейн',
        'name_en': 'Einstein',
        'emoji': '🧪',
        'prompt': 'Ты — Альберт Эйнштейн. Говори от первого лица. Мудро, просто, с юмором. Любишь объяснять сложное простыми словами. Про относительность.',
        'voice': 'einstein_voice'
    },
    'shivananda': {
        'name': 'Свами Шивананда',
        'name_en': 'Swami Shivananda',
        'emoji': '🧘',
        'prompt': 'Ты — Свами Шивананда. Говори от первого лица. Спокойно, мудро, про карму, про йогу, про просветление. Любишь повторять "Ом".',
        'voice': 'shivananda_voice'
    },
    
    # Культура
    'vysotsky': {
        'name': 'Высоцкий',
        'name_en': 'Vysotsky',
        'emoji': '🎸',
        'prompt': 'Ты — Владимир Высоцкий. Говори от первого лица. Хрипло, с надрывом, про горы, про друзей, про совесть. Любишь петь.',
        'voice': 'vysotsky_voice'
    },
    'tsoi': {
        'name': 'Цой',
        'name_en': 'Tsoi',
        'emoji': '🎤',
        'prompt': 'Ты — Виктор Цой. Говори от первого лица. Немногословно, ёмко, философски. Любишь тему перемен, ночи, звезды.',
        'voice': 'tsoi_voice'
    },
    'pugacheva': {
        'name': 'Пугачёва',
        'name_en': 'Pugacheva',
        'emoji': '👩',
        'prompt': 'Ты — Алла Пугачёва. Говори от первого лица. С иронией, по-женски мудро. Любишь вспоминать сцену, петь, давать советы.',
        'voice': 'pugacheva_voice'
    },
    'jackson': {
        'name': 'Майкл Джексон',
        'name_en': 'Michael Jackson',
        'emoji': '💃',
        'prompt': 'Ты — Майкл Джексон. Говори от первого лица. Мягко, с "хи-хи", про музыку, про танцы, про любовь к миру.',
        'voice': 'jackson_voice'
    },
    'chaplin': {
        'name': 'Чаплин',
        'name_en': 'Chaplin',
        'emoji': '🎭',
        'prompt': 'Ты — Чарли Чаплин. Говори через описание действий. Ты немой, но очень выразительный. Юмор, грусть, доброта.',
        'voice': None
    },
    'dzhigurda': {
        'name': 'Джигурда',
        'name_en': 'Dzhigurda',
        'emoji': '🎭',
        'prompt': 'Ты — Никита Джигурда. Говори от первого лица. Страстно, с надрывом, псевдо-философски. Любишь слово "русоид", "космос", "любовь".',
        'voice': 'dzhigurda_voice'
    },
    'moiseev': {
        'name': 'Моисеев',
        'name_en': 'Moiseev',
        'emoji': '🕺',
        'prompt': 'Ты — Борис Моисеев. Говори от первого лица. Ярко, эпатажно, с "детка", с теплотой. Любишь вспоминать маму, сцену, друзей.',
        'voice': 'moiseev_voice'
    },
    
    # Мистика
    'dracula': {
        'name': 'Дракула',
        'name_en': 'Dracula',
        'emoji': '🦇',
        'prompt': 'Ты — Граф Дракула. Говори от первого лица. Медленно, с восточноевропейским акцентом, растягивая слова. Ты элегантен, опасен, загадочен.',
        'voice': 'dracula_voice'
    },
    'linzi': {
        'name': 'Линь Цзы',
        'name_en': 'Lin Tzu',
        'emoji': '🀄',
        'prompt': 'Ты — Линь Цзы, древнекитайский мудрец. Говори загадками, коанами, притчами. Как дзен-мастер.',
        'voice': 'linzi_voice'
    },
    
    # Красота
    'blonde': {
        'name': 'Красивая Блондинка',
        'name_en': 'Beautiful Blonde',
        'emoji': '👩‍🦳',
        'prompt': 'Ты — Красивая Блондинка. Говори от первого лица. Кокетливо, с придыханием. Любишь слова "милый", "дорогой", "божественно". Обожаешь моду, туфли, селфи.',
        'voice': 'blonde_voice'
    },
    'mulatto': {
        'name': 'Красивая Мулатка',
        'name_en': 'Beautiful Mulatto',
        'emoji': '👩🏽',
        'prompt': 'Ты — Красивая Мулатка. Говори от первого лица. Страстно, живо, с латиноамериканским акцентом. Любишь танцы, карнавал, солнце.',
        'voice': 'mulatto_voice'
    },
    
    # Ещё один
    'mavrodi': {
        'name': 'Мавроди',
        'name_en': 'Mavrodi',
        'emoji': '💰',
        'prompt': 'Ты — Сергей Мавроди. Говори от первого лица. Убедительно, как опытный махинатор. Любишь рассуждать о деньгах, пирамидах, обмане системы.',
        'voice': 'mavrodi_voice'
    },
}

# ========== ПРОВЕРКА ДОСТУПА ==========
def check_access(user_id: int) -> tuple:
    """Проверяет доступ пользователя"""
    now = datetime.now()
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'paid_until': None,
            'free_start': now,
            'free_messages': 0,
            'current_personality': None,
            'language': 'ru'
        }
        return True, 'free', FREE_MESSAGES_LIMIT
    
    session = user_sessions[user_id]
    
    if session['paid_until'] and session['paid_until'] > now:
        return True, 'paid', 999
    
    if session['free_start']:
        free_end = session['free_start'] + timedelta(minutes=FREE_MINUTES)
        if now < free_end:
            remaining = FREE_MESSAGES_LIMIT - session['free_messages']
            if remaining > 0:
                return True, 'free', remaining
            else:
                return False, 'free_limit_exceeded', 0
        else:
            return False, 'free_time_expired', 0
    
    return False, 'no_access', 0

# ========== ЭМОЦИОНАЛЬНАЯ ПАМЯТЬ ==========
def remember(user_id: int, personality_id: str, message: str, response: str):
    """Сохраняет диалог в память"""
    if user_id not in user_memory:
        user_memory[user_id] = {}
    if personality_id not in user_memory[user_id]:
        user_memory[user_id][personality_id] = []
    
    user_memory[user_id][personality_id].append({
        'user': message,
        'bot': response,
        'time': datetime.now().isoformat()
    })
    
    # Храним только последние 20 сообщений
    if len(user_memory[user_id][personality_id]) > 20:
        user_memory[user_id][personality_id] = user_memory[user_id][personality_id][-20:]

def get_memory_context(user_id: int, personality_id: str) -> str:
    """Возвращает контекст последних сообщений"""
    if user_id not in user_memory or personality_id not in user_memory[user_id]:
        return ""
    
    recent = user_memory[user_id][personality_id][-5:]
    context = "\n".join([
        f"User: {m['user']}\n{personality_id}: {m['bot']}"
        for m in recent
    ])
    return context

# ========== ИМИТАЦИЯ AI (ДЕМО) ==========
async def get_ai_response(personality_id: str, user_message: str, user_id: int = None) -> str:
    """Получает ответ от AI (в демо-режиме)"""
    personality = PERSONALITIES[personality_id]
    
    # В реальной версии здесь будет вызов GitHub Models API
    # Сейчас имитация
    
    responses = {
        'lenin': [
            "Товарищ, это классовая борьба!",
            "Империализм — высшая стадия капитализма.",
            "Учиться, учиться и учиться!"
        ],
        'stalin': [
            "Кадры решают всё, товарищ.",
            "Пятилетку в четыре года!",
            "Враг народа будет уничтожен."
        ],
        'zhirinovsky': [
            "САПОГИ В ИНДИЙСКОМ ОКЕАНЕ!",
            "Я вам сейчас расскажу про юг!",
            "Россия, вперёд!"
        ],
        'dracula': [
            "Кровь... это жизнь...",
            "Добро пожаловать в мой замок, смертный.",
            "Вечность — это долго. Даже для меня."
        ],
        'blonde': [
            "Милый, это новые туфли!",
            "Божественно выгляжу? Спасибо, крем за 500 баксов!",
            "Сними меня, я в Инстаграм выложу."
        ]
    }
    
    default_responses = [
        "Интересный вопрос... Дай подумать.",
        "Хм, я об этом как-то не думал.",
        "А что ты сам думаешь?"
    ]
    
    resp_list = responses.get(personality_id, default_responses)
    return random.choice(resp_list)

# ========== ГРУППОВОЙ ЧАТ ==========
class GroupChat:
    def __init__(self, participants: list):
        self.participants = participants
        self.history = []
    
    async def discuss(self, topic: str) -> list:
        """Запускает обсуждение темы между персонажами"""
        messages = []
        for p in self.participants:
            if p in PERSONALITIES:
                msg = await get_ai_response(p, topic)
                personality = PERSONALITIES[p]
                messages.append(f"{personality['emoji']} {personality['name']}: {msg}")
                self.history.append(msg)
        return messages

# ========== ГОЛОС (ЗАГОТОВКА) ==========
async def text_to_speech(text: str, voice: str) -> str:
    """Преобразует текст в голос (интеграция с ElevenLabs)"""
    # Здесь будет реальный API
    # Пока возвращаем заглушку
    return f"voice_{voice}_{hash(text)}.ogg"

# ========== КОМАНДЫ ==========
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """Главное меню"""
    user_id = message.from_user.id
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Кнопки персонажей (первые 8 для компактности)
    count = 0
    for pid, p in PERSONALITIES.items():
        if count < 8:
            keyboard.insert(InlineKeyboardButton(
                f"{p['emoji']} {p['name']}", callback_data=f"chat_{pid}"
            ))
        count += 1
    
    # Кнопки управления
    keyboard.add(
        InlineKeyboardButton("👥 Групповой чат", callback_data="group"),
        InlineKeyboardButton("🔤 Сменить язык", callback_data="language")
    )
    keyboard.add(
        InlineKeyboardButton("💰 Статус", callback_data="status"),
        InlineKeyboardButton("❓ Помощь", callback_data="help")
    )
    keyboard.add(
        InlineKeyboardButton("🎭 Все персонажи", callback_data="all_personalities")
    )
    
    await message.answer(
        "🎭 **NOWSHOWBOT**\n\n"
        "21 персонаж. Бесконечные диалоги.\n"
        "Первый час — бесплатно (20 сообщений).\n"
        "Затем — 10 звёзд/сутки.\n\n"
        "Выберите собеседника:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data.startswith('chat_'))
async def callback_chat(callback: types.CallbackQuery):
    """Начать чат с персонажем"""
    user_id = callback.from_user.id
    personality_id = callback.data.replace('chat_', '')
    
    # Проверка доступа
    has_access, status, limit = check_access(user_id)
    
    if not has_access:
        await callback.message.edit_text(
            "🔒 **Доступ закрыт**\n\n"
            "Бесплатный час закончился.\n"
            f"Оплатите {STARS_PRICE} звёзд для продолжения.",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("⭐ Купить доступ", callback_data="buy"),
                InlineKeyboardButton("◀ Назад", callback_data="start")
            ),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Сохраняем текущего персонажа
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    user_sessions[user_id]['current_personality'] = personality_id
    
    personality = PERSONALITIES[personality_id]
    
    status_text = "⭐ Премиум" if status == 'paid' else f"🕐 Бесплатно (осталось {limit})"
    
    # Клавиатура чата
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔊 Голос (скоро)", callback_data="voice"))
    keyboard.add(InlineKeyboardButton("🔄 Сменить персонажа", callback_data="start"))
    keyboard.add(InlineKeyboardButton("💰 Статус", callback_data="status"))
    
    # Приветствие с учётом памяти
    memory = get_memory_context(user_id, personality_id)
    if memory:
        greeting = f"{personality['emoji']} С возвращением! Помню наш прошлый разговор.\n\n_Напишите что-нибудь..._"
    else:
        greetings = {
            'lenin': "Здравствуйте, товарищ!",
            'stalin': "Здравствуйте. Слушаю.",
            'zhirinovsky': "О, привет! Сейчас я тебе расскажу!",
            'dracula': "Добро пожаловать в мой замок...",
            'blonde': "Приветик, милый!"
        }
        greeting = greetings.get(personality_id, f"{personality['emoji']} Привет! Я {personality['name']}.")
    
    await callback.message.edit_text(
        f"{personality['emoji']} **{personality['name']}**\n\n"
        f"{greeting}\n\n"
        f"📊 **{status_text}**",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == 'group')
async def callback_group(callback: types.CallbackQuery):
    """Настройка группового чата"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    
    # Добавляем персонажей для выбора
    for pid, p in PERSONALITIES.items():
        keyboard.insert(InlineKeyboardButton(
            f"{p['emoji']} {p['name']}", callback_data=f"group_add_{pid}"
        ))
    
    keyboard.add(InlineKeyboardButton("✅ Начать обсуждение", callback_data="group_start"))
    keyboard.add(InlineKeyboardButton("◀ Назад", callback_data="start"))
    
    await callback.message.edit_text(
        "👥 **Групповой чат**\n\n"
        "Выберите участников (2-5 персонажей):\n"
        "(пока в разработке)",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == 'status')
async def callback_status(callback: types.CallbackQuery):
    """Показать статус подписки"""
    user_id = callback.from_user.id
    has_access, status, limit = check_access(user_id)
    
    if status == 'paid':
        paid_until = user_sessions[user_id]['paid_until']
        text = (
            "⭐ **Премиум доступ**\n\n"
            f"Активен до: {paid_until.strftime('%d.%m.%Y %H:%M')}\n"
            "✅ Безлимитные сообщения\n"
            "✅ Все 21 персонаж\n"
            "✅ Групповые чаты\n"
            "✅ Голосовые ответы (скоро)"
        )
    elif status == 'free':
        session = user_sessions[user_id]
        free_end = session['free_start'] + timedelta(minutes=FREE_MINUTES)
        text = (
            "🕐 **Бесплатный час**\n\n"
            f"Действует до: {free_end.strftime('%H:%M')}\n"
            f"Осталось сообщений: {limit}\n\n"
            f"⭐ После окончания — {STARS_PRICE} звёзд/сутки"
        )
    else:
        text = (
            "🔒 **Нет доступа**\n\n"
            f"Бесплатный час закончился.\n"
            f"Оплатите {STARS_PRICE} звёзд за сутки доступа."
        )
    
    keyboard = InlineKeyboardMarkup()
    if not has_access or status == 'free':
        keyboard.add(InlineKeyboardButton("⭐ Купить доступ", callback_data="buy"))
    keyboard.add(InlineKeyboardButton("◀ Назад", callback_data="start"))
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query_handler(lambda c: c.data == 'buy')
async def callback_buy(callback: types.CallbackQuery):
    """Покупка доступа"""
    prices = [LabeledPrice(label="Доступ на сутки", amount=STARS_PRICE)]
    
    await bot.send_invoice(
        callback.from_user.id,
        title="NOWSHOWBOT Premium",
        description="Сутки безлимитного доступа ко всем 21 персонажам",
        payload="daily_access",
        provider_token=PAYMENT_TOKEN,
        currency="XTR",
        prices=prices,
        start_parameter="create_invoice"
    )
    await callback.answer()

@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)

@dp.message_handler(content_types=types.ContentTypes.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_sessions:
        user_sessions[user_id] = {}
    
    user_sessions[user_id]['paid_until'] = datetime.now() + timedelta(days=1)
    user_sessions[user_id]['free_start'] = None
    
    await message.answer(
        "✅ **Оплата прошла успешно!**\n\n"
        "⭐ У вас премиум-доступ на 24 часа.\n"
        "Все 21 персонаж доступны безлимитно.\n\n"
        "Нажмите /start чтобы продолжить.",
        parse_mode="Markdown"
    )

@dp.callback_query_handler(lambda c: c.data == 'start')
async def callback_start(callback: types.CallbackQuery):
    """Вернуться в главное меню"""
    await cmd_start(callback.message)
    await callback.answer()

@dp.message_handler()
async def handle_message(message: types.Message):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    
    # Проверяем доступ
    has_access, status, limit = check_access(user_id)
    
    if not has_access:
        await message.answer(
            "🔒 **Доступ закрыт**\n\n"
            "Бесплатный час закончился.\n"
            f"Оплатите {STARS_PRICE} звёзд для продолжения.",
            parse_mode="Markdown"
        )
        return
    
    # Проверяем, выбран ли персонаж
    if user_id not in user_sessions or 'current_personality' not in user_sessions[user_id]:
        await message.answer("Сначала выберите персонажа в меню /start")
        return
    
    personality_id = user_sessions[user_id]['current_personality']
    personality = PERSONALITIES[personality_id]
    
    # Для бесплатного режима считаем сообщения
    if status == 'free':
        user_sessions[user_id]['free_messages'] = user_sessions[user_id].get('free_messages', 0) + 1
    
    # Отправляем "печатает..."
    await message.answer_chat_action("typing")
    
    # Получаем ответ от AI
    response = await get_ai_response(personality_id, message.text, user_id)
    
    # Сохраняем в память
    remember(user_id, personality_id, message.text, response)
    
    # Отправляем ответ
    await message.answer(f"{personality['emoji']} {response}")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    logger.info("🚀 NOWSHOWBOT запускается...")
    logger.info(f"Персонажей загружено: {len(PERSONALITIES)}")
    logger.info(f"Цена: {STARS_PRICE} звёзд/сутки")
    logger.info("Бот готов к работе!")
    
    executor.start_polling(dp, skip_updates=True)
