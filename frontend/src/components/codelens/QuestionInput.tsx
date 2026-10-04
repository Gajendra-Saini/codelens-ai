import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { CornerDownLeft, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const PLACEHOLDERS = [
  "Where is authentication handled?",
  "How does payment retry work?",
  "Which files handle database operations?",
  "Where is error handling implemented?",
];

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  loading: boolean;
}

export function QuestionInput({ value, onChange, onSubmit, loading }: Props) {
  const [ph, setPh] = useState(0);
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    const t = setInterval(() => setPh((p) => (p + 1) % PLACEHOLDERS.length), 3500);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (value) ref.current?.focus();
  }, [value]);

  const onKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !loading) onSubmit();
    }
  };

  return (
    <div>
      <h2 className="mb-3 text-lg font-semibold tracking-tight">What do you want to understand?</h2>
      <div className="panel p-2 transition-colors focus-within:border-primary/40">
        <textarea
          ref={ref}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={onKey}
          rows={3}
          placeholder={PLACEHOLDERS[ph]}
          className="w-full resize-none bg-transparent px-3 py-2.5 text-[15px] leading-relaxed outline-none placeholder:text-muted-foreground/60"
        />
        <div className="flex items-center justify-between gap-2 px-2 pb-1">
          <span className="hidden items-center gap-1.5 text-xs text-muted-foreground sm:inline-flex">
            <kbd className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px]">Enter</kbd> to ask ·
            <kbd className="rounded border border-border px-1.5 py-0.5 font-mono text-[10px]">Shift + Enter</kbd> new line
          </span>
          <Button onClick={onSubmit} disabled={loading || !value.trim()} className="ml-auto">
            {loading ? <Loader2 className="size-4 animate-spin" /> : <Sparkles className="size-4" />}
            Ask CodeLens
            {!loading && <CornerDownLeft className="size-3.5 opacity-60" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
