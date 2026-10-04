import { Link } from "@tanstack/react-router";
import { Github, ScanSearch } from "lucide-react";
import { GITHUB_URL } from "@/lib/config";

export function Navbar() {
  return (
    <header className="sticky top-0 z-20 border-b border-border bg-background/70 backdrop-blur-md">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:px-6">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="grid size-7 place-items-center rounded-md border border-border bg-surface">
            <ScanSearch className="size-4 text-primary" />
          </span>
          <span className="flex items-baseline gap-2">
            <span className="text-sm font-semibold tracking-tight">CodeLens AI</span>
            <span className="hidden text-xs text-muted-foreground sm:inline">
              AI-powered codebase intelligence
            </span>
          </span>
        </Link>
        <nav className="flex items-center gap-1 text-sm">
          <Link
            to="/"
            className="rounded-md px-3 py-1.5 text-muted-foreground transition-colors hover:text-foreground"
            activeProps={{ className: "text-foreground" }}
            activeOptions={{ exact: true }}
          >
            CodeLens
          </Link>
          <Link
            to="/about"
            className="rounded-md px-3 py-1.5 text-muted-foreground transition-colors hover:text-foreground"
            activeProps={{ className: "text-foreground" }}
          >
            About
          </Link>
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noreferrer"
            aria-label="GitHub"
            className="rounded-md p-2 text-muted-foreground transition-colors hover:text-foreground"
          >
            <Github className="size-4" />
          </a>
        </nav>
      </div>
    </header>
  );
}
