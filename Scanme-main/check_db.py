from database import get_order_by_id, get_pending_orders, get_order_history

print("=== Pending Orders ===")
pending = get_pending_orders()
for order in pending:
    print(f"ID: {order['id']}, Name: {order['name']}, Channel Msg ID: {order.get('channel_message_id')}")

print("\n=== Order History ===")
history = get_order_history()
for order in history:
    print(f"ID: {order['id']}, Name: {order['name']}, Status: {order['status']}, Channel Msg ID: {order.get('channel_message_id')}")
