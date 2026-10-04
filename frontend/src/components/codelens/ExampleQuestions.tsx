import { Boxes, Database, FlaskConical, KeyRound } from "lucide-react";

const EXAMPLES = [
  { label: "Authentication", q: "Where is authentication handled?", icon: KeyRound },
  { label: "Database", q: "How are database connections managed?", icon: Database },
  { label: "Testing", q: "Which files contain tests?", icon: FlaskConical },
  { label: "Architecture", q: "How is the application structured?", icon: Boxes },
];

export function ExampleQuestions({ onPick }: { onPick: (q: string) => void }) {
  return (
    <div className="fade-up">
      <p className="mb-3 text-xs font-medium text-muted-foreground">Try asking</p>
      <div className="grid gap-2 sm:grid-cols-2">
        {EXAMPLES.map(({ label, q, icon: Icon }) => (
          <button
            key={label}
            onClick={() => onPick(q)}
            className="group rounded-lg border border-border bg-surface/60 p-3.5 text-left transition-all hover:border-primary/30 hover:bg-surface"
          >
            <span className="flex items-center gap-2 text-xs font-medium text-muted-foreground group-hover:text-primary">
              <Icon className="size-3.5" /> {label}
            </span>
            <span className="mt-1.5 block text-sm">“{q}”</span>
          </button>
        ))}
      </div>
    </div>
  );
}
