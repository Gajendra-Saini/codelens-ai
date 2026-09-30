# This file manages storage and retrieval of vector embeddings in Qdrant.
# It creates the collection, stores vectors with metadata, searches vectors,
# and removes vectors belonging to a specific file.

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)


class QdrantVectorStore:

    def __init__(
        self,
        collection_name: str = "codelens_chunks",
        vector_size: int = 384,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.collection_name = collection_name

        self.client = QdrantClient(
            host=host,
            port=port,
        )

        if not self.client.collection_exists(
            collection_name=self.collection_name
        ):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )

    def add_points(
        self,
        points: list[PointStruct],
    ):
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(
        self,
        query_vector,
        limit: int = 5,
    ):
        query = (
            query_vector.tolist()
            if hasattr(query_vector, "tolist")
            else query_vector
        )

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query,
            limit=limit,
        )

        return results.points

    def delete_file(
        self,
        repository_id: str,
        file_path: str,
    ):
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="repository_id",
                        match=MatchValue(
                            value=repository_id
                        ),
                    ),
                    FieldCondition(
                        key="path",
                        match=MatchValue(
                            value=file_path
                        ),
                    ),
                ]
            ),
        )