class ContextBuilder:

    def build(self, results):

        context_parts = []

        for rank, result in enumerate(results, start=1):

            chunk = result["chunk"]
            score = result["score"]

            source = f"""===== SOURCE {rank} =====
File: {chunk.path}
Language: {chunk.language}
Relevance score: {score:.4f}

{chunk.content}
"""

            context_parts.append(source)

        return "\n".join(context_parts)