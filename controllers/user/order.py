import json
import pprint

from aiogram import types
from aiogram.client.session import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from data.config import config, WALLET_HEADERS
from keyboards.natal_chart.callbacks import OrderCallback


async def callback_create_order(callback_query: types.CallbackQuery, state: FSMContext, callback_data: OrderCallback):
    user_id = callback_query.from_user.id
    webhook_data = f"{user_id}_{callback_data.amount}_{str(callback_data.type.value)}"
    try:
        async with aiohttp.ClientSession(headers=WALLET_HEADERS) as session:
            url = f"https://pay.wallet.tg/wpay/store-api/v1/order"
            data = {

                "amount": {
                    "currencyCode": "USD",
                    "amount": "0.01"
                },
                "autoConversionCurrency": "USDT",
                "description": "Astro sub",
                "returnUrl": f"{config.server.url}/wallet/order",
                "failReturnUrl": f"{config.server.url}/wallet/order",
                "customData": webhook_data,
                "externalId": "XXX-YYY-ZZZ",
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
