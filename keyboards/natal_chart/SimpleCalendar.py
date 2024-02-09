import calendar
from datetime import datetime, timedelta
from aiogram.types import InlineKeyboardMarkup, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from .callbacks import CalendarCallback, CalendarActions

WEEKDAYS = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]


class SimpleCalendar():
    @staticmethod
    async def start_calendar(
            left_bound: datetime = datetime.now()
    ) -> InlineKeyboardMarkup:
        day = left_bound.day
        month = left_bound.month
        year = left_bound.year
        ignore_callback = CalendarCallback(action=CalendarActions.IGNORE, year=year, month=month,
                                            day=day)

        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(
            text="<<",
            callback_data=CalendarCallback(
                day=day,
                month=month,
                year=year,
                action=CalendarActions.STEP_BACKWARD_YEAR
            )
        )

        keyboard_builder.button(
            text=f"{calendar.month_name[month]} {str(year)}",
            callback_data=ignore_callback.pack()
        )



        keyboard_builder.button(
            text=">>",
            callback_data=CalendarCallback(
                day=day,
                month=month,
                year=year,
                action=CalendarActions.STEP_FORWARD_YEAR
            )
        )
        week_builder = InlineKeyboardBuilder()

        for i in range(6):
            weekday = (left_bound + timedelta(days=i)).weekday()
            week_builder.button(
                text=WEEKDAYS[weekday],
                callback_data=ignore_callback.pack()
            )

        month_calendar = calendar.monthcalendar(year, month)
        days_builder = InlineKeyboardBuilder()
        for week in month_calendar:
            calendar_row = []
            for day in week:
                if day == 0:
                    calendar_row.append(InlineKeyboardButton(text=" ", callback_data=ignore_callback.pack()))
                    continue
                calendar_row.append(InlineKeyboardButton(
                    text=str(day),
                    callback_data=CalendarCallback(action=CalendarActions.SET_DAY, year=year, month=month,
                                                    day=day).pack()
                ))
            days_builder.row(*calendar_row)

        # for i in range(6):
        #     day_data = (left_bound + timedelta(days=i))
        #     days_builder.button(
        #         text=f"{day_data.day}",
        #         callback_data=CalendarCallback(
        #             day=day_data.day,
        #             month=day_data.month,
        #             year=day_data.year,
        #             action=CalendarActions.SET_DAY
        #         )
        #     )

        arrows_builder = InlineKeyboardBuilder()
        arrows_builder.button(
            text="<",
            callback_data=CalendarCallback(
                day=day,
                month=month,
                year=year,
                action=CalendarActions.STEP_BACKWARD_MONTH
            )
        )

        arrows_builder.button(
            text=f" ",
            callback_data=ignore_callback.pack()
        )

        arrows_builder.button(
            text=">",
            callback_data=CalendarCallback(
                day=day,
                month=month,
                year=year,
                action=CalendarActions.STEP_FORWARD_MONTH
            )
        )

        keyboard_builder.attach(week_builder)
        keyboard_builder.attach(days_builder)
        keyboard_builder.attach(arrows_builder)

        return keyboard_builder.as_markup()

    async def process_selection(self, query: CallbackQuery, data: CalendarCallback) -> tuple[bool, [datetime, None]]:
        """
        Process the callback_query. This method generates a new calendar if forward or
        backward is pressed. This method should be called inside a CallbackQueryHandler.
        :param message_id:
        :param query: callback_query, as provided by the CallbackQueryHandler
        :param data: callback_data, dictionary, set by calendar_callback
        :return: Returns a tuple (Boolean,datetime), indicating if a date is selected
                    and returning the date if so.
        """
        return_data = (False, None)
        temp_date = datetime(int(data.year), int(data.month), 1)
        # processing empty buttons, answering with no action
        if data.action == CalendarActions.IGNORE:
            await query.answer(cache_time=60)

        # user picked a day button, return date
        if data.action == CalendarActions.SET_DAY:
            # await query.message.delete_reply_markup()  # removing inline keyboard
            return_data = True, datetime(int(data.year), int(data.month), int(data.day))

        # user navigates to next slice, editing message with new calendar
        if data.action == CalendarActions.STEP_FORWARD_MONTH:
            if data.month == 12:
                date = datetime(int(data.year) + 1, 1, 1)
            else:
                date = datetime(int(data.year), int(data.month) + 1, 1)
            await query.message.edit_reply_markup(query.inline_message_id, await self.start_calendar(date))

        # user navigates to previous slice, editing message with new calendar
        if data.action == CalendarActions.STEP_BACKWARD_MONTH and temp_date < datetime.now():
            if data.month == 1:
                date = datetime(int(data.year) - 1, 12, 1)
            else:
                date = datetime(int(data.year), int(data.month) - 1, 1)
            await query.message.edit_reply_markup(query.inline_message_id, await self.start_calendar(date))

        if data.action == CalendarActions.STEP_BACKWARD_YEAR:
            prev_date = datetime(int(data.year) - 1, int(data.month), 1)
            await query.message.edit_reply_markup(query.inline_message_id,
                                                  await self.start_calendar(prev_date))
        # user navigates to next year, editing message with new calendar

        if data.action == CalendarActions.STEP_FORWARD_YEAR and temp_date < datetime.now():
            next_date = datetime(int(data.year) + 1, int(data.month), 1)
            await query.message.edit_reply_markup(query.inline_message_id,
                                                  await self.start_calendar(next_date))


        if data.action == CalendarActions.START:
            date = datetime(int(data.year), int(data.month), data.day)
            await query.message.edit_reply_markup(query.inline_message_id, await self.start_calendar(date))

        return return_data
