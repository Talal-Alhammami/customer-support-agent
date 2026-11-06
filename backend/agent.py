import os
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from database import get_order
from llm import generate_response
from order_service import build_order_answer
from rag import search_documents
from router import classify_intent

# =========================================================
# Configuration
# =========================================================

load_dotenv()

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))

NO_INFO_ANSWER = (
    "I'm not sure about that. I can help with order tracking "
    "and questions about returns, shipping, and warranty."
)


# =========================================================
# 1. State
# =========================================================


class AgentState(TypedDict, total=False):
    message: str
    history: list  # last customer messages
    intent: str
    order_id: int | None
    answer: str
    source_type: str
    order: dict | None
    sources: list
    context: str


# =========================================================
# 2. Nodes
# =========================================================


def classify(state: AgentState) -> AgentState:

    history = state.get("history", [])

    intent, order_id = classify_intent(state["message"], history)

    return {"intent": intent, "order_id": order_id}


def order_node(state: AgentState) -> AgentState:

    order_id = state["order_id"]
    order = get_order(order_id)

    if order is None:
        return {
            "answer": f"I could not find order {order_id}.",
            "source_type": "database",
            "order": None,
        }

    return {
        "answer": build_order_answer(order),
        "source_type": "database",
        "order": order,
    }


def policy_node(state: AgentState) -> AgentState:

    message = state["message"]

    results = search_documents(message, top_k=1)

    # Keep only results that are similar enough to the question
    results = [result for result in results if result["score"] >= SIMILARITY_THRESHOLD]

    if not results:
        return {
            "answer": NO_INFO_ANSWER,
            "source_type": "rag",
            "sources": [],
            "context": "",
        }

    context = "\n\n".join(result["content"] for result in results)

    answer = generate_response(
        user_message=message,
        context=context,
    )

    return {
        "answer": answer,
        "source_type": "rag",
        "sources": results,
        "context": context,
    }


def ask_order_id_node(state: AgentState) -> AgentState:

    return {
        "answer": "Please send your order number so I can check it.",
        "source_type": "clarification",
    }


def smalltalk_node(state: AgentState) -> AgentState:

    lowered = state["message"].lower()

    if "thank" in lowered or "thx" in lowered:
        answer = "You're welcome! Is there anything else I can help you with?"
    elif "bye" in lowered:
        answer = "Goodbye! Have a great day."
    elif "how are you" in lowered:
        answer = "I'm doing well, thank you! How can I help you today?"
    elif "your name" in lowered or "who are you" in lowered:
        answer = (
            "I'm the AI customer support assistant. I can track your order "
            "and answer questions about returns, shipping, and warranty."
        )
    elif lowered.strip(" !.?") in ("yes", "yeah", "no", "nope") or "chat" in lowered:
        answer = "Sure! Tell me what you need help with."
    else:
        answer = "Hello! How can I help you today?"

    return {"answer": answer, "source_type": "smalltalk"}


# =========================================================
# 3. Routing function
# =========================================================


def route(state: AgentState) -> str:
    return state["intent"]


# =========================================================
# 4. Build the graph
# =========================================================

builder = StateGraph(AgentState)

builder.add_node("classify", classify)
builder.add_node("order_tracking", order_node)
builder.add_node("policy", policy_node)
builder.add_node("ask_order_id", ask_order_id_node)
builder.add_node("smalltalk", smalltalk_node)

builder.add_edge(START, "classify")

builder.add_conditional_edges(
    "classify",
    route,
    {
        "order_tracking": "order_tracking",
        "policy": "policy",
        "ask_order_id": "ask_order_id",
        "smalltalk": "smalltalk",
    },
)

builder.add_edge("order_tracking", END)
builder.add_edge("policy", END)
builder.add_edge("ask_order_id", END)
builder.add_edge("smalltalk", END)

graph = builder.compile()


# =========================================================
# 5. Manual test
# =========================================================

if __name__ == "__main__":
    tests = [
        ("Where is order 1001?", []),
        ("Track order 9999", []),
        ("Where is my order?", []),
        ("1001", ["where is my order"]),
        ("1001", []),
        ("Can I return opened software products?", []),
        ("How long is the laptop warranty?", []),
        ("Do I get free coffee when I buy a laptop?", []),
        ("thank you", []),
    ]

    for text, history in tests:
        result = graph.invoke({"message": text, "history": history})

        print("\nQUESTION:", text, "| history:", history)
        print("INTENT:  ", result["intent"])
        print("SOURCE:  ", result["source_type"])
        print("ANSWER:  ", result["answer"])
