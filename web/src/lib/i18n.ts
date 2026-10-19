// Sayt matnlari. Hozir faqat o'zbek lotin; keyin uz_cyrl va ru qo'shiladi.
import uzLatn from "@/locales/uz_latn.json";

type Key = keyof typeof uzLatn;

const locales = { uz_latn: uzLatn } as const;

export function t(key: Key, locale: keyof typeof locales = "uz_latn"): string {
  return locales[locale][key] ?? key;
}
