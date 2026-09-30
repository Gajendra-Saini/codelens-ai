from app.repositories.chunker import CodeChunker
from app.repositories.markdown_chunker import MarkdownChunker
from app.repositories.text_chunker import TextChunker


class RepositoryChunker:

    def __init__(self):
        self.text_chunker = TextChunker()
        self.markdown_chunker = MarkdownChunker()
        self.code_chunker = CodeChunker()

    def create_chunks(self, code_file):

        if code_file.language == "text":
            return self.text_chunker.create_chunks(code_file)

        if code_file.language == "markdown":
            return self.markdown_chunker.create_chunks(code_file)

        if code_file.language == "python":
            # For now, Python requires parsing before chunking.
            return []

        return []