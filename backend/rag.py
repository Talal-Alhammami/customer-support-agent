from pathlib import Path

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

KNOWLEDGE_DIR = Path("data")

embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def load_documents():

    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")

        documents.append({"source": file_path.name, "content": content})

    return documents


def create_chunks(documents):

    chunks = []

    for document in documents:
        paragraphs = [
            paragraph.strip()
            for paragraph in document["content"].split("\n\n")
            if paragraph.strip()
        ]

        if not paragraphs:
            continue

        title = paragraphs[0]

        for paragraph in paragraphs[1:]:
            chunks.append({"source": document["source"], "content": f"{title}\n{paragraph}"})

    return chunks


def search_documents(question: str, top_k: int = 1):

    documents = load_documents()

    chunks = create_chunks(documents)

    question_embedding = embedding_model.encode(question, convert_to_tensor=True)

    chunk_texts = [chunk["content"] for chunk in chunks]

    chunk_embeddings = embedding_model.encode(chunk_texts, convert_to_tensor=True)

    scores = cos_sim(question_embedding, chunk_embeddings)[0]

    top_results = scores.topk(k=min(top_k, len(chunks)))

    MIN_SCORE = 0.35
    results = []

    for score, index in zip(top_results.values, top_results.indices, strict=True):
        score_value = score.item()
        if score_value < MIN_SCORE:
            continue

        chunk = chunks[index.item()]  # type: ignore

        results.append(
            {"source": chunk["source"], "content": chunk["content"], "score": score_value}
        )

    return results


if __name__ == "__main__":
    question = "Can I return opened software products"

    results = search_documents(question, top_k=3)

    print("\nQUESTION:")
    print(question)

    for number, result in enumerate(results, start=1):
        print(f"\nRESULT #{number}")

        print("SOURCE:")
        print(result["source"])

        print("SIMILARITY:")
        print(result["score"])

        print("CONTENT:")
        print(result["content"])

        print("-" * 50)
