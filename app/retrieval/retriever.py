import re

from rank_bm25 import BM25Okapi

from app.retrieval.rrf import ReciprocalRankFusion
from app.retrieval.reranker import CrossEncoderReranker


class Retriever:

    def __init__(
        self,
        embedding_service,
        vector_store,
        chunks,
        rrf=None,
        reranker=None,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.chunks = chunks

        self.rrf = rrf or ReciprocalRankFusion()
        self.reranker = reranker or CrossEncoderReranker()

        # -----------------------------
        # BM25 index
        # -----------------------------

        self.documents = [
            chunk.content
            for chunk in chunks
        ]

        tokenized_documents = [
            self._tokenize(document)
            for document in self.documents
        ]

        self.bm25 = BM25Okapi(
            tokenized_documents
        )

    # -----------------------------
    # Tokenization
    # -----------------------------

    def _tokenize(
        self,
        text: str,
    ) -> list[str]:

        return re.findall(
            r"\b\w+\b",
            text.lower(),
        )

    # -----------------------------
    # Dense retrieval
    # -----------------------------

    def dense_retrieve(
        self,
        query: str,
        limit: int = 20,
    ):

        query_vector = (
            self.embedding_service.embed_text(query)
        )

        return self.vector_store.search(
            query_vector,
            limit=limit,
        )

    # -----------------------------
    # BM25 retrieval
    # -----------------------------

    def bm25_retrieve(
        self,
        query: str,
        limit: int = 20,
    ):

        tokenized_query = self._tokenize(
            query
        )

        scores = self.bm25.get_scores(
            tokenized_query
        )

        ranked_ids = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )[:limit]

        return [
            {
                "id": chunk_id,
                "score": scores[chunk_id],
                "chunk": self.chunks[chunk_id],
            }
            for chunk_id in ranked_ids
        ]

    # -----------------------------
    # Full retrieval pipeline
    # -----------------------------

    def retrieve(
        self,
        query: str,
        limit: int = 5,
        candidate_limit: int = 20,
    ):

        # 1. Dense retrieval

        dense_results = self.dense_retrieve(
            query,
            limit=candidate_limit,
        )

        dense_ids = [
            result.id
            for result in dense_results
        ]

        # 2. BM25 retrieval

        bm25_results = self.bm25_retrieve(
            query,
            limit=candidate_limit,
        )

        bm25_ids = [
            result["id"]
            for result in bm25_results
        ]

        # 3. RRF

        rrf_results = self.rrf.fuse(
            [
                dense_ids,
                bm25_ids,
            ]
        )

        # 4. Convert RRF IDs into
        #    (chunk_id, chunk) pairs

        candidates = [
            (
                chunk_id,
                self.chunks[chunk_id],
            )
            for chunk_id, score in rrf_results
        ]

        # 5. Cross-encoder reranking

        reranked_results = self.reranker.rerank(
            query=query,
            candidates=candidates,
            limit=limit,
        )

        return reranked_results