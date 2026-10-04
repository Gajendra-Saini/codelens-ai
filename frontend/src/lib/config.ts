// Single place to configure the FastAPI backend URL.
// Override at build time with VITE_API_BASE_URL.
export const API_BASE_URL: string =
  (import.meta.env['VITE_API_BASE_URL'] as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000";

export const GITHUB_URL = "https://github.com";
