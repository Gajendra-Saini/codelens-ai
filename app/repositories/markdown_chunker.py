import re

from app.repositories.models import CodeChunk, CodeFile


MAX_LINES = 100


class MarkdownChunker:

    def create_chunks(
        self,
        code_file: CodeFile,
    ) -> list[CodeChunk]:

        lines = code_file.content.splitlines()

        chunks = []

        current_lines = []
        current_heading = None
        start_line = None

        for line_number, line in enumerate(lines, start=1):

            if re.match(r"^#{1,6}\s+", line):

                if current_lines:
                    chunks.extend(
                        self._create_chunks(
                            code_file,
                            current_lines,
                            current_heading,
                            start_line,
                            line_number - 1,
                        )
                    )

                current_heading = line.strip("# ").strip()
                current_lines = [line]
                start_line = line_number

            else:

                if start_line is None:
                    start_line = line_number

                current_lines.append(line)

        if current_lines:
            chunks.extend(
                self._create_chunks(
                    code_file,
                    current_lines,
                    current_heading,
                    start_line,
                    len(lines),
                )
            )

        return chunks

    def _create_chunks(
        self,
        code_file,
        lines,
        heading,
        start_line,
        end_line,
    ):
        chunks = []

        total_lines = len(lines)

        for offset in range(0, total_lines, MAX_LINES):

            chunk_lines = lines[offset:offset + MAX_LINES]

            chunk_start_line = start_line + offset

            chunk_end_line = min(
                chunk_start_line + len(chunk_lines) - 1,
                end_line,
            )

            chunks.append(
                self._create_chunk(
                    code_file,
                    chunk_lines,
                    heading,
                    chunk_start_line,
                    chunk_end_line,
                )
            )

        return chunks

    def _create_chunk(
        self,
        code_file,
        lines,
        heading,
        start_line,
        end_line,
    ):
        content = "\n".join(lines)

        return CodeChunk(
            content=content,
            path=code_file.path,
            language=code_file.language,
            structure_type="markdown_section",
            name=heading or "document",
            parent=None,
            start_line=start_line,
            end_line=end_line,
        )