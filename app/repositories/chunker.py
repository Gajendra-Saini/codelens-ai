from app.repositories.models import CodeChunk, CodeFile, CodeStructure


class CodeChunker:

    def create_chunk(
        self,
        code_file: CodeFile,
        structure: CodeStructure,
    ) -> CodeChunk:

        lines = code_file.content.splitlines()

        content = "\n".join(
            lines[
                structure.start_line - 1 : structure.end_line
            ]
        )

        return CodeChunk(
            content=content,
            path=code_file.path,
            language=code_file.language,
            structure_type=structure.type,
            name=structure.name,
            parent=structure.parent,
            start_line=structure.start_line,
            end_line=structure.end_line,
        )