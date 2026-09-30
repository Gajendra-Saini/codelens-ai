# This file handles chunking for text files.
# It splits large text files into smaller chunks that can be embedded and retrieved.
# Different file types can use different chunking strategies.

import re

from app.repositories.models import CodeChunk


MAX_CHARACTERS = 500


class TextChunker:

    def create_chunks(self, code_file):

        paragraphs = [
            paragraph.strip()
            for paragraph in re.split(r"\n\s*\n", code_file.content)
            if paragraph.strip()
        ]

        chunks = []

        for paragraph in paragraphs:

            if len(paragraph) <= MAX_CHARACTERS:
                chunks.append(
                    self._create_chunk(
                        code_file,
                        paragraph,
                    )
                )

            else:
                chunks.extend(
                    self._split_large_paragraph(
                        code_file,
                        paragraph,
                    )
                )

        return chunks

    def _split_large_paragraph(self, code_file, paragraph):

        sentences = re.split(
            r"(?<=[.!?])\s+",
            paragraph,
        )

        chunks = []
        current_sentences = []
        current_size = 0

        for sentence in sentences:

            sentence_size = len(sentence)

            if (
                current_sentences
                and current_size + sentence_size > MAX_CHARACTERS
            ):
                content = " ".join(current_sentences)

                chunks.append(
                    self._create_chunk(
                        code_file,
                        content,
                    )
                )

                current_sentences = []
                current_size = 0

            current_sentences.append(sentence)
            current_size += sentence_size

        if current_sentences:

            content = " ".join(current_sentences)

            chunks.append(
                self._create_chunk(
                    code_file,
                    content,
                )
            )

        return chunks

    def _create_chunk(self, code_file, content):

        return CodeChunk(
            content=content,
            path=code_file.path,
            language="text",
            structure_type="text",
            name=code_file.path.name,
            parent=None,
            start_line=0,
            end_line=0,
        )