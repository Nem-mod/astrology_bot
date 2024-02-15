import json
import pprint

from aiogram import types
from aiogram.client.session import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from data.config import config, WALLET_HEADERS
from keyboards.natal_chart.callbacks import OrderCallback

import random


def generate_random_string():
    xxx = random.randint(0, 999)
    yyy = random.randint(0, 999)
    zzz = random.randint(0, 999)

    xxx_formatted = str(xxx).zfill(3)
    yyy_formatted = str(yyy).zfill(3)
    zzz_formatted = str(zzz).zfill(3)

    random_string = f"{xxx_formatted}-{yyy_formatted}-{zzz_formatted}"

    return random_string

async def callback_create_order(callback_query: types.CallbackQuery, state: FSMContext, callback_data: OrderCallback):
    user_id = callback_query.from_user.id
    webhook_data = f"{user_id}_{callback_data.amount}_{str(callback_data.type.value)}"
    externalId = generate_random_string()
    try:
        async with aiohttp.ClientSession(headers=WALLET_HEADERS) as session:
            url = f"https://pay.wallet.tg/wpay/store-api/v1/order"
            data = {
                "amount": {
                    "currencyCode": "USD",
                    "amount": "0.01" # Change IT after verification
                },
                "autoConversionCurrency": "USDT",
                "description": f"{callback_data.description}",
                "returnUrl": f"https://t.me/astrolog_ai_bot",
                "failReturnUrl": f"{config.server.url}/wallet/order",
                "customData": webhook_data,
                "externalId": externalId,
                "timeoutSeconds": 60 * 10,
                "customerTelegramUserId": user_id
            }

            data = json.dumps(data)
            async with session.post(url=url, data=data) as resp:
                response = await resp.json()
                pprint.pprint(response)

        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(
            text=_("Buy"),
            url=response["data"]["payLink"]
        )
    except Exception as err:
        raise Exception(f"Create order error: {err}")

    # TODO: add localization
    await callback_query.message.answer(
        text=_("Your order is ready. To continue press \"Buy\" button"),
        reply_markup=keyboard_builder.as_markup()
    )
