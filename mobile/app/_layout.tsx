import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { t } from "@/lib/i18n";

export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ title: t("app.title") }} />
    </>
  );
}
