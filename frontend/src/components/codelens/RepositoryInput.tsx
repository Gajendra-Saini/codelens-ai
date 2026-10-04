import { useState, type FormEvent } from "react";
import { ArrowRight, Github, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  loading: boolean;
  initialValue?: string;
  onSubmit: (url: string) => void;
  onCancel?: (() => void) | undefined;
}

export function RepositoryInput({ loading, initialValue = "", onSubmit, onCancel }: Props) {
  const [url, setUrl] = useState(initialValue);
  const [touched, setTouched] = useState(false);
  const empty = url.trim().length === 0;

  const submit = (e: FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (empty || loading) return;
    onSubmit(url.trim());
  };

  return (
    <form onSubmit={submit} className="w-full">
      <label htmlFor="repo" className="mb-2 block text-left text-xs font-medium text-muted-foreground">
        GitHub Repository
      </label>
      <div className="panel flex flex-col gap-2 p-2 sm:flex-row sm:items-center">
        <div className="flex flex-1 items-center gap-2.5 px-2">
          <Github className="size-4 shrink-0 text-muted-foreground" />
          <input
            id="repo"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            placeholder="https://github.com/username/repository"
            autoComplete="off"
            spellCheck={false}
            className="h-10 w-full min-w-0 bg-transparent font-mono text-sm outline-none placeholder:text-muted-foreground/60 disabled:opacity-60"
          />
        </div>
        <div className="flex gap-2">
          {onCancel && (
            <Button type="button" variant="ghost" onClick={onCancel} disabled={loading} className="h-10">
              Cancel
            </Button>
          )}
          <Button type="submit" disabled={loading} className="h-10 flex-1 px-4 sm:flex-none">
            {loading ? <Loader2 className="size-4 animate-spin" /> : <ArrowRight className="size-4" />}
            {loading ? "Indexing…" : "Index Repository"}
          </Button>
        </div>
      </div>
      <p className="mt-2.5 text-left text-xs text-muted-foreground">
        {touched && empty ? (
          <span className="text-destructive">Enter a GitHub repository URL to continue.</span>
        ) : (
          "Public GitHub repositories only"
        )}
      </p>
    </form>
  );
}
