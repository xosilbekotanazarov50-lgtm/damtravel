from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.language import KEYBOARD_BUTTONS, ADMIN_MESSAGES


def get_admin_main_keyboard(lang: str = 'ru') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['pending'], callback_data="admin_pending")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['waiting'], callback_data="admin_waiting")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['history'], callback_data="admin_history")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['packages'], callback_data="admin_packages")],
        ]
    )


def get_pending_orders_keyboard(orders: list, lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    for order in orders:
        buttons.append(
            [InlineKeyboardButton(text=order["name"], callback_data=f"order_{order['id']}")]
        )
    buttons.append([InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_order_view_keyboard(order_id: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['call_client'], callback_data=f"call_{order_id}")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_pending")],
        ]
    )


def get_confirm_call_keyboard(order_id: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['yes'], callback_data=f"confirm_yes_{order_id}")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['no'], callback_data=f"confirm_no_{order_id}")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['wait'], callback_data=f"confirm_wait_{order_id}")],
        ]
    )


def get_history_keyboard(orders: list, lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    for order in orders:
        status_icon = "✅" if order["status"] == "accepted" else "❌"
        buttons.append(
            [InlineKeyboardButton(text=f"{order['name']} {status_icon}", callback_data=f"order_{order['id']}")]
        )
    buttons.append([InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_history_order_keyboard(order_id: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['delete'], callback_data=f"delete_{order_id}")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_history")],
        ]
    )


def get_packages_keyboard(packages: list, lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    for pkg in packages:
        buttons.append(
            [InlineKeyboardButton(text=f"📦 {pkg['name']}", callback_data=f"pkg_manage_{pkg['id']}")]
        )
    buttons.append([InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['add_package'], callback_data="pkg_add")])
    buttons.append([InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_package_manage_keyboard(package_id: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['delete'], callback_data=f"pkg_delete_{package_id}")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_packages")],
        ]
    )


def get_waiting_orders_keyboard(orders: list, lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    for order in orders:
        buttons.append(
            [InlineKeyboardButton(text=order["name"], callback_data=f"waiting_{order['id']}")]
        )
    buttons.append([InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_waiting_order_keyboard(order_id: int, lang: str = 'ru') -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['yes'], callback_data=f"confirm_yes_{order_id}")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['no'], callback_data=f"confirm_no_{order_id}")],
            [InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_waiting")],
        ]
    )


def get_pagination_keyboard(page: int, total_pages: int, callback_prefix: str, lang: str = 'ru') -> InlineKeyboardMarkup:
    buttons = []
    nav_row = []
    btn_prev = KEYBOARD_BUTTONS[lang]['back'] if lang == 'ru' else ADMIN_MESSAGES[lang]['btn_prev']
    btn_next = ADMIN_MESSAGES[lang]['btn_next']
    
    if page > 1:
        nav_row.append(InlineKeyboardButton(text=btn_prev, callback_data=f"{callback_prefix}_page_{page - 1}"))
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text=btn_next, callback_data=f"{callback_prefix}_page_{page + 1}"))
    if nav_row:
        buttons.append(nav_row)
    buttons.append([InlineKeyboardButton(text=KEYBOARD_BUTTONS[lang]['back'], callback_data="admin_main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
