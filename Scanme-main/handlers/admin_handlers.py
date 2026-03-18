from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from bot import ADMIN_IDS, CHANNEL_ID
from bot.language import ADMIN_MESSAGES, CHANNEL_MESSAGES, KEYBOARD_BUTTONS
from keyboards.admin_keyboards import (
    get_admin_main_keyboard,
    get_pending_orders_keyboard,
    get_order_view_keyboard,
    get_confirm_call_keyboard,
    get_history_keyboard,
    get_history_order_keyboard,
    get_packages_keyboard,
    get_package_manage_keyboard,
    get_waiting_orders_keyboard,
    get_waiting_order_keyboard,
    get_pagination_keyboard,
)
from states.order_states import AdminCallState
from database import (
    get_order_by_id, 
    get_order_history,
    update_order_status, 
    delete_order,
    get_orders_by_status,
    get_orders_count_by_status,
    add_package,
    get_packages,
    delete_package,
)

admin_router = Router()

ITEMS_PER_PAGE = 10


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def get_admin_lang(user_id: int) -> str:
    # For now, admin panel uses Russian by default
    # Can be extended to save admin language preference
    return 'ru'


@admin_router.message(F.text == "/admin")
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        lang = get_admin_lang(message.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await message.answer(texts['no_access'])
        return

    lang = get_admin_lang(message.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    await message.answer(
        texts['admin_panel'],
        reply_markup=get_admin_main_keyboard(lang),
    )


@admin_router.callback_query(F.data == "admin_main")
async def admin_main(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    await callback.message.edit_text(
        texts['admin_panel'], 
        reply_markup=get_admin_main_keyboard(lang)
    )


@admin_router.callback_query(F.data == "admin_pending")
async def admin_pending(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    orders = get_orders_by_status('pending', limit=ITEMS_PER_PAGE, offset=0)
    total = get_orders_count_by_status('pending')
    total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total > 0 else 1

    if not orders:
        await callback.answer(texts['no_pending'], show_alert=True)
        return

    page_info = texts['page_info'].format(current=1, total=total_pages, total_count=total)
    await callback.message.edit_text(
        f"{texts['btn_pending']}\n{page_info}",
        reply_markup=get_pending_orders_keyboard(orders, lang),
    )


@admin_router.callback_query(F.data.startswith("order_"))
async def view_order(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    order_id = int(callback.data.split("_")[1])
    order = get_order_by_id(order_id)

    if not order:
        await callback.answer(texts['order_not_found'], show_alert=True)
        return

    text = f"""{texts['name']}: {order['name']}
{texts['phone']}: `{order['phone']}`
{texts['destination']}: {order['destination']}
{texts['people_count']}: {order['people_count']}
{texts['time']}: {order['time']}"""

    if order["status"] == "pending":
        keyboard = get_order_view_keyboard(order_id, lang)
    elif order["status"] == "pending_review":
        text += f"\n\n{texts['status_pending_review_display']}"
        keyboard = get_waiting_order_keyboard(order_id, lang)
    else:
        status_icon = "✅" if order["status"] == "accepted" else "❌"
        text += f"\n\nСтатус: {status_icon}"
        keyboard = get_history_order_keyboard(order_id, lang)

    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@admin_router.callback_query(F.data.startswith("call_"))
async def call_client(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    order_id = int(callback.data.split("_")[1])
    await state.update_data(order_id=order_id)
    await callback.message.edit_text(
        texts['call_question'],
        reply_markup=get_confirm_call_keyboard(order_id, lang),
    )
    await state.set_state(AdminCallState.confirming)


@admin_router.callback_query(F.data.startswith("confirm_yes_"))
async def confirm_yes(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    order_id = int(callback.data.split("_")[2])
    await process_order_result(callback, state, order_id, "accepted")


@admin_router.callback_query(F.data.startswith("confirm_no_"))
async def confirm_no(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    order_id = int(callback.data.split("_")[2])
    await process_order_result(callback, state, order_id, "rejected")


@admin_router.callback_query(F.data.startswith("confirm_wait_"))
async def confirm_wait(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    order_id = int(callback.data.split("_")[2])
    await process_order_result(callback, state, order_id, "pending_review")


async def process_order_result(callback: types.CallbackQuery, state: FSMContext, order_id: int, status: str):
    from bot import bot

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    update_order_status(order_id, status)
    await state.clear()

    order = get_order_by_id(order_id)

    if order and order.get("channel_message_id"):
        try:
            channel_chat_id = int(CHANNEL_ID)
            order_lang = order.get('lang', 'ru')
            channel_texts = CHANNEL_MESSAGES.get(order_lang, CHANNEL_MESSAGES['ru'])
            
            if order_lang == 'uz':
                text = f"""{channel_texts['new_order']}

{channel_texts['name']}: {order['name']}
{channel_texts['phone']}: {order['phone']}
{channel_texts['destination']}: {order['destination']}
{channel_texts['people_count']}: {order['people_count']}
{channel_texts['time']}: {order['time']}

{channel_texts[f'status_{status}']}"""
            else:
                text = f"""{channel_texts['new_order']}

{channel_texts['name']}: {order['name']}
{channel_texts['phone']}: {order['phone']}
{channel_texts['destination']}: {order['destination']}
{channel_texts['people_count']}: {order['people_count']}
{channel_texts['time']}: {order['time']}

{channel_texts[f'status_{status}']}"""

            await bot.edit_message_text(
                chat_id=channel_chat_id,
                message_id=order["channel_message_id"],
                text=text,
            )
            print(f"Channel message updated with status: {status}")
        except Exception as e:
            print(f"Error updating channel message: {e}")

    status_text = texts[f'status_{status}']
    await callback.message.edit_text(
        texts['order_marked'].format(order_id=order_id, status=status_text),
        reply_markup=get_admin_main_keyboard(lang),
    )


@admin_router.callback_query(F.data == "admin_history")
async def admin_history(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    orders = get_order_history()

    if not orders:
        await callback.answer(texts['no_history'], show_alert=True)
        return

    await callback.message.edit_text(
        texts['btn_history'],
        reply_markup=get_history_keyboard(orders, lang),
    )


@admin_router.callback_query(F.data.startswith("delete_"))
async def delete_order_handler(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет доступа.", show_alert=True)
        return

    order_id = int(callback.data.split("_")[1])
    delete_order(order_id)
    
    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]

    await callback.message.edit_text(
        texts['order_deleted'].format(order_id=order_id),
        reply_markup=get_admin_main_keyboard(lang),
    )


@admin_router.callback_query(F.data == "admin_waiting")
async def admin_waiting(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    orders = get_orders_by_status('pending_review', limit=ITEMS_PER_PAGE, offset=0)
    total = get_orders_count_by_status('pending_review')
    total_pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE if total > 0 else 1

    if not orders:
        await callback.answer(texts['no_waiting'], show_alert=True)
        return

    page_info = texts['page_info'].format(current=1, total=total_pages, total_count=total)
    await callback.message.edit_text(
        f"{texts['btn_waiting']}\n{page_info}",
        reply_markup=get_waiting_orders_keyboard(orders, lang),
    )


@admin_router.callback_query(F.data.startswith("waiting_"))
async def view_waiting_order(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    order_id = int(callback.data.split("_")[1])
    order = get_order_by_id(order_id)

    if not order:
        await callback.answer(texts['order_not_found'], show_alert=True)
        return

    text = f"""{texts['name']}: {order['name']}
{texts['phone']}: `{order['phone']}`
{texts['destination']}: {order['destination']}
{texts['people_count']}: {order['people_count']}
{texts['time']}: {order['time']}

{texts['status_pending_review_display']}"""

    await callback.message.edit_text(
        text,
        reply_markup=get_waiting_order_keyboard(order_id, lang),
        parse_mode="Markdown",
    )


@admin_router.callback_query(F.data == "admin_packages")
async def admin_packages(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    packages = get_packages()

    if not packages:
        await callback.message.edit_text(
            texts['packages_empty'],
            reply_markup=get_packages_keyboard([], lang),
        )
        return

    await callback.message.edit_text(
        texts['packages_title'],
        reply_markup=get_packages_keyboard(packages, lang),
    )


@admin_router.callback_query(F.data == "pkg_add")
async def pkg_add_prompt(callback: types.CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    await state.set_state(AdminCallState.confirming)
    await callback.message.edit_text(
        texts['pkg_enter_name'],
        reply_markup=get_admin_main_keyboard(lang),
    )


@admin_router.callback_query(F.data.startswith("pkg_manage_"))
async def pkg_manage(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    
    pkg_id = int(callback.data.split("_")[2])
    packages = get_packages()
    pkg = next((p for p in packages if p['id'] == pkg_id), None)

    if not pkg:
        await callback.answer("Пакет не найден.", show_alert=True)
        return

    await callback.message.edit_text(
        f"📦 {pkg['name']}",
        reply_markup=get_package_manage_keyboard(pkg_id, lang),
    )


@admin_router.callback_query(F.data.startswith("pkg_delete_"))
async def pkg_delete(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        lang = get_admin_lang(callback.from_user.id)
        texts = ADMIN_MESSAGES[lang]
        await callback.answer(texts['no_access_alert'], show_alert=True)
        return

    lang = get_admin_lang(callback.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    pkg_id = int(callback.data.split("_")[2])
    delete_package(pkg_id)

    packages = get_packages()
    if packages:
        await callback.message.edit_text(
            texts['pkg_deleted'],
            reply_markup=get_packages_keyboard(packages, lang),
        )
    else:
        await callback.message.edit_text(
            texts['pkg_deleted_empty'],
            reply_markup=get_admin_main_keyboard(lang),
        )


@admin_router.message(AdminCallState.confirming)
async def add_package_name(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    lang = get_admin_lang(message.from_user.id)
    texts = ADMIN_MESSAGES[lang]
    
    package_name = message.text.strip()
    if package_name:
        if add_package(package_name):
            await message.answer(
                texts['pkg_added'].format(name=package_name),
                reply_markup=get_admin_main_keyboard(lang),
            )
        else:
            await message.answer(
                texts['pkg_exists'],
                reply_markup=get_admin_main_keyboard(lang),
            )
    else:
        await message.answer(
            texts['pkg_empty_name'],
            reply_markup=get_admin_main_keyboard(lang),
        )
    
    await state.clear()
