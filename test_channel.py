import asyncio
from bot import bot, CHANNEL_ID

async def test_channel():
    try:
        # Get channel info
        chat = await bot.get_chat(CHANNEL_ID)
        print(f"Channel found: {chat.title}")
        print(f"Channel ID: {chat.id}")
        print(f"Channel type: {chat.type}")
        
        # Try to send a test message
        msg = await bot.send_message(CHANNEL_ID, "Test message - ignore")
        print(f"Test message sent with ID: {msg.message_id}")
        
        # Try to set reaction
        from aiogram.types import ReactionTypeEmoji
        await bot.set_message_reaction(
            chat_id=CHANNEL_ID,
            message_id=msg.message_id,
            reaction=[ReactionTypeEmoji(emoji="✅")],
        )
        print("Reaction set successfully!")
        
        # Delete test message
        await bot.delete_message(CHANNEL_ID, msg.message_id)
        print("Test message deleted")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await bot.session.close()

asyncio.run(test_channel())
