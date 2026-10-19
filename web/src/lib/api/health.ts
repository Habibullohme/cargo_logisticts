// Backend /api/v1/health javobi. 1-bosqichdan turlar openapi.json dan avtomatik yaratiladi.
export type Health = {
  status: "ok" | "degraded";
  message: string;
  database: "ok" | "error";
  database_message: string;
  server_time: string;
  version: string;
};

const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:8000";

export async function getHealth(): Promise<Health | null> {
  try {
    const res = await fetch(`${API_URL}/api/v1/health`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as Health;
  } catch {
    return null;
  }
}
