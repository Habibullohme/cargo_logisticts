import type { Metadata, Viewport } from "next";
import { t } from "@/lib/i18n";
import "./globals.css";

export const metadata: Metadata = {
  title: t("site.title"),
  description: t("site.description"),
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="uz">
      <body>{children}</body>
    </html>
  );
}
