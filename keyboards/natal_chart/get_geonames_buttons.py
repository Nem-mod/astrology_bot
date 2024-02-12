import geocoder
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware
from keyboards.natal_chart.callbacks import GeoNameCallback, GeoNameActions


async def get_geonames_buttons(city: str) -> InlineKeyboardMarkup or None:
    geo_res = geocoder.geonames(city, key='artem.nechaev', maxRows=5)
    keyboard_builder = InlineKeyboardBuilder()
    geo_data = geo_res.geojson["features"]
    if not geo_data:
        return None
    for geo_item in geo_data:
        geo_item_prop = geo_item["properties"]
        keyboard_builder.button(
            text=f'{geo_item_prop["address"]} -- {geo_item_prop["country"]}',
            callback_data=GeoNameCallback(
                action=GeoNameActions.choose,
                address=geo_item_prop["address"],
                lat=float(geo_item_prop["lat"]),
                lng=float(geo_item_prop["lng"])
            )
        )

    keyboard_builder.button(
        text=_("⬅️ Back"), callback_data="/cancel_get_birth_city"

    )
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()
