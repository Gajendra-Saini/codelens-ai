import { Check, Copy, RefreshCw } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";

interface Props {
  repoUrl: string;
  repositoryId: string;
  filesFound: number;
  onChange: () => void;
}

export function RepositoryHeader({ repoUrl, repositoryId, filesFound, onChange }: Props) {
  const [copied, setCopied] = useState(false);
  const display = repoUrl.replace(/^https?:\/\//, "").replace(/\.git$/, "").replace(/\/$/, "");

  const copy = async () => {
    await navigator.clipboard?.writeText(repositoryId);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };

  return (
    <div className="panel fade-up flex flex-col gap-4 p-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="min-w-0">
        <p className="text-[11px] font-medium uppercase tracking-wider text-muted-foreground">Repository</p>
        <p className="mt-1 truncate font-mono text-sm">{display}</p>
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1 text-success">
            <Check className="size-3" /> Indexed
          </span>
          <span>{filesFound} files</span>
          <button
            onClick={copy}
            className="inline-flex items-center gap-1 font-mono transition-colors hover:text-foreground"
            title="Copy repository ID"
          >
            id {repositoryId.slice(0, 8)}…
            {copied ? <Check className="size-3" /> : <Copy className="size-3" />}
          </button>
        </div>
      </div>
      <Button variant="outline" size="sm" onClick={onChange} className="self-start sm:self-center">
        <RefreshCw className="size-3.5" /> Change repository
      </Button>
    </div>
  );
}
