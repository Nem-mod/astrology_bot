from aiogram import types
async def callback_start(message: types.message.Message) -> None:
    await message.answer(
        "🤖 Добро пожаловать на борт JetOffice Sales Bot.\n"
        "Тут вы можете ближе познакомиться с Jettofice и его решениями.\n"
        "Задавайте свои вопросы и вам ответит наш СПЕЦИАЛЬНО ОБУЧЕНЫЙ БОТ."
    )

