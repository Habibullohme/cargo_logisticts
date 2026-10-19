import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { API_URL, getHealth, type Health } from "@/lib/api/health";
import { t } from "@/lib/i18n";

type State = { kind: "loading" } | { kind: "done"; health: Health | null };

function formatTime(iso: string): string {
  // "2026-10-19T09:05:00+05:00" -> "09:05, 19.10.2026" (server allaqachon Toshkent vaqtida)
  const [date, rest] = iso.split("T");
  const [y, m, d] = date.split("-");
  return `${rest.slice(0, 5)}, ${d}.${m}.${y}`;
}

export default function HomeScreen() {
  const [state, setState] = useState<State>({ kind: "loading" });

  const check = useCallback(async () => {
    setState({ kind: "loading" });
    setState({ kind: "done", health: await getHealth() });
  }, []);

  useEffect(() => {
    check();
  }, [check]);

  const health = state.kind === "done" ? state.health : null;
  let tone: keyof typeof tones = "error";
  let statusText = t("home.status_error");
  if (health?.database === "ok") {
    tone = "ok";
    statusText = t("home.status_ok");
  } else if (health) {
    tone = "warn";
    statusText = t("home.status_db_error");
  }

  return (
    <ScrollView contentContainerStyle={styles.page}>
      <Text style={styles.heading}>{t("home.heading")}</Text>
      <Text style={styles.lead}>{t("home.lead")}</Text>

      <View style={[styles.card, state.kind === "done" && tones[tone]]}>
        <Text style={styles.cardTitle}>{t("home.status_title")}</Text>
        {state.kind === "loading" ? (
          <View style={styles.row}>
            <ActivityIndicator />
            <Text style={styles.body}>{t("home.checking")}</Text>
          </View>
        ) : (
          <>
            <Text style={[styles.statusLine, { color: toneColors[tone] }]}>{statusText}</Text>
            {health ? (
              <>
                <Text style={styles.body}>{health.message}</Text>
                <Text style={styles.muted}>
                  {t("home.server_time")}: {formatTime(health.server_time)}
                </Text>
              </>
            ) : (
              <>
                <Text style={styles.body}>{t("home.status_error_hint")}</Text>
                <Text style={styles.muted}>{API_URL}</Text>
              </>
            )}
          </>
        )}
      </View>

      <Pressable
        onPress={check}
        disabled={state.kind === "loading"}
        style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]}
      >
        <Text style={styles.buttonText}>{t("home.retry")}</Text>
      </Pressable>
    </ScrollView>
  );
}

const colors = {
  bg: "#F3F5F8",
  surface: "#FFFFFF",
  ink: "#152033",
  muted: "#586379",
  line: "#D3D9E3",
  accent: "#1D5BB8",
};

const toneColors = { ok: "#1E7A4E", warn: "#9A6200", error: "#B3401F" };

const tones = StyleSheet.create({
  ok: { backgroundColor: "#E1F3E9", borderLeftColor: toneColors.ok },
  warn: { backgroundColor: "#FCF0D8", borderLeftColor: toneColors.warn },
  error: { backgroundColor: "#FBE7E0", borderLeftColor: toneColors.error },
});

const styles = StyleSheet.create({
  page: { flexGrow: 1, backgroundColor: colors.bg, padding: 16, gap: 16 },
  heading: { fontSize: 28, fontWeight: "700", color: colors.ink },
  lead: { fontSize: 17, lineHeight: 25, color: colors.muted },
  card: {
    backgroundColor: colors.surface,
    borderColor: colors.line,
    borderWidth: 1,
    borderLeftWidth: 6,
    borderRadius: 12,
    padding: 16,
    gap: 6,
  },
  cardTitle: { fontSize: 13, fontWeight: "600", letterSpacing: 0.8, color: colors.muted },
  statusLine: { fontSize: 20, fontWeight: "700" },
  body: { fontSize: 16, lineHeight: 23, color: colors.ink },
  muted: { fontSize: 14, color: colors.muted },
  row: { flexDirection: "row", alignItems: "center", gap: 10 },
  button: {
    backgroundColor: colors.accent,
    borderRadius: 12,
    paddingVertical: 18,
    alignItems: "center",
  },
  buttonPressed: { opacity: 0.8 },
  buttonText: { color: "#FFFFFF", fontSize: 18, fontWeight: "700" },
});
