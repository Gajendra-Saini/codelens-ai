import { useState } from "react";
import { ChevronDown, FileCode2 } from "lucide-react";
import type { QueryResult } from "@/lib/api";
import { cn } from "@/lib/utils";

export function SourcesList({ results }: { results: QueryResult[] }) {
  return (
    <section>
      <h3 className="text-sm font-semibold">Sources</h3>
      <p className="mt-0.5 text-xs text-muted-foreground">Repository evidence used to generate this answer.</p>
      <div className="mt-4 space-y-2">
        {results.map((r, i) => (
          <SourceCard key={i} index={i + 1} result={r} defaultOpen={i === 0} />
        ))}
      </div>
    </section>
  );
}

export function SourceCard({
  index,
  result,
  defaultOpen,
}: {
  index: number;
  result: QueryResult;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(!!defaultOpen);
  const { chunk } = result;
  const pct = Math.round(Math.max(0, Math.min(1, result.score)) * 100);
  const hasLines = chunk.start_line != null && chunk.end_line != null && chunk.end_line > 0;

  return (
    <div className="overflow-hidden rounded-lg border border-border bg-surface/60 transition-colors hover:border-foreground/15">
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        <span className="font-mono text-[10px] font-medium tracking-wider text-muted-foreground">
          SOURCE {index}
        </span>
        <FileCode2 className="size-3.5 shrink-0 text-muted-foreground" />
        <span className="min-w-0 flex-1 truncate font-mono text-sm">
          {chunk.path}
          {hasLines && (
            <span className="text-muted-foreground">
              :{chunk.start_line}-{chunk.end_line}
            </span>
          )}
        </span>
        <span className="hidden items-center gap-2 sm:flex">
          <span className="h-1 w-14 overflow-hidden rounded-full bg-muted">
            <span className="block h-full rounded-full bg-primary" style={{ width: `${pct}%` }} />
          </span>
          <span className="w-24 text-right text-xs text-muted-foreground">Relevance {pct}%</span>
        </span>
        <span className="text-xs text-muted-foreground sm:hidden">{pct}%</span>
        <ChevronDown className={cn("size-4 shrink-0 text-muted-foreground transition-transform", open && "rotate-180")} />
      </button>
      <div className={cn("grid transition-all duration-200", open ? "grid-rows-[1fr]" : "grid-rows-[0fr]")}>
        <div className="overflow-hidden">
          <div className="border-t border-border px-4 py-3">
            {(chunk.language || chunk.structure_type || chunk.name) && (
              <div className="mb-2 flex flex-wrap gap-1.5">
                {[chunk.language, chunk.structure_type, chunk.parent ? `${chunk.parent}.${chunk.name}` : chunk.name]
                  .filter(Boolean)
                  .map((t, i) => (
                    <span key={i} className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground">
                      {t}
                    </span>
                  ))}
              </div>
            )}
            <pre className="max-h-72 overflow-auto whitespace-pre-wrap break-words rounded-md bg-background/60 p-3 font-mono text-xs leading-relaxed text-muted-foreground">
              {chunk.content}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
