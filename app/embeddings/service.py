# This file converts text chunks into vector embeddings.
# The embeddings are later stored in Qdrant and used for semantic retrieval.

from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
    ):
        self.model = SentenceTransformer(
            model_name,
            device="cpu",
        )

    def embed_text(self, text: str):

        return self.model.encode(text)

    def embed_texts(self, texts: list[str]):

        return self.model.encode(texts)