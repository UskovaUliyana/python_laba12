import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

TOKEN = "8559173706:AAEK2JP9XR6BJs_6naaD7dMJ7Sg4YC4lq6Q"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

user_data = {}

def to_float(s):
    s = s.replace(',', '.')
    return float(s)

def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💰 Кредитный калькулятор")],
            [KeyboardButton(text="🏦 Калькулятор вкладов")],
            [KeyboardButton(text="📅 Игра 52 недели богатства")],
            [KeyboardButton(text="🎯 Финансовая цель")],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_credit_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Аннуитетный платёж")],
            [KeyboardButton(text="📊 Дифференцированный платёж")],
            [KeyboardButton(text="🔙 Главное меню")]
        ],
        resize_keyboard=True
    )
    return keyboard

def calculate_annuity(amount, rate, months):
    monthly_rate = rate / 12 / 100
    payment = amount * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    total = payment * months
    overpayment = total - amount
    
    result = (
        f"📊 Аннуитетный платёж\n\n"
        f"Сумма кредита: {amount:,.0f} ₽\n"
        f"Ставка: {rate}% годовых\n"
        f"Срок: {months} мес.\n\n"
        f"Ежемесячный платёж: {payment:,.0f} ₽\n"
        f"Общая сумма выплат: {total:,.0f} ₽\n"
        f"Переплата: {overpayment:,.0f} ₽\n\n"
        f"💡 Плюс: платёж всегда одинаковый, легко планировать бюджет\n"
        f"💡 Минус: переплата больше, чем при дифференцированном"
    )
    return result

def calculate_differentiated(amount, rate, months):
    monthly_rate = rate / 12 / 100
    principal_payment = amount / months
    
    total = 0
    first_payment = 0
    last_payment = 0
    
    for i in range(1, months + 1):
        remaining = amount - principal_payment * (i - 1)
        interest_payment = remaining * monthly_rate
        monthly_total = principal_payment + interest_payment
        total += monthly_total
        
        if i == 1:
            first_payment = monthly_total
        if i == months:
            last_payment = monthly_total
    
    overpayment = total - amount
    
    result = (
        f"📊 Дифференцированный платёж\n\n"
        f"Сумма кредита: {amount:,.0f} ₽\n"
        f"Ставка: {rate}% годовых\n"
        f"Срок: {months} мес.\n\n"
        f"Первый платёж: {first_payment:,.0f} ₽\n"
        f"Последний платёж: {last_payment:,.0f} ₽\n"
        f"Общая сумма выплат: {total:,.0f} ₽\n"
        f"Переплата: {overpayment:,.0f} ₽\n\n"
        f"💡 Плюс: переплата меньше, чем при аннуитетном\n"
        f"💡 Минус: первые платежи выше"
    )
    return result

def calculate_deposit(amount, rate, months, capitalization=False):
    if capitalization:
        monthly_rate = rate / 12 / 100
        final_amount = amount * (1 + monthly_rate) ** months
    else:
        final_amount = amount * (1 + rate / 100 * months / 12)
    profit = final_amount - amount
    
    result = (
        f"🏦 Результаты вклада:\n\n"
        f"Сумма вклада: {amount:,.0f} ₽\n"
        f"Ставка: {rate}% годовых\n"
        f"Срок: {months} мес.\n"
        f"Капитализация: {'Да' if capitalization else 'Нет'}\n"
        f"Итоговая сумма: {final_amount:,.0f} ₽\n"
        f"Доход: {profit:,.0f} ₽"
    )
    return result

def calculate_52_weeks(step=50):
    total = 0
    schedule = []
    for week in range(1, 53):
        amount = week * step
        total += amount
        schedule.append(f"Неделя {week}: {amount:,.0f} ₽")
    
    result = (
        f"📅 Игра «52 недели богатства»\n"
        f"Шаг: {step:,.0f} ₽\n"
        f"Итого за год: {total:,.0f} ₽\n\n"
        f"📅 График накоплений:\n"
        f"{'=' * 40}\n"
    )
    result += "\n".join(schedule[:5]) + "\n...\n" + "\n".join(schedule[-5:])
    return result

@dp.message(Command("start"))
async def start_command(message: types.Message):
    text = (
        "👋 Привет! Я финансовый бот.\n\n"
        "💰 Рассчитываю кредиты (аннуитетные и дифференцированные)\n"
        "🏦 Считаю доход по вкладам\n"
        "📅 Игра «52 недели богатства»\n"
        "🎯 Помогу накопить на цель\n\n"
        "Выбери действие 👇"
    )
    await message.answer(text, reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text == "🔙 Главное меню")
async def back_to_main(message: types.Message):
    await message.answer("Выбери действие 👇", reply_markup=get_main_keyboard())
    user_data.pop(message.from_user.id, None)

@dp.message(lambda message: message.text == "❓ Помощь")
async def help_command(message: types.Message):
    text = (
        "📖 *Справка по боту*\n\n"
        "💰 *Кредитный калькулятор:*\n"
        "   • Аннуитетный: `100000 15 12`\n"
        "   • Дифференцированный: `100000 15 12`\n"
        "   • Дробные проценты можно писать через точку или запятую (например: 15,5 или 15.5)\n\n"
        "🏦 *Калькулятор вкладов:*\n"
        "   • `50000 8 6 да` (с капитализацией)\n"
        "   • `50000 8,5 6 нет` (без капитализации, проценты через запятую)\n\n"
        "📅 *Игра 52 недели:*\n"
        "   • `50` (шаг 50₽)\n\n"
        "🎯 *Финансовая цель:*\n"
        "   • `500000 24` (накопить 500к за 24 месяца)\n\n"
        "Вводи числа через пробел!"
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(lambda message: message.text == "💰 Кредитный калькулятор")
async def credit_menu(message: types.Message):
    user_data[message.from_user.id] = {'mode': 'credit'}
    await message.answer("Выбери тип платежа 👇", reply_markup=get_credit_keyboard())

@dp.message(lambda message: message.text == "📊 Аннуитетный платёж")
async def annuity_prompt(message: types.Message):
    user_data[message.from_user.id] = {'mode': 'annuity'}
    await message.answer(
        "Введи: сумму ставку срок\nПример: 100000 15 12 или 100000 15,5 12",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.text == "📊 Дифференцированный платёж")
async def differentiated_prompt(message: types.Message):
    user_data[message.from_user.id] = {'mode': 'differentiated'}
    await message.answer(
        "Введи: сумму ставку срок\nПример: 100000 15 12 или 100000 15,5 12",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.text == "🏦 Калькулятор вкладов")
async def deposit_prompt(message: types.Message):
    user_data[message.from_user.id] = {'mode': 'deposit'}
    await message.answer(
        "Введи: сумму ставку срок кап(да/нет)\nПример: 50000 8 6 да или 50000 8,5 6 да",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.text == "📅 Игра 52 недели богатства")
async def game_52_prompt(message: types.Message):
    user_data[message.from_user.id] = {'mode': 'game_52'}
    await message.answer(
        "Введи шаг (сумма за 1 неделю):\nПример: 50",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message(lambda message: message.text == "🎯 Финансовая цель")
async def goal_prompt(message: types.Message):
    user_data[message.from_user.id] = {'mode': 'goal'}
    await message.answer(
        "Введи сумму цели и срок в месяцах:\nПример: 500000 24",
        reply_markup=ReplyKeyboardRemove()
    )

@dp.message()
async def handle_calculation(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in user_data:
        await message.answer("Используй меню 👇", reply_markup=get_main_keyboard())
        return
    
    mode = user_data[user_id].get('mode')
    
    try:
        parts = message.text.strip().split()
        
        if mode == 'annuity':
            if len(parts) != 3:
                await message.answer("Нужно 3 числа: сумма ставка срок\nПример: 100000 15 12 или 100000 15,5 12")
                return
            amount = to_float(parts[0])
            rate = to_float(parts[1])
            months = int(parts[2])
            result = calculate_annuity(amount, rate, months)
            await message.answer(result, reply_markup=get_main_keyboard())
            user_data.pop(user_id)
        
        elif mode == 'differentiated':
            if len(parts) != 3:
                await message.answer("Нужно 3 числа: сумма ставка срок\nПример: 100000 15 12 или 100000 15,5 12")
                return
            amount = to_float(parts[0])
            rate = to_float(parts[1])
            months = int(parts[2])
            result = calculate_differentiated(amount, rate, months)
            await message.answer(result, reply_markup=get_main_keyboard())
            user_data.pop(user_id)
        
        elif mode == 'deposit':
            if len(parts) < 3:
                await message.answer("Нужно минимум 3 значения: сумма ставка срок\nПример: 50000 8 6 да или 50000 8,5 6 да")
                return
            amount = to_float(parts[0])
            rate = to_float(parts[1])
            months = int(parts[2])
            cap = False
            if len(parts) >= 4:
                cap = parts[3].lower() in ['да', 'yes', '1', 'true']
            result = calculate_deposit(amount, rate, months, cap)
            await message.answer(result, reply_markup=get_main_keyboard())
            user_data.pop(user_id)
        
        elif mode == 'game_52':
            step = 50
            if len(parts) >= 1:
                try:
                    step = to_float(parts[0])
                except ValueError:
                    await message.answer("Введи число.")
                    return
            result = calculate_52_weeks(step)
            await message.answer(result, reply_markup=get_main_keyboard())
            user_data.pop(user_id)
        
        elif mode == 'goal':
            if len(parts) != 2:
                await message.answer("Нужно 2 числа: сумма цели и срок")
                return
            goal = to_float(parts[0])
            months = int(parts[1])
            per_month = goal / months
            result = (
                f"🎯 Финансовая цель\n\n"
                f"Цель: {goal:,.0f} ₽\n"
                f"Срок: {months} мес.\n"
                f"Нужно откладывать: {per_month:,.0f} ₽/мес.\n\n"
                f"Начни копить уже сегодня! 💪"
            )
            await message.answer(result, reply_markup=get_main_keyboard())
            user_data.pop(user_id)
        
        else:
            await message.answer("Не понял. Выбери действие в меню.", reply_markup=get_main_keyboard())
            user_data.pop(user_id)
    
    except ValueError:
        await message.answer("Ошибка! Вводи только числа через пробел. Дробные числа можно писать через точку или запятую.\nПример: 100000 15,5 12")
    except Exception as e:
        await message.answer(f"Ошибка: {e}", reply_markup=get_main_keyboard())
        user_data.pop(user_id)

async def main():
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())