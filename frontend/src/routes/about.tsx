import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About — CodeLens AI" },
      { name: "description", content: "How CodeLens AI indexes repositories and generates grounded answers using retrieval-augmented generation." },
      { property: "og:title", content: "About — CodeLens AI" },
      { property: "og:description", content: "How CodeLens AI turns a GitHub repository into a searchable knowledge base." },
      { property: "og:type", content: "article" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: About,
});

const STEPS = [
  ["01", "Index", "The repository is cloned, split into structure-aware chunks, and embedded into a vector index."],
  ["02", "Retrieve", "Your question is embedded and matched against the most relevant chunks in the repository."],
  ["03", "Answer", "An LLM generates an answer grounded only in the retrieved evidence, with sources attached."],
  ["04", "Refuse", "When the evidence is insufficient, CodeLens says so rather than guessing."],
];

function About() {
  return (
    <main className="mx-auto max-w-3xl px-4 pb-24 pt-16 sm:px-6">
      <p className="font-mono text-xs text-primary">About</p>
      <h1 className="text-gradient mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
        Grounded answers about real code.
      </h1>
      <p className="mt-4 max-w-xl text-muted-foreground">
        CodeLens AI is a retrieval-augmented system for understanding unfamiliar codebases. A React frontend talks to a
        FastAPI backend that handles indexing, retrieval and generation.
      </p>
      <div className="mt-12 grid gap-3 sm:grid-cols-2">
        {STEPS.map(([n, t, d]) => (
          <div key={n} className="panel p-5">
            <span className="font-mono text-xs text-muted-foreground">{n}</span>
            <h2 className="mt-2 font-semibold">{t}</h2>
            <p className="mt-1.5 text-sm text-muted-foreground">{d}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
