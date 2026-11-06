"""
HTTP
FastAPI
Pydantic
POST /chat
"""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import graph
from database import get_order

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Customer Support Agent API",
    description=(
        "Customer Support Agent using LangGraph, SQLite, RAG, "
        "Hugging Face Transformers, and FastAPI."
    ),
    version="2.0.0",
)

# Allow the React frontend (different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# Request model
# =========================================================


class ChatRequest(BaseModel):
    message: str
    history: list[str] = []  # last customer messages (optional)


# =========================================================
# General endpoints
# =========================================================


@app.get("/")
def home():
    return {"message": "Customer Support API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


# =========================================================
# Orders endpoint
# =========================================================


@app.get("/orders/{order_id}")
def read_order(order_id: int):

    order = get_order(order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail=f"Order {order_id} was not found.",
        )

    return order


# =========================================================
# Chat endpoint
# =========================================================


@app.post("/chat")
def chat(request: ChatRequest):

    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(
            status_code=400,
            detail="The message cannot be empty.",
        )

    try:
        result = graph.invoke(
            {
                "message": user_message,
                "history": request.history,
            }
        )

    except Exception as error:
        logger.exception("Agent failed for message: %r", user_message)

        raise HTTPException(
            status_code=500,
            detail="Internal agent error. Please try again.",
        ) from error

    response = {
        "answer": result["answer"],
        "intent": result["intent"],
        "source_type": result["source_type"],
    }

    # Extra fields that belong to each route
    if result["source_type"] == "database":
        response["order"] = result.get("order")

    if result["source_type"] == "rag":
        response["sources"] = result.get("sources", [])
        response["context"] = result.get("context", "")

    return response
