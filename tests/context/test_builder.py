from unittest.mock import Mock

from app.context.builder import ContextBuilder


def make_chunk(
    path,
    language,
    content,
):
    chunk = Mock()
    chunk.path = path
    chunk.language = language
    chunk.content = content
    return chunk


def test_context_builder_formats_single_result():

    chunk = make_chunk(
        "auth.txt",
        "text",
        "JWT authentication is implemented here.",
    )

    results = [
        {
            "id": ("auth.txt", 0),
            "score": 0.91234,
            "chunk": chunk,
        }
    ]

    builder = ContextBuilder()

    context = builder.build(results)

    assert "===== SOURCE 1 =====" in context
    assert "File: auth.txt" in context
    assert "Language: text" in context
    assert "Relevance score: 0.9123" in context
    assert "JWT authentication is implemented here." in context


def test_context_builder_formats_multiple_results():

    chunk1 = make_chunk(
        "auth.txt",
        "text",
        "JWT authentication.",
    )

    chunk2 = make_chunk(
        "database.txt",
        "text",
        "Database connection.",
    )

    results = [
        {
            "id": ("auth.txt", 0),
            "score": 0.91,
            "chunk": chunk1,
        },
        {
            "id": ("database.txt", 0),
            "score": 0.72,
            "chunk": chunk2,
        },
    ]

    builder = ContextBuilder()

    context = builder.build(results)

    assert "===== SOURCE 1 =====" in context
    assert "===== SOURCE 2 =====" in context

    assert "File: auth.txt" in context
    assert "File: database.txt" in context

    assert "JWT authentication." in context
    assert "Database connection." in context


def test_context_builder_returns_empty_string_for_no_results():

    builder = ContextBuilder()

    context = builder.build([])

    assert context == ""