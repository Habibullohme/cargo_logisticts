import { getHealth } from "@/lib/api/health";
import { t } from "@/lib/i18n";

// Har safar ochilganda backenddan yangi holat olinadi.
export const dynamic = "force-dynamic";

function formatTime(iso: string): string {
  return new Intl.DateTimeFormat("uz-UZ", {
    timeZone: "Asia/Tashkent",
    hour: "2-digit",
    minute: "2-digit",
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  }).format(new Date(iso));
}

export default async function HomePage() {
  const health = await getHealth();

  let tone: "ok" | "warn" | "error" = "error";
  let statusText = t("home.status_error");
  if (health?.database === "ok") {
    tone = "ok";
    statusText = t("home.status_ok");
  } else if (health) {
    tone = "warn";
    statusText = t("home.status_db_error");
  }

  return (
    <main className="page">
      <header className="brand">{t("site.title")}</header>

      <section className="hero">
        <h1>{t("home.heading")}</h1>
        <p>{t("home.lead")}</p>
      </section>

      <section className={`status status-${tone}`} aria-live="polite">
        <h2>{t("home.status_title")}</h2>
        <p className="status-line">{statusText}</p>
        {health && <p>{health.message}</p>}
        {health && (
          <p className="muted">
            {t("home.server_time")}: {formatTime(health.server_time)}
          </p>
        )}
      </section>
    </main>
  );
}
