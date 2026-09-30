# CodeLens AI --- Part 1: Repository Ingestion & Indexing {#codelens-ai--part-1-repository-ingestion--indexing}

## 1. Purpose {#1-purpose}

Part 1 prepares a GitHub repository so CodeLens can retrieve useful
information later.

Current V1 supports `.txt` files only.

Core pipeline:

``` text
GitHub URL
    ↓
Validate URL
    ↓
Clone / Update Repository
    ↓
Discover Supported Files
    ↓
Build CodeFile objects
    ↓
Chunk Files
    ↓
Generate Embeddings
    ↓
Create Qdrant Points
    ↓
Store Vectors + Metadata
    ↓
Track File Hashes
    ↓
Support Incremental Indexing
```

------------------------------------------------------------------------

## 2. High-Level Architecture {#2-high-level-architecture}

``` text
GitHub URL
    ↓
RepositoryLoader
    ↓
CodeFile[]
    ↓
RepositoryIndexingService
    ↓
RepositoryIndexer
    ├── Indexer
    ├── TextChunker
    ├── EmbeddingService
    └── QdrantVectorStore
             ↓
           Qdrant

Indexer
    ↓
IndexMetadataStore
    ↓
storage/index_metadata.json
```

The key idea is separation of responsibilities:

  Component                                  Responsibility
  ------------------------------------------ --------------------------------------------
  `config.py`                                Application configuration
  `models.py`                                Data models
  `validator.py`                             GitHub URL validation
  `languages.py`                             Extension → language mapping
  `loader.py`                                Clone/update, discovery, CodeFile creation
  `text_chunker.py`                          Text → chunks
  `embeddings/service.py`                    Text → vectors
  `vectorstore/qdrant.py`                    Vector storage/search/deletion
  `indexing/metadata.py`                     Metadata persistence
  `indexing/indexer.py`                      Change detection
  `indexing/repository_indexer.py`           Complete indexing of one file
  `indexing/repository_indexer_service.py`   Complete indexing of one repository
  `main.py`                                  FastAPI entry point

------------------------------------------------------------------------

## 3. Data Models --- `models.py` {#3-data-models--modelspy}

`models.py` defines the objects flowing through the ingestion/indexing
pipeline.

### Repository

``` python
class Repository(BaseModel):
    id: UUID
    path: Path
```

Represents a locally stored repository.

### CodeFile

``` python
class CodeFile(BaseModel):
    repository_id: UUID
    path: Path
    language: str
    content: str
    size: int
```

Represents one complete discovered file.

Mental model:

``` text
physical file
    ↓
CodeFile
```

### CodeStructure

Stores structural information such as type, name, parameters, line
range, parent, and docstring. It is mainly for future
structured-language parsing and is not central to the current `.txt` V1
flow.

### CodeChunk

``` python
class CodeChunk(BaseModel):
    content: str
    path: Path
    language: str
    structure_type: str
    name: str
    parent: str | None
    start_line: int
    end_line: int
```

Represents a retrieval-sized unit produced from a file.

Mental model:

``` text
CodeFile
   ↓
chunker
   ↓
CodeChunk[]
```

------------------------------------------------------------------------

## 4. URL Validation --- `validator.py` {#4-url-validation--validatorpy}

`validator.py` performs the first validation step after a repository URL
is provided.

Current checks:

``` text
HTTPS
+
github.com
+
owner/repository path
```

Example:

``` text
https://github.com/Gajendra-Saini/testingrag
```

Flow:

``` text
User URL
   ↓
is_valid_git_url()
   ↓
True / False
```

This prevents us from attempting to clone an obviously invalid
repository URL.

------------------------------------------------------------------------

## 5. Language Mapping --- `languages.py` {#5-language-mapping--languagespy}

`languages.py` maps file extensions to language names.

Examples:

``` text
.py   → python
.js   → javascript
.ts   → typescript
.md   → markdown
.txt  → text
```

Although V1 indexes only `.txt`, the mapping already contains
future-supported extensions.

Mental shortcut:

``` text
extension → language
```

------------------------------------------------------------------------

## 6. Repository Loading --- `loader.py` {#6-repository-loading--loaderpy}

`loader.py` is responsible for:

1.  validating the GitHub URL
2.  cloning a repository
3.  updating an existing repository
4.  discovering supported files recursively
5.  reading files
6.  creating `CodeFile` objects

Mental shortcut:

``` text
GitHub URL
    ↓
local repository
    ↓
files
    ↓
CodeFile[]
```

### Deterministic Repository ID

The loader normalizes the URL and generates a UUID5.

This means equivalent URL forms can map to the same repository identity.

The repository ID is then used for:

``` text
local storage
metadata namespace
Qdrant metadata
```

### First run

``` text
repository doesn't exist
        ↓
git clone
        ↓
storage/repositories/<repository_id>
```

### Later run

``` text
repository already exists
        ↓
git pull --ff-only
```

### File discovery

Current V1:

``` python
SUPPORTED_EXTENSIONS = {
    ".txt",
}
```

Ignored directories include:

``` text
.git
__pycache__
.venv
venv
node_modules
.pytest_cache
```

Discovery is recursive and uses a lower-cased suffix, so `.txt`, `.TXT`,
etc. are treated consistently.

### Building a CodeFile

The loader:

``` text
read UTF-8 content
      ↓
get file size
      ↓
identify language
      ↓
convert absolute path to repository-relative path
      ↓
create CodeFile
```

------------------------------------------------------------------------

## 7. Text Chunking --- `text_chunker.py` {#7-text-chunking--text_chunkerpy}

`text_chunker.py` handles chunking for text files.

Current maximum:

``` text
500 characters
```

The strategy is:

``` text
file content
    ↓
split into paragraphs
    ↓
small paragraph?
    ├── yes → one chunk
    └── no  → split into sentences
                 ↓
             combine sentences
                 ↓
              chunks
```

For example:

``` text
Large paragraph
      ↓
Sentence A. Sentence B. Sentence C.
      ↓
Chunk 1
Chunk 2
```

Current text chunks use:

``` text
language       = text
structure_type = text
parent         = None
start_line     = 0
end_line       = 0
```

Line ranges are currently not calculated because V1 is a simple text
chunker.

Future architecture can have:

``` text
.txt → TextChunker
.md  → MarkdownChunker
.py  → PythonChunker
.js  → JavaScriptChunker
```

------------------------------------------------------------------------

## 8. Embeddings --- `embeddings/service.py` {#8-embeddings--embeddingsservicepy}

`EmbeddingService` converts text into numerical vectors.

Current model:

``` text
all-MiniLM-L6-v2
```

Current vector size:

``` text
384 dimensions
```

Mental model:

``` text
text
 ↓
EmbeddingService
 ↓
384-dimensional vector
```

There are two methods:

``` text
embed_text()
    → one text

embed_texts()
    → multiple texts
```

The indexing pipeline mainly uses `embed_texts()` because a file
normally produces multiple chunks.

Example:

``` text
Chunk 1
Chunk 2
Chunk 3
   ↓
embed_texts()
   ↓
Vector 1
Vector 2
Vector 3
```

Embeddings allow later semantic retrieval.

------------------------------------------------------------------------

## 9. Qdrant --- `vectorstore/qdrant.py` {#9-qdrant--vectorstoreqdrantpy}

`qdrant.py` is the abstraction layer between CodeLens and Qdrant.

It handles:

``` text
create collection
add points
search vectors
delete vectors for a file
```

Mental model:

``` text
CodeLens
   ↓
QdrantVectorStore
   ↓
Qdrant
```

### Collection

Current collection:

``` text
codelens_chunks
```

It is configured for:

``` text
384-dimensional vectors
COSINE distance
```

The vector dimension must match the embedding model.

### Qdrant Point

A point contains:

``` text
ID
+
VECTOR
+
PAYLOAD
```

Our payload includes:

``` text
repository_id
path
file_hash
content
language
structure_type
name
parent
start_line
end_line
chunk_index
```

The vector supports semantic search; the payload preserves source
information and chunk metadata.

### Deterministic point IDs

Point IDs are generated from:

``` text
repository_id
+
file_path
+
chunk_index
```

This gives a stable identity to the same repository/file/chunk position.

### Deletion

`delete_file()` filters using:

``` text
repository_id
+
path
```

This prevents deleting a same-named file from another repository.

------------------------------------------------------------------------

## 10. Metadata --- `indexing/metadata.py` {#10-metadata--indexingmetadatapy}

`metadata.py` manages:

``` text
storage/index_metadata.json
```

Its job is only metadata persistence:

``` text
load()
save()
remove_file()
```

It does not decide whether a file changed.

Conceptual structure:

``` json
{
  "repositories": {
    "repository-id": {
      "files": {
        "auth.txt": {
          "hash": "...",
          "indexed": true
        }
      }
    }
  }
}
```

Mental shortcut:

``` text
metadata.py
→ manages stored indexing state
```

------------------------------------------------------------------------

## 11. Incremental Change Detection --- `indexing/indexer.py` {#11-incremental-change-detection--indexingindexerpy}

`indexer.py` answers:

> Should this file be indexed?

It uses `IndexMetadataStore`.

### Hashing

File content is converted to a SHA-256 hash:

``` text
file content
    ↓
SHA-256
    ↓
hash
```

### `should_index()`

Logic:

``` text
file metadata exists?
       │
   ┌───┴───┐
  NO      YES
   │        │
 INDEX   calculate hash
            │
       compare hashes
          │     │
        same  different
          │     │
        SKIP   INDEX
```

Therefore:

``` text
new       → index
unchanged → skip
changed   → index
```

### `mark_indexed()`

After successful indexing, it stores:

``` text
hash
indexed = true
```

This allows the next indexing run to compare the new content with the
previously indexed version.

------------------------------------------------------------------------

## 12. File-Level Indexing --- `indexing/repository_indexer.py` {#12-file-level-indexing--indexingrepository_indexerpy}

`RepositoryIndexer` handles one file from beginning to end.

Mental shortcut:

``` text
RepositoryIndexer
→ index ONE CodeFile
```

Dependencies:

``` text
RepositoryIndexer
├── Indexer
├── Chunker
├── EmbeddingService
└── QdrantVectorStore
```

### Complete flow

``` text
CodeFile
   ↓
1. Check whether indexing is needed
   ↓
2. Delete old vectors
   ↓
3. Chunk
   ↓
4. Embed
   ↓
5. Create Qdrant points
   ↓
6. Store vectors
   ↓
7. Mark indexed
```

### Step 1 --- Should index? {#step-1--should-index}

If:

``` python
should_index() == False
```

return:

``` text
status = skipped
```

No embedding or Qdrant work is performed.

### Step 2 --- Delete old vectors {#step-2--delete-old-vectors}

For a changed file, old vectors are removed before new vectors are
inserted.

Otherwise:

``` text
old chunks + new chunks
```

could coexist and stale content could be retrieved.

Correct:

``` text
delete old
   ↓
create new
   ↓
store new
```

### Step 3 --- Chunk {#step-3--chunk}

``` text
CodeFile
   ↓
TextChunker
   ↓
CodeChunk[]
```

### Empty file

If:

``` text
chunks == []
```

the embedding model is not called.

The file is marked indexed with:

``` text
chunks = 0
```

No vectors are created.

### Step 4 --- Embed {#step-4--embed}

Chunk contents are passed to:

``` text
EmbeddingService.embed_texts()
```

### Step 5 --- Create points {#step-5--create-points}

Each chunk and embedding become a `PointStruct`.

The point stores:

``` text
deterministic ID
vector
payload
```

### Step 6 --- Store {#step-6--store}

Points are sent to:

``` text
QdrantVectorStore.add_points()
```

### Step 7 --- Mark indexed {#step-7--mark-indexed}

Only after Qdrant storage succeeds do we call:

``` text
Indexer.mark_indexed()
```

This prevents metadata from claiming success when vector storage failed.

------------------------------------------------------------------------

## 13. Deleted File Handling {#13-deleted-file-handling}

`RepositoryIndexer` also handles files that disappeared from the
repository.

Suppose metadata contains:

``` text
auth.txt
database.txt
payment.txt
random.txt
```

but the current repository contains:

``` text
auth.txt
database.txt
payment.txt
```

Then:

``` text
indexed_files - current_file_paths
```

produces:

``` text
random.txt
```

For each deleted file:

``` text
delete Qdrant vectors
        ↓
remove metadata
```

This prevents stale data.

------------------------------------------------------------------------

## 14. Repository-Level Orchestration --- `repository_indexing_service.py` {#14-repository-level-orchestration--repository_indexing_servicepy}

This is the main indexing orchestrator.

Mental shortcut:

``` text
RepositoryIndexingService
→ index the WHOLE repository
```

It connects:

``` text
RepositoryLoader
RepositoryIndexer
```

and constructs the lower-level dependencies.

### Dependency tree

``` text
RepositoryIndexingService
        │
        ├── RepositoryLoader
        │
        └── RepositoryIndexer
                ├── Indexer
                │     └── IndexMetadataStore
                ├── TextChunker
                ├── EmbeddingService
                └── QdrantVectorStore
```

### `index_repository()`

The complete sequence:

``` text
1. Clone/update repository
2. Discover supported files
3. Build CodeFile objects
4. Track current file paths
5. Index each file
6. Remove deleted files
7. Return summary
```

### Return summary

The service returns:

``` text
repository_id
files_found
results
deleted_files
```

This gives the caller a high-level result of the indexing operation.

------------------------------------------------------------------------

## 15. RepositoryIndexer vs RepositoryIndexingService {#15-repositoryindexer-vs-repositoryindexingservice}

This distinction is critical.

### `RepositoryIndexer`

Handles:

``` text
ONE FILE
```

Example:

``` text
auth.txt
```

### `RepositoryIndexingService`

Handles:

``` text
WHOLE REPOSITORY
```

Example:

``` text
auth.txt
database.txt
payment.txt
testing.txt
```

Think:

``` text
RepositoryIndexingService
        ↓
for each CodeFile
        ↓
RepositoryIndexer.index_file()
```

------------------------------------------------------------------------

## 16. Dependency Injection {#16-dependency-injection}

`RepositoryIndexingService` accepts optional dependencies.

Production:

``` text
real RepositoryLoader
real RepositoryIndexer
real Qdrant
real embeddings
```

Tests:

``` text
Mock RepositoryLoader
Mock RepositoryIndexer
```

This lets us test orchestration without:

``` text
cloning GitHub
loading models
using external infrastructure
```

It is an important reason the system is testable.

------------------------------------------------------------------------

# 17. The Four Incremental Indexing Cases {#17-the-four-incremental-indexing-cases}

These are the most important Part 1 scenarios.

## A. New file {#a-new-file}

``` text
No metadata
   ↓
should_index = True
   ↓
chunk
   ↓
embed
   ↓
Qdrant
   ↓
save hash
```

Result:

``` text
INDEX
```

## B. Unchanged file {#b-unchanged-file}

``` text
current hash == stored hash
          ↓
       SKIP
```

No new embeddings.

## C. Changed file {#c-changed-file}

``` text
current hash != stored hash
          ↓
delete old vectors
          ↓
chunk new content
          ↓
embed
          ↓
store new vectors
          ↓
save new hash
```

Result:

``` text
RE-INDEX
```

## D. Deleted file {#d-deleted-file}

``` text
previously indexed
       ↓
not in current repository
       ↓
delete Qdrant vectors
       ↓
remove metadata
```

Result:

``` text
DELETE
```

------------------------------------------------------------------------

# 18. Why Qdrant and Metadata Are Separate {#18-why-qdrant-and-metadata-are-separate}

They solve different problems.

### Qdrant

Answers:

> Where are the searchable chunks?

Stores:

``` text
vectors
chunk content
retrieval metadata
```

### Metadata JSON

Answers:

> What version of each file did we last index?

Stores:

``` text
file hash
indexed state
```

So:

``` text
Qdrant
→ searchable knowledge

Metadata
→ indexing state
```

------------------------------------------------------------------------

# 19. Complete `auth.txt` Example {#19-complete-authtxt-example}

Suppose:

``` text
auth.txt
```

contains:

``` text
Authentication uses JWT tokens.

The validate_token function checks whether
the token is valid and expired.

Invalid tokens are rejected.
```

### Loader

Creates:

``` text
CodeFile(
    path="auth.txt",
    language="text",
    content="...",
    size=...
)
```

### Chunker

Creates:

``` text
Chunk 0:
Authentication uses JWT tokens.

Chunk 1:
The validate_token function checks whether
the token is valid and expired.

Chunk 2:
Invalid tokens are rejected.
```

### Embedding

Creates:

``` text
Vector 0
Vector 1
Vector 2
```

### Qdrant

Stores:

``` text
Point 0
Point 1
Point 2
```

Each contains:

``` text
ID
vector
repository_id
path
content
chunk_index
other metadata
```

### Metadata

Stores:

``` text
auth.txt
hash = SHA256(current content)
indexed = true
```

Now the information is ready for Part 2 retrieval.

------------------------------------------------------------------------

# 20. Why We Index Once and Retrieve Many Times {#20-why-we-index-once-and-retrieve-many-times}

We don\'t want this:

``` text
User question
    ↓
read repository
    ↓
chunk
    ↓
embed entire repository
    ↓
answer
```

for every question.

Instead:

``` text
Repository
    ↓
INDEX ONCE
    ↓
Qdrant
```

Then:

``` text
Question 1 → retrieve
Question 2 → retrieve
Question 3 → retrieve
Question 4 → retrieve
```

This separation is fundamental to the RAG architecture.

------------------------------------------------------------------------

# 21. Testing {#21-testing}

Part 1 has a regression suite of:

  Component                        Tests
  ----------------------------- --------
  Repository Loader                   14
  Text Chunker                        10
  Embedding Service                    5
  Qdrant Vector Store                  4
  Indexer / Metadata                   9
  Repository Indexer                   7
  Repository Indexing Service         10
  **Total**                       **59**

Final status:

``` text
59 / 59 PASSED
```

------------------------------------------------------------------------

# 22. What the Tests Prove {#22-what-the-tests-prove}

The suite covers:

``` text
✓ deterministic repository IDs
✓ URL normalization
✓ URL validation
✓ clone behavior
✓ pull/update behavior
✓ ignored directories
✓ extension handling
✓ CodeFile construction
✓ text chunking
✓ empty files
✓ embedding behavior
✓ embedding order
✓ Qdrant collection creation
✓ Qdrant insertion/search
✓ Qdrant deletion
✓ deterministic hashes
✓ new file detection
✓ unchanged file detection
✓ changed file detection
✓ metadata persistence
✓ individual file indexing
✓ changed-file vector replacement
✓ payload creation
✓ unique point IDs
✓ empty-chunk behavior
✓ deleted-file cleanup
✓ repository-level orchestration
```

------------------------------------------------------------------------

# 23. Debugging Map {#23-debugging-map}

When something breaks, use the responsibility boundaries.

### GitHub URL problem

Look at:

``` text
validator.py
```

### Clone/update problem

Look at:

``` text
loader.py → clone()
```

### Files missing

Look at:

``` text
loader.py → discover_files()
```

and:

``` text
SUPPORTED_EXTENSIONS
IGNORED_DIRECTORIES
```

### Wrong CodeFile

Look at:

``` text
loader.py → build_code_file()
models.py
```

### Wrong chunks

Look at:

``` text
text_chunker.py
```

### Embeddings missing

Look at:

``` text
embeddings/service.py
repository_indexer.py
```

### Vectors missing

Look at:

``` text
repository_indexer.py
qdrant.py
Qdrant server
```

### Everything gets re-indexed

Look at:

``` text
indexer.py
metadata.py
storage/index_metadata.json
```

### Old vectors remain after file changes

Look at:

``` text
repository_indexer.py
qdrant.py → delete_file()
```

### Deleted files remain searchable

Look at:

``` text
remove_deleted_files()
qdrant.py
metadata.py
```

------------------------------------------------------------------------

# 24. Important Design Decisions {#24-important-design-decisions}

## Single Responsibility

Each component has one main job.

``` text
Loader       → repositories/files
Chunker      → chunks
Embedding    → vectors
Qdrant       → vector storage
Metadata     → metadata persistence
Indexer      → change detection
RepositoryIndexer
             → one-file pipeline
RepositoryIndexingService
             → repository orchestration
```

## Separation of Concerns

We avoid one giant indexing function.

Instead:

``` text
Loader
Chunker
EmbeddingService
VectorStore
Indexer
```

are independent components.

## Testability

Dependencies can be replaced with mocks.

## Incremental Indexing

Only changed/new files are re-processed.

## Source Metadata Preservation

Every vector keeps enough information to identify its source.

------------------------------------------------------------------------

# 25. Current V1 Limitations {#25-current-v1-limitations}

The following are intentionally deferred:

``` text
Only .txt support
No Python AST parsing
No Markdown-aware chunking
No code-aware chunking
No line-number calculation for text chunks
No chunk overlap
No BM25
No hybrid retrieval
No RRF
No reranking
No relevance gate
No context builder
No LLM generation
```

These are not failures of Part 1. They are boundaries between
versions/parts.

------------------------------------------------------------------------

# 26. Part 1 Mental Model {#26-part-1-mental-model}

Remember this:

``` text
REPOSITORY
    ↓
FILES
    ↓
CodeFile
    ↓
CodeChunk
    ↓
Embedding
    ↓
Qdrant Point
    ↓
Vector Database
```

And separately:

``` text
FILE CONTENT
    ↓
SHA-256 HASH
    ↓
METADATA
    ↓
INDEX / SKIP DECISION
```

These are the two core flows of Part 1.

------------------------------------------------------------------------

# 27. One-Line Revision of Every File {#27-one-line-revision-of-every-file}

``` text
config.py
→ application configuration

models.py
→ data models

validator.py
→ GitHub URL validation

languages.py
→ extension → language mapping

loader.py
→ repository loading + file discovery + CodeFile creation

text_chunker.py
→ text → CodeChunk[]

embeddings/service.py
→ text → vectors

vectorstore/qdrant.py
→ vector storage/search/deletion

indexing/metadata.py
→ indexing metadata persistence

indexing/indexer.py
→ change detection

indexing/repository_indexer.py
→ one-file indexing pipeline

indexing/repository_indexer_service.py
→ whole-repository indexing orchestration

main.py
→ FastAPI application entry point
```

------------------------------------------------------------------------

# 28. Part 1 → Part 2 Boundary {#28-part-1--part-2-boundary}

At the end of Part 1:

``` text
Qdrant
    ↓
vectors
+
chunk content
+
metadata
```

Part 2 starts with:

``` text
USER QUESTION
```

Planned retrieval/generation architecture:

``` text
Question
   ↓
Dense Retrieval
   +
BM25 Retrieval
   ↓
RRF Fusion
   ↓
Cross-Encoder Reranking
   ↓
Relevance Gate
   ↓
Context Builder
   ↓
Prompt Builder
   ↓
Gemini
   ↓
Grounded Answer
```

The relationship is:

``` text
PART 1
Prepare the knowledge
        ↓
      Qdrant
        ↓
PART 2
Find and use the knowledge
```

------------------------------------------------------------------------

# 29. Final Part 1 Checklist {#29-final-part-1-checklist}

You should be able to explain:

-   Why repository URLs are validated
-   How repository IDs are generated
-   Why repository IDs are deterministic
-   Clone vs pull
-   File discovery
-   Ignored directories
-   Supported extensions
-   `Repository`
-   `CodeFile`
-   `CodeStructure`
-   `CodeChunk`
-   Why chunking is needed
-   How `TextChunker` works
-   Why embeddings are needed
-   What the 384 dimensions represent
-   What a Qdrant collection is
-   What a Qdrant point contains
-   Why payload metadata is stored
-   Why cosine distance is configured
-   Why point IDs are deterministic
-   Why metadata JSON exists
-   SHA-256 change detection
-   `should_index()`
-   `mark_indexed()`
-   New file flow
-   Unchanged file flow
-   Changed file flow
-   Deleted file flow
-   Why old vectors are deleted
-   Why metadata is updated after vector storage
-   Difference between `metadata.py` and `indexer.py`
-   Difference between `RepositoryIndexer` and
    `RepositoryIndexingService`
-   Why dependency injection is useful
-   Why mocks are used
-   What the 59 tests cover
-   How to debug each stage

------------------------------------------------------------------------

# 30. Final Summary {#30-final-summary}

Part 1 transforms a GitHub repository into a searchable vector
representation.

The complete transformation is:

``` text
GitHub Repository
       ↓
RepositoryLoader
       ↓
CodeFile
       ↓
TextChunker
       ↓
CodeChunk
       ↓
EmbeddingService
       ↓
Vector
       ↓
Qdrant Point
       ↓
Qdrant
```

At the same time, incremental state is maintained:

``` text
File Content
      ↓
SHA-256
      ↓
Index Metadata
      ↓
New / Unchanged / Changed / Deleted
```

The most important architectural idea is:

> **Part 1 prepares and maintains the knowledge base. Part 2 will
> retrieve the right pieces of that knowledge base and use them to
> answer questions.**

Part 1 is currently considered complete with a green regression suite of
**59/59 tests passing**.
