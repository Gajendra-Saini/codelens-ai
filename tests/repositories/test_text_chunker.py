from pathlib import Path
from uuid import uuid4

from app.repositories.models import CodeFile
from app.repositories.text_chunker import TextChunker


def create_code_file(content: str) -> CodeFile:

    return CodeFile(
        repository_id=uuid4(),
        path=Path("auth.txt"),
        language="text",
        content=content,
        size=len(content.encode("utf-8")),
    )


def test_single_paragraph_creates_one_chunk():

    code_file = create_code_file(
        "User authentication is handled by the auth service."
    )

    chunker = TextChunker()

    chunks = chunker.create_chunks(code_file)

    assert len(chunks) == 1
    assert chunks[0].content == (
        "User authentication is handled by the auth service."
    )


def test_multiple_paragraphs_create_multiple_chunks():

    content = (
        "Authentication validates user credentials.\n\n"
        "Authorization determines what the user can access.\n\n"
        "Logging records security events."
    )

    code_file = create_code_file(content)

    chunks = TextChunker().create_chunks(code_file)

    assert len(chunks) == 3

    assert chunks[0].content == (
        "Authentication validates user credentials."
    )

    assert chunks[1].content == (
        "Authorization determines what the user can access."
    )

    assert chunks[2].content == (
        "Logging records security events."
    )


def test_empty_paragraphs_are_ignored():

    content = (
        "First paragraph.\n\n\n\n"
        "Second paragraph.\n\n\n"
        "Third paragraph."
    )

    code_file = create_code_file(content)

    chunks = TextChunker().create_chunks(code_file)

    assert len(chunks) == 3


def test_whitespace_around_paragraphs_is_removed():

    content = (
        "   First paragraph.   \n\n"
        "   Second paragraph.   "
    )

    code_file = create_code_file(content)

    chunks = TextChunker().create_chunks(code_file)

    assert len(chunks) == 2
    assert chunks[0].content == "First paragraph."
    assert chunks[1].content == "Second paragraph."


def test_large_paragraph_is_split():

    sentence = "Authentication validates the user credentials."

    content = " ".join([sentence] * 20)

    code_file = create_code_file(content)

    chunks = TextChunker().create_chunks(code_file)

    assert len(chunks) > 1

    assert all(
        len(chunk.content) <= 500
        for chunk in chunks
    )


def test_large_paragraph_preserves_all_content():

    sentences = [
        "Authentication validates the user.",
        "Authorization checks permissions.",
        "Logging records security events.",
        "Sessions maintain user state.",
    ]

    content = " ".join(sentences)

    code_file = create_code_file(content)

    chunks = TextChunker().create_chunks(code_file)

    reconstructed = " ".join(
        chunk.content
        for chunk in chunks
    )

    assert reconstructed == content


def test_chunk_metadata_is_correct():

    code_file = create_code_file(
        "Authentication is handled here."
    )

    chunks = TextChunker().create_chunks(code_file)

    chunk = chunks[0]

    assert chunk.path == Path("auth.txt")
    assert chunk.language == "text"
    assert chunk.structure_type == "text"
    assert chunk.name == "auth.txt"
    assert chunk.parent is None
    assert chunk.start_line == 0
    assert chunk.end_line == 0


def test_multiple_chunks_keep_same_file_metadata():

    content = (
        "First paragraph.\n\n"
        "Second paragraph.\n\n"
        "Third paragraph."
    )

    code_file = create_code_file(content)

    chunks = TextChunker().create_chunks(code_file)

    assert len(chunks) == 3

    for chunk in chunks:
        assert chunk.path == Path("auth.txt")
        assert chunk.language == "text"
        assert chunk.name == "auth.txt"


def test_sentence_without_terminal_punctuation_is_preserved():

    content = "This sentence has no terminal punctuation"

    code_file = create_code_file(content)

    chunks = TextChunker().create_chunks(code_file)

    assert len(chunks) == 1
    assert chunks[0].content == content


def test_empty_file_creates_no_chunks():

    code_file = create_code_file("")

    chunks = TextChunker().create_chunks(code_file)

    assert chunks == []