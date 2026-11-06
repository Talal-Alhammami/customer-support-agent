import re

from order_service import extract_order_id

# Greetings / thanks / goodbye (the WHOLE message must be small talk)
SMALLTALK_PATTERN = re.compile(
    r"^\s*(?:hi|hello|hey|good\s+(?:morning|afternoon|evening)"
    r"|how\s+are\s+you(?:\s+doing)?"
    r"|what(?:'s|\s+is)\s+your\s+name|who\s+are\s+you"
    r"|(?:i\s+)?(?:wanna|want\s+to)\s+chat(?:\s+with\s+you)?"
    r"|yes|no|yeah|nope"
    r"|thanks?(?:\s+a\s+lot)?|thank\s+you(?:\s+(?:so|very)\s+much)?|thx"
    r"|ok|okay|bye|goodbye)\s*[!.?]*\s*$",
    re.IGNORECASE,
)

# Words that indicate a company-policy question
POLICY_PATTERN = re.compile(
    r"\b(?:returns?|refunds?|warranty|policy|policies|exchange)\b",
    re.IGNORECASE,
)

# Words that indicate the customer asks about an order status
TRACKING_PATTERN = re.compile(
    r"\b(?:where|track(?:ing)?|status|shipped)\b",
    re.IGNORECASE,
)

# The word "order" / "orders"
ORDER_WORD_PATTERN = re.compile(r"\borders?\b", re.IGNORECASE)


def classify_intent(message: str, history=()) -> tuple[str, int | None]:
    """Return (intent, order_id)."""

    history = list(history)
    text = message.strip()

    # -1. Small talk (the whole message is a greeting / thanks / goodbye)
    if SMALLTALK_PATTERN.match(message):
        return "smalltalk", None

    # 0. A bare number right after the customer talked about an order
    if text.isdigit() and len(text) >= 4:
        recent = " ".join(history[-2:])
        if ORDER_WORD_PATTERN.search(recent):
            return "order_tracking", int(text)

    is_policy = POLICY_PATTERN.search(message) is not None
    is_tracking = TRACKING_PATTERN.search(message) is not None

    # 1. Policy words without tracking words -> policy question
    if is_policy and not is_tracking:
        return "policy", None

    # 2. Order number + order intent -> order tracking
    order_id = extract_order_id(message)

    if order_id is not None:
        return "order_tracking", order_id

    # 3. Talks about an order but has no number -> ask for it
    if ORDER_WORD_PATTERN.search(message) is not None and not is_policy:
        return "ask_order_id", None

    # 4. Everything else -> company knowledge base
    return "policy", None
