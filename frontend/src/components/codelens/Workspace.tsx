import { useRef, useState } from "react";
import {
  ApiError,
  indexRepository,
  queryRepository,
  type ApiErrorKind,
  type IndexResponse,
  type QueryResponse,
} from "@/lib/api";
import { Hero } from "./Hero";
import { RepositoryInput } from "./RepositoryInput";
import { ErrorMessage, IndexingStatus, LoadingState } from "./States";
import { RepositoryHeader } from "./RepositoryHeader";
import { QuestionInput } from "./QuestionInput";
import { ExampleQuestions } from "./ExampleQuestions";
import { AnswerCard, QuestionCard } from "./AnswerCard";

const kindOf = (e: unknown): ApiErrorKind => (e instanceof ApiError ? e.kind : "unknown");

export function Workspace() {
  const [repo, setRepo] = useState<{ url: string; data: IndexResponse } | null>(null);
  const [switching, setSwitching] = useState(false);
  const [indexing, setIndexing] = useState(false);
  const [indexError, setIndexError] = useState<ApiErrorKind | null>(null);
  const [justIndexed, setJustIndexed] = useState(false);
  const lastUrl = useRef("");

  const [question, setQuestion] = useState("");
  const [asked, setAsked] = useState<string | null>(null);
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState<QueryResponse | null>(null);
  const [queryError, setQueryError] = useState<ApiErrorKind | null>(null);

  const runIndex = async (url: string) => {
    lastUrl.current = url;
    setIndexing(true);
    setIndexError(null);
    try {
      const data = await indexRepository(url);
      setRepo({ url, data });
      setSwitching(false);
      setJustIndexed(true);
      setAnswer(null);
      setAsked(null);
      setQueryError(null);
      setQuestion("");
    } catch (e) {
      setIndexError(kindOf(e));
    } finally {
      setIndexing(false);
    }
  };

  const runQuery = async (q = question.trim()) => {
    if (!repo || !q) return;
    setAsked(q);
    setAsking(true);
    setAnswer(null);
    setQueryError(null);
    setJustIndexed(false);
    try {
      setAnswer(await queryRepository(repo.data.repository_id, q));
      setQuestion("");
    } catch (e) {
      setQueryError(kindOf(e));
    } finally {
      setAsking(false);
    }
  };

  const indexForm = (
    <div className="space-y-4">
      <RepositoryInput
        key={switching ? "switch" : "initial"}
        loading={indexing}
        initialValue={lastUrl.current}
        onSubmit={runIndex}
        onCancel={repo ? () => { setSwitching(false); setIndexError(null); } : undefined}
      />
      {indexing && (
        <LoadingState label="Indexing repository..." hint="Cloning, chunking and embedding source files." />
      )}
      {indexError && !indexing && <ErrorMessage kind={indexError} onRetry={() => runIndex(lastUrl.current)} />}
    </div>
  );

  if (!repo) {
    return (
      <div className="mx-auto flex max-w-2xl flex-col items-center gap-12 pt-16 sm:pt-24">
        <Hero />
        {indexForm}
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl space-y-8 pt-10">
      {switching ? (
        <div className="panel fade-up p-4 sm:p-5">{indexForm}</div>
      ) : (
        <RepositoryHeader
          repoUrl={repo.url}
          repositoryId={repo.data.repository_id}
          filesFound={repo.data.files_found}
          onChange={() => { setSwitching(true); setIndexError(null); }}
        />
      )}
      {justIndexed && !switching && <IndexingStatus data={repo.data} />}

      <QuestionInput value={question} onChange={setQuestion} onSubmit={() => runQuery()} loading={asking} />

      {!asked && <ExampleQuestions onPick={setQuestion} />}

      {asked && (
        <div className="space-y-4">
          <QuestionCard question={asked} />
          {asking && <LoadingState label="Searching repository..." hint="Retrieving relevant chunks and generating a grounded answer." />}
          {queryError && !asking && <ErrorMessage kind={queryError} onRetry={() => runQuery(asked)} />}
          {answer && !asking && <AnswerCard data={answer} />}
        </div>
      )}
    </div>
  );
}
