import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot token
TOKEN = "8097605944:AAHwNjXwWQbptOXlDB8FMjM5d6NUv1KGr1M"
ADMIN_ID = 123456789  # O'zingizning Telegram ID raqamingizni kiriting

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# 200 ta savol ro‘yxati
top_questions = [
    {"savol": "O‘zbekiston poytaxti qaysi shahar?", "javob": "Toshkent", "variantlar": ["Samarqand", "Buxoro", "Toshkent", "Andijon"]},
    {"savol": "Yerning sun’iy yo‘ldoshi nima?", "javob": "Oy", "variantlar": ["Mars", "Oy", "Yupiter", "Venera"]},
    {"savol": "Eng katta okean qaysi?", "javob": "Tinch okeani", "variantlar": ["Atlantika okeani", "Hind okeani", "Tinch okeani", "Shimoliy muz okeani"]},
    # {"savol": "Qaysi sport turida "ace" termini ishlatiladi?", "javob": "Tennis", "variantlar": ["Boks", "Basketbol", "Tennis", "Shaxmat"]}
    
]

questions = random.sample(top_questions, len(top_questions))

players = {}

@dp.message_handler(commands=['start'])
async def start_game(message: types.Message):
    chat_id = message.chat.id
    players[chat_id] = {"score": 0, "wrong": 0, "current_question": 0}
    await message.answer("🎮 <b>Aqilni Sinov o‘yini boshlandi!</b>\n\n❗ Istalgan vaqtda /stop buyrug‘ini bosib o‘yinni to‘xtatishingiz mumkin.", parse_mode="HTML")
    await ask_question(message)

async def ask_question(message):
    chat_id = message.chat.id
    player = players.get(chat_id)
    
    if player and player["current_question"] < len(questions):
        question_data = questions[player["current_question"]]
        savol = question_data["savol"]
        variantlar = question_data["variantlar"]
        
        keyboard = InlineKeyboardMarkup()
        for variant in variantlar:
            keyboard.add(InlineKeyboardButton(variant, callback_data=variant))
        
        await message.answer(f"❓ <b>{savol}</b>", parse_mode="HTML", reply_markup=keyboard)
    else:
        await show_results(message)

@dp.callback_query_handler(lambda call: True)
async def check_answer(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    player = players.get(chat_id)
    
    if player:
        current_question = player["current_question"]
        correct_answer = questions[current_question]["javob"]
        
        if call.data == correct_answer:
            player["score"] += 1
            response_text = "✅ <b>To‘g‘ri javob!</b> 🎉"
        else:
            player["wrong"] += 1
            response_text = f"❌ <b>Noto‘g‘ri!</b> ✅ To‘g‘ri javob: <b>{correct_answer}</b>"
        
        player["current_question"] += 1
        await call.message.edit_text(response_text, parse_mode="HTML")
        await ask_question(call.message)

@dp.message_handler(commands=['stop'])
async def stop_game(message: types.Message):
    await message.answer("🛑 O‘yin to‘xtatildi!", parse_mode="HTML")
    await show_results(message)

async def show_results(message):
    chat_id = message.chat.id
    player = players.pop(chat_id, None)
    if player:
        total_correct = player["score"]
        total_wrong = player["wrong"]
        result_text = f"🏆 <b>O‘yin tugadi!</b>\n✅ To‘g‘ri javoblar: {total_correct}\n❌ Noto‘g‘ri javoblar: {total_wrong}"
        await message.answer(result_text, parse_mode="HTML")
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🔄 Qayta o‘ynash", callback_data="restart"))
    keyboard.add(InlineKeyboardButton("🌐 Telegram kanalimiz", url="https://t.me/webstormers"))
    await message.answer("🔄 O‘yinni qayta boshlash uchun tugmani bosing!", reply_markup=keyboard)

@dp.callback_query_handler(lambda call: call.data == "restart")
async def restart_game(call: types.CallbackQuery):
    chat_id = call.message.chat.id
    players.pop(chat_id, None)
    await start_game(call.message)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
