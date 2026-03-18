from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from bot import bot, CHANNEL_ID
from bot.language import USER_MESSAGES, CHANNEL_MESSAGES
from keyboards.user_keyboards import (
    get_language_keyboard, 
    get_start_keyboard, 
    get_start_keyboard_uz,
    get_contact_keyboard,
    get_packages_keyboard,
    get_people_keyboard,
    get_time_keyboard,
    get_lang_settings_keyboard,
)
from states.order_states import OrderStates
from database import (
    create_order, 
    has_pending_order, 
    set_channel_message_id,
    get_user_lang,
    set_user_lang,
    get_packages,
)

user_router = Router()


@user_router.message(F.text == "/start")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    user_lang = get_user_lang(message.from_user.id)
    texts = USER_MESSAGES[user_lang]
    
    # Check if user is new (no language saved means first time)
    from database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (message.from_user.id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        # New user - ask to select language
        await message.answer(texts['welcome_new'], reply_markup=get_language_keyboard())
    else:
        # Existing user - show start button
        if user_lang == 'uz':
            keyboard = get_start_keyboard_uz()
            text = texts['welcome_return']
        else:
            keyboard = get_start_keyboard()
            text = texts['welcome_return']
        await message.answer(text, reply_markup=keyboard)


@user_router.message(F.text == "/lang")
async def cmd_lang(message: types.Message):
    user_lang = get_user_lang(message.from_user.id)
    texts = USER_MESSAGES[user_lang]
    await message.answer(
        texts['lang_settings'],
        reply_markup=get_lang_settings_keyboard(user_lang)
    )


@user_router.callback_query(F.data == "set_lang_ru")
async def set_lang_ru(callback: types.CallbackQuery):
    set_user_lang(callback.from_user.id, 'ru')
    texts = USER_MESSAGES['ru']
    await callback.message.edit_text(
        texts['lang_changed_ru'],
        reply_markup=get_lang_settings_keyboard('ru')
    )


@user_router.callback_query(F.data == "set_lang_uz")
async def set_lang_uz(callback: types.CallbackQuery):
    set_user_lang(callback.from_user.id, 'uz')
    texts = USER_MESSAGES['uz']
    await callback.message.edit_text(
        texts['lang_changed_uz'],
        reply_markup=get_lang_settings_keyboard('uz')
    )


@user_router.callback_query(F.data == "lang_ru")
async def select_language_ru(callback: types.CallbackQuery, state: FSMContext):
    set_user_lang(callback.from_user.id, 'ru')
    texts = USER_MESSAGES['ru']
    await callback.message.edit_text(
        texts['welcome_return'],
        reply_markup=get_start_keyboard()
    )


@user_router.callback_query(F.data == "lang_uz")
async def select_language_uz(callback: types.CallbackQuery, state: FSMContext):
    set_user_lang(callback.from_user.id, 'uz')
    texts = USER_MESSAGES['uz']
    await callback.message.edit_text(
        texts['welcome_return'],
        reply_markup=get_start_keyboard_uz()
    )


@user_router.callback_query(F.data == "start_order")
async def start_order(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user_lang = get_user_lang(user_id)
    texts = USER_MESSAGES[user_lang]

    if has_pending_order(user_id):
        await callback.answer(texts['has_pending'], show_alert=True)
        return

    await state.clear()
    await state.update_data(lang=user_lang)
    
    await callback.message.edit_text(texts['enter_name'])
    await state.set_state(OrderStates.name)


@user_router.message(OrderStates.name)
async def process_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    await state.update_data(name=message.text)
    await message.answer(
        texts['enter_phone'],
        reply_markup=get_contact_keyboard()
    )
    await state.set_state(OrderStates.phone)


@user_router.message(OrderStates.phone, F.contact)
async def process_phone_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    phone = message.contact.phone_number
    await state.update_data(phone=phone)
    
    packages = get_packages()
    if packages:
        await message.answer(
            texts['enter_destination'],
            reply_markup=get_packages_keyboard(packages, lang)
        )
    else:
        await message.answer(texts['enter_destination'])
    
    await state.set_state(OrderStates.destination)


@user_router.message(OrderStates.phone)
async def process_phone_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    await state.update_data(phone=message.text)
    
    packages = get_packages()
    if packages:
        await message.answer(
            texts['enter_destination'],
            reply_markup=get_packages_keyboard(packages, lang)
        )
    else:
        await message.answer(texts['enter_destination'])
    
    await state.set_state(OrderStates.destination)


@user_router.callback_query(OrderStates.destination, F.data.startswith("pkg_"))
async def select_package(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    if callback.data == "pkg_custom":
        await callback.message.answer(lang == 'uz' and "Manzilni yozing:" or texts['enter_destination'])
        await state.set_state(OrderStates.destination)
        return
    
    pkg_id = int(callback.data.split("_")[1])
    packages = get_packages()
    pkg = next((p for p in packages if p['id'] == pkg_id), None)
    
    if pkg:
        await state.update_data(destination=pkg['name'])
        await callback.message.answer(
            texts['enter_people'],
            reply_markup=get_people_keyboard(lang)
        )
        await state.set_state(OrderStates.people_count)


@user_router.message(OrderStates.destination)
async def process_destination(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    await state.update_data(destination=message.text)
    await message.answer(
        texts['enter_people'],
        reply_markup=get_people_keyboard(lang)
    )
    await state.set_state(OrderStates.people_count)


@user_router.callback_query(OrderStates.people_count, F.data.startswith("people_"))
async def select_people(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    if callback.data == "people_custom":
        await callback.message.answer("Сколько человек поедет? (введите число):")
        return
    
    people_count = int(callback.data.split("_")[1])
    await state.update_data(people_count=people_count)
    await callback.message.answer(
        texts['enter_time'],
        reply_markup=get_time_keyboard(lang)
    )
    await state.set_state(OrderStates.time)


@user_router.message(OrderStates.people_count)
async def process_people_count_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    if message.text.isdigit():
        await state.update_data(people_count=int(message.text))
        await message.answer(
            texts['enter_time'],
            reply_markup=get_time_keyboard(lang)
        )
        await state.set_state(OrderStates.time)
    else:
        await message.answer(texts['invalid_number'])


@user_router.callback_query(OrderStates.time, F.data.startswith("time_"))
async def select_time(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    if callback.data == "time_custom":
        await callback.message.answer(texts['custom_time'])
        return
    
    hour = int(callback.data.split("_")[1])
    time_str = str(hour)
    await state.update_data(time=time_str)
    
    await submit_order(callback.message, state, data, lang)


@user_router.message(OrderStates.time)
async def process_time_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang', 'ru')
    texts = USER_MESSAGES[lang]
    
    await state.update_data(time=message.text)
    await submit_order(message, state, data, lang)


async def submit_order(message: types.Message, state: FSMContext, data: dict, lang: str):
    data = await state.get_data()
    
    order_id = create_order(
        user_id=message.from_user.id,
        name=data["name"],
        phone=data["phone"],
        destination=data["destination"],
        people_count=data["people_count"],
        time=data["time"],
        lang=lang,
    )

    await state.clear()
    
    texts = USER_MESSAGES[lang]
    await message.answer(texts['order_accepted'])

    order = {
        "id": order_id,
        **data,
    }

    await send_order_to_channel(order)


async def send_order_to_channel(order: dict):
    lang = order.get('lang', 'ru')
    texts = CHANNEL_MESSAGES[lang]
    
    if lang == 'uz':
        text = f"""{texts['new_order']}

{texts['name']}: {order['name']}
{texts['phone']}: {order['phone']}
{texts['destination']}: {order['destination']}
{texts['people_count']}: {order['people_count']}
{texts['time']}: {order['time']}"""
    else:
        text = f"""{texts['new_order']}

{texts['name']}: {order['name']}
{texts['phone']}: {order['phone']}
{texts['destination']}: {order['destination']}
{texts['people_count']}: {order['people_count']}
{texts['time']}: {order['time']}"""

    try:
        print(f"Sending to channel: {CHANNEL_ID}")
        sent_message = await bot.send_message(CHANNEL_ID, text)
        print(f"Message sent with ID: {sent_message.message_id}")
        set_channel_message_id(order["id"], sent_message.message_id)
        print(f"Saved channel_message_id for order {order['id']}")
    except Exception as e:
        print(f"Error sending to channel: {e}")
