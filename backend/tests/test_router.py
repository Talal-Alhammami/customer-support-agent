import pytest

from router import classify_intent


@pytest.mark.parametrize(
    "message, expected_intent, expected_order_id",
    [
        # Order tracking
        ("Where is order 1001?", "order_tracking", 1001),
        ("Track order 1002", "order_tracking", 1002),
        ("What is the delivery status of order 1003?", "order_tracking", 1003),
        # Order question without a number
        ("Where is my order?", "ask_order_id", None),
        # Policy questions
        ("Can I return opened software products?", "policy", None),
        ("How long is the laptop warranty?", "policy", None),
        ("What is the refund policy?", "policy", None),
        # The cases the old router got wrong
        ("Can I return order 1001?", "policy", None),
        ("Can I return opened software product 1001?", "policy", None),
        ("What happened in 2026?", "policy", None),
        # Small talk
        ("thank you", "smalltalk", None),
        ("Thanks!", "smalltalk", None),
        ("hello", "smalltalk", None),
        ("bye", "smalltalk", None),
        # Small talk + a real question must NOT be small talk
        ("hello, where is order 1001?", "order_tracking", 1001),
        ("what is your name", "smalltalk", None),
        ("yes", "smalltalk", None),
        ("i wanna chat with you", "smalltalk", None),
    ],
)
def test_classify_intent(message, expected_intent, expected_order_id):

    intent, order_id = classify_intent(message)

    assert intent == expected_intent
    assert order_id == expected_order_id


def test_bare_number_after_order_question():
    assert classify_intent("1001", ["where is my order"]) == ("order_tracking", 1001)


def test_bare_number_without_context():
    assert classify_intent("1001", []) == ("policy", None)


def test_bare_number_after_unrelated_message():
    assert classify_intent("1001", ["can I return a product"]) == ("policy", None)
