from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot.language import KEYBOARD_BUTTONS


def get_language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS['ru']['lang_ru'], callback_data="lang_ru")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS['ru']['lang_uz'], callback_data="lang_uz")],
        ]
    )


def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS['ru']['start'], callback_data="start_order")],
        ]
    )


def get_start_keyboard_uz() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS['uz']['start'], callback_data="start_order")],
        ]
    )


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=KEYBOARD_BUTTONS['uz']['contact'], request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_packages_keyboard(packages: list, lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for pkg in packages:
        row.append(InlineKeyboardButton(text=pkg['name'], callback_data=f"pkg_{pkg['id']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    btn_text = KEYBOARD_BUTTONS[lang]['write_address']
    buttons.append([InlineKeyboardButton(text=btn_text, callback_data="pkg_custom")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_people_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i in range(1, 11):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"people_{i}"))
        if len(row) == 5:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    btn_text = KEYBOARD_BUTTONS[lang]['custom_people']
    buttons.append([InlineKeyboardButton(text=btn_text, callback_data="people_custom")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_time_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for i in range(1, 8):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"time_{i}"))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    btn_text = KEYBOARD_BUTTONS[lang]['custom_time']
    buttons.append([InlineKeyboardButton(text=btn_text, callback_data="time_custom")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lang_settings_keyboard(current_lang: str) -> InlineKeyboardMarkup:
    ru_text = KEYBOARD_BUTTONS['ru']['lang_ru']
    uz_text = KEYBOARD_BUTTONS['ru']['lang_uz']
    
    if current_lang == 'ru':
        ru_text = "✅ " + ru_text
    else:
        uz_text = "✅ " + uz_text
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=ru_text, callback_data="set_lang_ru")],
            [InlineKeyboardButton(text=uz_text, callback_data="set_lang_uz")],
        ]
    )
