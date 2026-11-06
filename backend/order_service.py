import re

# Order intent: the message must talk about an order / tracking / delivery
ORDER_INTENT_PATTERN = re.compile(
    r"\b(?:orders?|track(?:ing|ed)?|shipments?)\b"
    r"|\bshipping status\b"
    r"|\bdelivery status\b"
    r"|\bpackage status\b",
    re.IGNORECASE,
)

# Order ID: a number with 4 digits or more
ORDER_ID_PATTERN = re.compile(r"\b\d{4,}\b")


def extract_order_id(message: str) -> int | None:

    # Ignore the number if the message has no order/tracking intent
    if ORDER_INTENT_PATTERN.search(message) is None:
        return None

    match = ORDER_ID_PATTERN.search(message)

    if match is None:
        return None

    return int(match.group())


def build_order_answer(order: dict) -> str:

    answer = f"Order {order['order_id']} for {order['product']} is currently {order['status']}."

    if order["tracking_number"]:
        answer += f" The tracking number is {order['tracking_number']}."

    if order["expected_delivery"]:
        answer += f" The expected delivery date is {order['expected_delivery']}."

    return answer


if __name__ == "__main__":
    test_messages = [
        "Where is order 1001?",
        "Track order 1002",
        "What is the delivery status of order 1003?",
        "Where are my orders 1001?",
        "Can I return opened software products?",
        "Can I return opened software product 1001?",
        "What happened in 2026?",
    ]

    for message in test_messages:
        order_id = extract_order_id(message)

        print(f"Message: {message}")
        print(f"Order ID: {order_id}")
        print("-" * 60)
