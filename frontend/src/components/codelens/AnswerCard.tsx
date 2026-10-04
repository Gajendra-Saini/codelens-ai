import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { MessageSquare, ScanSearch } from "lucide-react";
import type { QueryResponse } from "@/lib/api";
import { InsufficientEvidence } from "./States";
import { SourcesList } from "./SourcesList";

export function QuestionCard({ question }: { question: string }) {
  return (
    <div className="fade-up flex items-start gap-3 rounded-lg border border-border bg-surface/60 px-4 py-3">
      <MessageSquare className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
      <p className="text-sm break-words">{question}</p>
    </div>
  );
}

export function AnswerCard({ data }: { data: QueryResponse }) {
  return (
    <div className="fade-up space-y-8">
      {data.sufficient ? (
        <section className="panel p-5 sm:p-6">
          <div className="mb-4 flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            <ScanSearch className="size-3.5 text-primary" /> CodeLens Answer
          </div>
          <div className="prose-answer text-[15px] break-words">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.answer}</ReactMarkdown>
          </div>
        </section>
      ) : (
        <InsufficientEvidence />
      )}
      {data.results?.length > 0 && <SourcesList results={data.results} />}
    </div>
  );
}
