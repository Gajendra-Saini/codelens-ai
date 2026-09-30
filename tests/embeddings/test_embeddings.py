from app.embeddings.service import EmbeddingService
import numpy as np

def test_embed_text_returns_embedding():

    service = EmbeddingService()

    embedding = service.embed_text(
        "Authentication validates user credentials."
    )

    assert embedding is not None
    assert len(embedding) == 384


def test_embed_texts_returns_embedding_for_each_input():

    service = EmbeddingService()

    texts = [
        "Authentication validates credentials.",
        "Payment processing handles transactions.",
        "Database stores application data.",
    ]

    embeddings = service.embed_texts(texts)

    assert len(embeddings) == len(texts)

    for embedding in embeddings:
        assert len(embedding) == 384


def test_same_text_produces_same_embedding():

    service = EmbeddingService()

    embedding1 = service.embed_text(
        "Authentication validates user credentials."
    )

    embedding2 = service.embed_text(
        "Authentication validates user credentials."
    )

    assert embedding1.tolist() == embedding2.tolist()


def test_different_text_produces_different_embedding():

    service = EmbeddingService()

    embedding1 = service.embed_text(
        "Authentication validates user credentials."
    )

    embedding2 = service.embed_text(
        "The payment service processes transactions."
    )

    assert embedding1.tolist() != embedding2.tolist()


def test_batch_embeddings_preserve_input_order():

    service = EmbeddingService()

    texts = [
        "Authentication service",
        "Payment service",
        "Database service",
    ]

    embeddings = service.embed_texts(texts)

    individual_embeddings = [
        service.embed_text(text)
        for text in texts
    ]

    for batch_embedding, individual_embedding in zip(
        embeddings,
        individual_embeddings,
    ):
        assert np.allclose(
            batch_embedding,
            individual_embedding,
            rtol=1e-5,
            atol=1e-5,
        )