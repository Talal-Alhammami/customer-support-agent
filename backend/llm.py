"""
Prompt
LLM
Transformers
Inference
"""

import os

from dotenv import load_dotenv
from transformers import pipeline

# =========================================================
# 1. Load configuration
# =========================================================

load_dotenv()

model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-0.5B-Instruct")

max_new_tokens = int(os.getenv("MAX_NEW_TOKENS", "150"))


# =========================================================
# 2. Load LLM
# =========================================================

generator = pipeline("text-generation", model=model_name)


# =========================================================
# 3. System prompt
# =========================================================

SYSTEM_PROMPT = """
You are a customer support assistant.

Answer using only the COMPANY CONTEXT.

Rules:
1. Never contradict the COMPANY CONTEXT.
2. Words like "cannot" and "not" mean the answer is NO.
3. For yes/no questions, start with YES or NO, then give one short sentence
   quoting the relevant rule from the COMPANY CONTEXT.
4. Keep the answer short.
"""


# =========================================================
# 4. Generate an answer
# =========================================================


def generate_response(user_message: str, context: str) -> str:

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
COMPANY CONTEXT:
{context}

CUSTOMER QUESTION:
{user_message}
""",
        },
    ]

    # -----------------------------------------------------
    # LLM inference
    # -----------------------------------------------------

    response = generator(messages, max_new_tokens=max_new_tokens, do_sample=False)

    # -----------------------------------------------------
    # Extract assistant answer
    # -----------------------------------------------------

    generated_text = response[0]["generated_text"]

    if isinstance(generated_text, list):
        answer = generated_text[-1]["content"]
    else:
        answer = generated_text

    answer = answer.strip()

    return answer
