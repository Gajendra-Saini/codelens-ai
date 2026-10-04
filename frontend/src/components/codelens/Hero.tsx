export function Hero() {
  return (
    <div className="fade-up text-center">
      <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface/60 px-3 py-1 font-mono text-[11px] text-muted-foreground">
        <span className="size-1.5 rounded-full bg-primary" /> Retrieval-augmented code search
      </span>
      <h1 className="text-gradient mt-6 text-4xl font-semibold tracking-tight sm:text-5xl md:text-6xl md:leading-[1.05]">
        Ask your codebase.
        <br />
        Understand your codebase.
      </h1>
      <p className="mx-auto mt-5 max-w-md text-base text-muted-foreground">
        Connect a GitHub repository and explore your codebase using natural language.
      </p>
    </div>
  );
}
