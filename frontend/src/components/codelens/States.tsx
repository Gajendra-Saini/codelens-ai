import { AlertTriangle, CheckCircle2, RotateCcw, SearchX } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ApiErrorKind, IndexResponse } from "@/lib/api";

export function LoadingState({ label, hint }: { label: string; hint?: string }) {
  return (
    <div className="panel fade-up p-5" role="status" aria-live="polite">
      <div className="flex items-center gap-3">
        <span className="relative flex size-2.5">
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-primary/60" />
          <span className="relative inline-flex size-2.5 rounded-full bg-primary" />
        </span>
        <p className="text-sm font-medium">{label}</p>
      </div>
      {hint && <p className="mt-1.5 pl-5.5 text-xs text-muted-foreground">{hint}</p>}
      <div className="mt-4 h-0.5 overflow-hidden rounded-full bg-muted">
        <div className="scan-bar h-full w-1/3 rounded-full bg-primary/70" />
      </div>
    </div>
  );
}

export function IndexingStatus({ data }: { data: IndexResponse }) {
  return (
    <div className="panel fade-up flex items-start gap-3 p-4">
      <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-success" />
      <div className="min-w-0 text-sm">
        <p className="font-medium">Repository indexed successfully</p>
        <p className="mt-1 text-muted-foreground">
          {data.files_found} {data.files_found === 1 ? "file" : "files"} discovered · Ready to answer questions
        </p>
      </div>
    </div>
  );
}

const ERRORS: Record<ApiErrorKind, { title: string; body: string }> = {
  invalid_url: {
    title: "Invalid repository URL",
    body: "Check that the URL points to a public GitHub repository, e.g. https://github.com/user/repo.",
  },
  index_failed: {
    title: "Unable to index repository",
    body: "The repository could not be cloned or processed. Make sure it exists and is public.",
  },
  unavailable: {
    title: "CodeLens backend is unavailable",
    body: "The API could not be reached. Confirm the FastAPI server is running and accessible.",
  },
  unknown: { title: "Something went wrong", body: "An unexpected error occurred. Please try again." },
};

export function ErrorMessage({ kind, onRetry }: { kind: ApiErrorKind; onRetry?: () => void }) {
  const e = ERRORS[kind];
  return (
    <div className="fade-up flex flex-col gap-3 rounded-xl border border-destructive/30 bg-destructive/5 p-4 sm:flex-row sm:items-center">
      <AlertTriangle className="size-4 shrink-0 text-destructive" />
      <div className="flex-1 text-sm">
        <p className="font-medium">{e.title}</p>
        <p className="mt-0.5 text-muted-foreground">{e.body}</p>
      </div>
      {onRetry && (
        <Button variant="outline" size="sm" onClick={onRetry}>
          <RotateCcw className="size-3.5" /> Try again
        </Button>
      )}
    </div>
  );
}

export function InsufficientEvidence() {
  return (
    <div className="fade-up rounded-xl border border-warning/25 bg-warning/5 p-5">
      <div className="flex items-center gap-2.5">
        <SearchX className="size-4 text-warning" />
        <p className="text-sm font-medium">Not enough evidence</p>
      </div>
      <p className="mt-2 text-sm text-muted-foreground">
        CodeLens could not find sufficient evidence in the indexed repository to answer this question.
        Try rephrasing or asking about a specific file or feature.
      </p>
    </div>
  );
}
