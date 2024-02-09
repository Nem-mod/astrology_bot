import calendar
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callbacks import TimeChooserCallback, TimeChooserActions
from aiogram.utils.i18n import gettext as _, FSMI18nMiddleware



class SimpleTimeChooser():
    @staticmethod
    async def start_time_chooser(
            hour: int, minute: int
    ) -> InlineKeyboardMarkup:
        ignore_callback = TimeChooserCallback(action=TimeChooserActions.IGNORE, hour=hour, minute=minute)

        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(
            text="↑",
            callback_data=TimeChooserCallback(
                hour=hour,
                minute=minute,
                action=TimeChooserActions.STEP_HOUR_T
            )
        )
        keyboard_builder.button(
            text="↑",
            callback_data=TimeChooserCallback(
                hour=hour,
                minute=minute,
                action=TimeChooserActions.STEP_MINUTE_T
            )
        )
        keyboard_builder.row()

        keyboard_builder.button(
            text=f"{hour}" if hour >= 10 else f"0{hour}",
            callback_data=ignore_callback
        )
        keyboard_builder.button(
            text=f"{minute}" if minute >= 10 else f"0{minute}",
            callback_data=ignore_callback
        )


        keyboard_builder.button(
            text="↓",
            callback_data=TimeChooserCallback(
                hour=hour,
                minute=minute,
                action=TimeChooserActions.STEP_HOUR_B
            )
        )
        keyboard_builder.button(
            text="↓",
            callback_data=TimeChooserCallback(
                hour=hour,
                minute=minute,
                action=TimeChooserActions.STEP_MINUTE_B
            )
        )

        keyboard_builder.adjust(2)

        add_builder = InlineKeyboardBuilder()
        add_builder.button(
            text=_("I dont know exact time"),
            callback_data=TimeChooserCallback(
                hour=hour,
                minute=minute,
                action=TimeChooserActions.CONTINUE
            )
        )
        add_builder.button(
            text=_("Confirm"),
            callback_data=TimeChooserCallback(
                hour=hour,
                minute=minute,
                action=TimeChooserActions.CONFIRM
            )
        )

        add_builder.adjust(1)
        keyboard_builder.attach(add_builder)
        return keyboard_builder.as_markup()

    async def process_selection(self, query: CallbackQuery, data: TimeChooserCallback) -> tuple[bool, [int, None], [int, None]]:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param message_id:
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a tuple (Boolean,datetime), indicating if a date is selected
                    and returning the date if so.
        """
        return_data = (False, None, None)
        hour, minute = data.hour, data.minute
        if data.action == TimeChooserActions.IGNORE:
            await query.answer(cache_time=60)

        if data.action == TimeChooserActions.CONFIRM:
            return_data = True, data.hour, data.minute


        if data.action == TimeChooserActions.CONTINUE:
            return_data = True, 12, 0

        if data.action == TimeChooserActions.STEP_HOUR_T:
            if hour == 23:
                hour = 0
            else:
                hour += 1
            await query.message.edit_reply_markup(query.inline_message_id, await self.start_time_chooser(hour=hour, minute=minute))

        if data.action == TimeChooserActions.STEP_HOUR_B:
            if hour == 0:
                hour = 23
            else:
                hour -= 1
            await query.message.edit_reply_markup(query.inline_message_id,
                                                  await self.start_time_chooser(hour=hour, minute=minute))

        if data.action == TimeChooserActions.STEP_MINUTE_T:
            if minute == 59:
                minute = 0
            else:
                minute += 1
            await query.message.edit_reply_markup(query.inline_message_id,
                                                  await self.start_time_chooser(hour=hour, minute=minute))

        if data.action == TimeChooserActions.STEP_MINUTE_B:
            if minute == 0:
                minute = 59
            else:
                minute -= 1
            await query.message.edit_reply_markup(query.inline_message_id,
                                                  await self.start_time_chooser(hour=hour, minute=minute))

        return return_data
