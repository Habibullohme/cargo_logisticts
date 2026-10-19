// Backend /api/v1/health javobi. 1-bosqichdan turlar openapi.json dan avtomatik yaratiladi.
export type Health = {
  status: "ok" | "degraded";
  message: string;
  database: "ok" | "error";
  database_message: string;
  server_time: string;
  version: string;
};

export const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000";

export async function getHealth(): Promise<Health | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 8000);
  try {
    const res = await fetch(`${API_URL}/api/v1/health`, { signal: controller.signal });
    if (!res.ok) return null;
    return (await res.json()) as Health;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}
