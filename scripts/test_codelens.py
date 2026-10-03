from pathlib import Path

from app.repositories.loader import RepositoryLoader
from app.indexing.repository_indexer_service import (
    RepositoryIndexingService,
)
from app.retrieval.service import RetrievalService
from app.generation.prompt_builder import PromptBuilder
from app.generation.llm import LLMService
from app.generation.query_service import QueryService


def main():

    print("=" * 70)
    print("CODELENS AI")
    print("=" * 70)

    repo_url = input(
        "\nEnter GitHub repository URL: "
    ).strip()

    question = input(
        "\nEnter your question: "
    ).strip()

    print("\n" + "=" * 70)
    print("STEP 1: INDEXING REPOSITORY")
    print("=" * 70)

    indexing_service = RepositoryIndexingService()

    indexing_result = (
        indexing_service.index_repository(
            repo_url
        )
    )

    repository_id = indexing_result[
        "repository_id"
    ]

    print(
        f"\nRepository ID: {repository_id}"
    )

    print(
        f"Files found: "
        f"{indexing_result['files_found']}"
    )

    print("\nIndexing results:")

    for result in indexing_result["results"]:

        print(
            f"- {result['status']:8} "
            f"{result['path']}"
        )

    if indexing_result["deleted_files"]:

        print("\nDeleted files:")

        for path in indexing_result[
            "deleted_files"
        ]:
            print(f"- {path}")

    print("\n" + "=" * 70)
    print("STEP 2: BUILDING RETRIEVAL PIPELINE")
    print("=" * 70)

    loader = RepositoryLoader(
        storage_dir="storage/repositories"
    )

    repository = loader.clone(repo_url)

    retrieval_service = RetrievalService(
        repository_loader=loader
    )

    retrieval_pipeline = (
        retrieval_service.build_pipeline(
            repository
        )
    )

    print("Retrieval pipeline ready.")

    print("\n" + "=" * 70)
    print("STEP 3: QUERYING CODEBASE")
    print("=" * 70)

    prompt_builder = PromptBuilder()

    llm_service = LLMService()

    query_service = QueryService(
        retrieval_pipeline=retrieval_pipeline,
        prompt_builder=prompt_builder,
        llm_service=llm_service,
    )

    result = query_service.answer(
        question
    )

    print("\n" + "=" * 70)
    print("ANSWER")
    print("=" * 70)

    print(
        f"\n{result['answer']}"
    )

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    if result["results"]:

        for index, item in enumerate(
            result["results"],
            start=1,
        ):

            chunk = item["chunk"]

            print(
                f"\n[{index}] "
                f"{chunk.path}"
            )

            print(
                f"Score: "
                f"{item['score']:.4f}"
            )

    else:

        print(
            "\nNo relevant sources found."
        )


if __name__ == "__main__":
    main()