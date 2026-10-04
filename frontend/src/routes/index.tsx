import { createFileRoute } from "@tanstack/react-router";
import { Workspace } from "@/components/codelens/Workspace";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "CodeLens AI — Ask your codebase" },
      { name: "description", content: "Index a public GitHub repository and ask natural-language questions with grounded, source-referenced answers." },
      { property: "og:title", content: "CodeLens AI — Ask your codebase" },
      { property: "og:description", content: "AI-powered codebase intelligence with grounded answers and source references." },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: () => (
    <main className="px-4 pb-24 sm:px-6">
      <Workspace />
    </main>
  ),
});
