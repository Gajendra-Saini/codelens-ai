import { API_BASE_URL } from "./config";

export interface IndexFileResult {
  status: string;
  path: string;
  chunks?: number;
}
export interface IndexResponse {
  repository_id: string;
  files_found: number;
  results: IndexFileResult[];
  deleted_files: string[];
}
export interface SourceChunk {
  content: string;
  path: string;
  language: string | null;
  structure_type: string | null;
  name: string | null;
  parent: string | null;
  start_line: number | null;
  end_line: number | null;
}
export interface QueryResult {
  id: [string, number] | unknown;
  score: number;
  chunk: SourceChunk;
}
export interface QueryResponse {
  answer: string;
  sufficient: boolean;
  results: QueryResult[];
}

export type ApiErrorKind = "invalid_url" | "index_failed" | "unavailable" | "unknown";

export class ApiError extends Error {
  constructor(public kind: ApiErrorKind, public detail?: string) {
    super(kind);
  }
}

async function post<T>(path: string, body: unknown, failKind: ApiErrorKind): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError("unavailable");
  }
  if (!res.ok) {
    let detail: string | undefined;
    try {
      const data = await res.json();
      detail = typeof data?.detail === "string" ? data.detail : undefined;
    } catch {
      /* ignore */
    }
    if (res.status === 422 || /invalid.*url|url.*invalid/i.test(detail ?? "")) {
      throw new ApiError("invalid_url", detail);
    }
    if (res.status >= 502 && res.status <= 504) throw new ApiError("unavailable", detail);
    throw new ApiError(failKind, detail);
  }
  return (await res.json()) as T;
}

export const indexRepository = (repo_url: string) =>
  post<IndexResponse>("/repositories/index", { repo_url }, "index_failed");

export const queryRepository = (repository_id: string, question: string) =>
  post<QueryResponse>("/query", { repository_id, question }, "unknown");
