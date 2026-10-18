# Loyiha: Yuk tashish platformasi (butun O'zbekiston bozorlari bo'ylab)

Sen tajribali dasturchisan va men bilan birga ishlaysan. Men (Habibullo) dasturlashda boshlang'ich darajadaman, shuning uchun har bir bosqichdan keyin nima qilganingni oddiy o'zbek tilida tushuntir. Men loyihani **Ubuntu (Linux)** da ishlab chiqaman — u tashqi SSD'ga o'rnatilgan. Menga beradigan barcha buyruqlar Ubuntu terminali (bash) uchun bo'lsin. Kompyuterimda Windows ham bor, lekin ishlab chiqish va deploy Linux'da bo'ladi, chunki server ham Linux.

Birinchi ish: shu promptni loyiha ildiziga `CLAUDE.md` qilib saqla, keyingi sessiyalarda ham kontekst yo'qolmasin.

---

## 1. Muammo va g'oya

O'zbekistonda yuk mashinalari (asosan Isuzu) va yuk egalarini bog'laydigan qulay tizim yo'q. Hozir hammasi qo'lda: Telegram guruhlardagi e'lonlar va dispetcherlar orqali. Masalan, Namangandan yuk olib keladigan mashhur odam o'zida mashina yo'q, buyurtmalarni yig'ib, tanish isuzichilarga beradi va o'rtadan pul oladi. Natija: qimmat, yuklar ezilib keladi, kim aybdorligi noma'lum.

Yandex Go taksida qilgan ishni yuk tashishda qilmoqchimiz: **yuk egasi o'zi mashina topadi, isuzichi o'zi yuk topadi, hammasi avtomatlashgan.**

### Bozorning o'ziga xosligi (juda muhim)
- Bu **yig'ma yuk (LTL / "sborniy")** bozori: bitta isuziga 20–30 ta savdogarning 5–10 qop/korobka yuki yig'iladi. Butun mashinani bitta odam yollashi kam.
- Narx **qop/korobka soni bo'yicha** belgilanadi, kilometr bo'yicha emas.
- Boshlang'ich soha: **faqat oyoq kiyim savdosi**.
- Platforma **butun O'zbekiston bozorlari bo'ylab** ishlashi kerak: istalgan viloyat, shahar, bozor va yo'nalish. Shuning uchun hech bir shahar, bozor yoki yo'nalish kodga yozib qo'yilmaydi — hammasi bazada saqlanadi va admin qo'shadi.
- Birinchi bo'lib bazaga kiritiladigan yo'nalishlar (sinov uchun): Namangan → Toshkent; Andijon / Shahrixon / Marg'ilon / Qo'qon → Toshkent; Toshkent → Buxoro, Xorazm. Keyin qolgan viloyatlar, keyinroq xalqaro.
- Mashinalar Toshkentdan vodiyga **yarim bo'sh qaytadi** — bu bo'sh joyni arzonroq sotish muhim funksiya.
- Haydovchilar ko'pincha **qaysi bozorga, qaysi darvoza/yuk tushirish joyiga** borishni bilmaydi (Chorsu, Abu Saxiy va h.k.).

---

## 2. Foydalanuvchilar (rollar)

1. **Yuk yuboruvchi** — bozor savdogari (oyoq kiyimchi).
2. **Haydovchi (isuzichi)** — mashina egasi yoki haydovchi.
3. **Qabul qiluvchi** — yukni oladigan savdogar. Bu to'liq huquqli rol: u o'ziga kelayotgan barcha yuklarni kuzatib turadi (3.11-bo'lim). Ro'yxatdan o'tmagan bo'lsa ham kuzatish havolasi orqali yukini ko'ra oladi. Bitta odam ham yuboruvchi, ham qabul qiluvchi bo'lishi mumkin.
4. **Admin / operator** — platforma xodimi: haydovchilarni tekshiradi, tariflarni belgilaydi, bahslarni hal qiladi.

---

## 3. Birinchi versiya: Telegram bot + veb-sayt + mobil ilova

Boshidanoq uchta mijoz ilova yaratamiz: **Telegram bot**, **veb-sayt** va **mobil ilova**. Uchalasi bitta umumiy **backend API** va bitta bazaga ulanadi. Barcha biznes mantiq (narx hisoblash, moslashtirish, holatlar) faqat backendda bo'ladi; bot, sayt va ilova faqat ko'rsatadi va API'ga so'rov yuboradi. Bitta funksiya bir marta yoziladi, uchala joyda ishlaydi.

- **Telegram bot** — bozor savdogarlari va haydovchilar uchun eng oson kirish yo'li.
- **Veb-sayt** — yuk yuboruvchilar uchun kabinet + admin panel (haydovchilarni tekshirish, tariflar, bozor xaritasi, bahslar, statistika).
- **Mobil ilova** — asosan haydovchilar uchun (rasm olish, buyurtmalar, reyslar); avval Android, keyin iOS.
- Bitta foydalanuvchi bitta akkaunt bilan uchala joydan ham kira oladi.

### Texnologiyalar (taklif, agar jiddiy sabab bo'lsa o'zgartirishni menga tushuntirib taklif qil)
- **Backend API:** Python 3.12, **FastAPI**, biznes mantiq alohida `services/` qatlamida
- **Baza:** **PostgreSQL**, SQLAlchemy 2 + Alembic (migratsiyalar)
- **Telegram bot:** **aiogram 3**; bazaga to'g'ridan-to'g'ri emas, backend API orqali ishlaydi
- **Veb-sayt:** Next.js (TypeScript), telefonda ham qulay ko'rinadigan (responsive)
- **Mobil ilova:** React Native (Expo, TypeScript), avval Android
- **Kirish (login):** Telegram orqali — saytda Telegram Login, ilovada bot yuborgan bir martalik kod. Shunda boshida pullik SMS kerak emas.
- Bitta repozitoriy (monorepo): `backend/`, `bot/`, `web/`, `mobile/`, `docs/`
- Docker Compose (lokal ishga tushirish va deploy uchun)
- Barcha matnlar uchun i18n tuzilmasi (hozir faqat o'zbek lotin, keyin kirill va rus qo'shiladi)
- Testlar: pytest (backend)

### Funksiyalar

**3.1. Ro'yxatdan o'tish**
- Telefon raqami Telegram "kontakt yuborish" tugmasi orqali.
- Rol tanlash: yuk yuboruvchi yoki haydovchi.
- Haydovchi uchun qo'shimcha: ism, mashina raqami, mashina turi, sig'imi (taxminiy qop/korobka soni), ishlaydigan yo'nalishlari, hujjat rasmlari (haydovchilik guvohnomasi, texpasport, **yuk tashish litsenziya varaqasi**).
- Haydovchi holati: `tekshirilmoqda` → `tasdiqlangan` / `rad etilgan` / `bloklangan`. Admin tasdiqlamaguncha buyurtma ololmaydi.

**3.2. Tariflar**
- Admin har bir yo'nalish uchun narxni belgilaydi: 1 qop/korobka uchun narx (so'mda). Qaytish reysi uchun alohida (arzonroq) tarif.
- Buyurtma berishda narx avtomatik hisoblanadi va yuboruvchiga oldindan ko'rsatiladi.

**3.3. Buyurtma (yuk yuboruvchi)**
- Qayerdan (shahar + bozor), qayerga (shahar + bozor + yuk tushirish joyi).
- Qop/korobka soni, yuk turi (hozircha "oyoq kiyim"), taxminiy yuk qiymati.
- Qabul qiluvchining ismi va telefoni.
- Sana (bugun / ertaga / tanlangan kun).
- Kim to'laydi: yuboruvchi yoki qabul qiluvchi. To'lov usuli: hozircha naqd (keyin Click/Payme).
- "Yukni sug'urtalash" belgisi (hozircha faqat belgi saqlanadi, integratsiya keyin).
- Izoh.

**3.4. Reys (haydovchi)**
- Haydovchi reys e'lon qiladi: yo'nalish, sana, bo'sh joy (qop/korobka soni), qaytish reysimi yoki yo'q.
- **Moslashtirish:** bir xil yo'nalish va sanadagi buyurtmalar haydovchiga taklif qilinadi, sig'imdan oshmasligi kerak. Bitta reysga ko'p buyurtma yig'iladi.
- Haydovchi buyurtmani qabul qiladi yoki rad etadi. Yuboruvchiga haydovchi ma'lumotlari (ism, mashina raqami, reyting, telefon) yuboriladi.

**3.5. Buyurtma holatlari va dalil tizimi** (yuk ezilishi/yo'qolishi bahslarini hal qilish uchun eng muhim qism)
- Holatlar: `yangi` → `haydovchi_tayinlandi` → `yuk_olindi` → `yolda` → `yetkazildi` → `yakunlandi`; yana `bekor_qilindi` va `bahs`.
- `yuk_olindi`: haydovchi yukning **rasmini** yuklaydi va joy sonini tasdiqlaydi; yuboruvchi ham tasdiqlaydi.
- `yetkazildi`: haydovchi rasm yuklaydi + **qabul qiluvchidan 4 xonali kod** kiritadi. Kod yuboruvchiga beriladi, u qabul qiluvchiga aytadi (keyin SMS orqali yuboriladi).
- Har bir holat o'zgarishi vaqt va kim o'zgartirgani bilan tarixga (audit log) yoziladi.
- Har bir tomon "Muammo bor" tugmasi bilan bahs ochishi mumkin (rasm + izoh) — admin ko'radi.

**3.6. Reyting va qora ro'yxat**
- Yakunlangan buyurtmadan keyin ikki tomon ham 1–5 baho va izoh qoldiradi.
- Admin foydalanuvchini bloklashi mumkin.

**3.7. Bozor xaritasi**
- Admin bozorlar va yuk tushirish joylarini kiritadi: nomi, shahar, darvoza/zona, koordinata (lat/lon), izoh ("2-darvoza, ertalab 6 dan 9 gacha" kabi).
- Haydovchiga buyurtma tayinlanganda tushirish joyi botda Telegram **lokatsiya** xabari, ilova va saytda esa xaritada belgi sifatida ko'rsatiladi ("Navigatorda ochish" tugmasi bilan).

**3.8. Bekor qilish**
- Kim, qachon bekor qila oladi; sababi saqlanadi. Jarima qoidalari hozircha faqat sozlama sifatida (summa 0), keyin yoqiladi.

**3.9. Admin**
- Asosiy admin panel **veb-saytda**: haydovchilarni tasdiqlash (hujjat rasmlari bilan), tariflarni o'zgartirish, shahar/bozor/yo'nalish va yuk tushirish joylarini qo'shish (xaritada belgilab), bahslarni ko'rish, foydalanuvchini bloklash, statistika (kunlik buyurtmalar, reyslar).
- Botda faqat tezkor admin buyruqlari (yangi haydovchi tushganda xabar, bir tugma bilan tasdiqlash). Adminlar ro'yxati bazada, birinchi admin `.env` da.

**3.10. Bildirishnomalar**
- Har bir holat o'zgarishida tegishli tomonlarga (yuboruvchi, qabul qiluvchi, haydovchi) xabar: Telegram bot orqali va mobil ilovada push-bildirishnoma. Bildirishnoma yuborish backendda bitta joyda bo'lsin.

**3.11. Yukni kuzatish — qabul qiluvchi uchun (eng muhim funksiyalardan biri)**

Bugun savdogarning eng katta muammosi: unga Namangandan yuk yuborilgan, lekin yuk qayerda, qachon keladi, nechta pachka ekanini bilmaydi va haydovchiga qayta-qayta qo'ng'iroq qiladi. Tizim buni to'liq hal qilishi kerak.

- **"Menga kelayotgan yuklar"** sahifasi (bot, sayt, ilovada): qabul qiluvchining telefon raqamiga bog'langan barcha yuklar ro'yxati. Yuboruvchi buyurtmada qabul qiluvchi raqamini kiritgani bilan yuk avtomatik shu ro'yxatga tushadi.
- Har bir yuk bo'yicha ko'rinadi:
    - kimdan va qayerdan yuborilgan;
    - **nechta pachka/qop/korobka** — yuborilganda e'lon qilingan son va haydovchi yuk olganda tasdiqlagan son (farq bo'lsa ogohlantirish);
    - yuk olingandagi rasm;
    - hozirgi holat va holatlar tarixi (vaqti bilan);
    - **mashina hozir qayerda** — xaritada (haydovchining oxirgi joylashuvi va qachon yangilangani);
    - **taxminiy yetib kelish vaqti** (yo'nalishning o'rtacha davomiyligi + mashinaning hozirgi joyi asosida; oddiy hisob bilan boshlanadi);
    - haydovchi ismi, mashina raqami, telefoni;
    - qabul qilish kodi (yukni olganda haydovchiga aytiladi).
- **Kuzatish havolasi:** har bir yuk uchun maxsus, taxmin qilib bo'lmaydigan havola (login talab qilmaydi). Yuboruvchi uni qabul qiluvchiga yuboradi. Havolada shaxsiy ma'lumotlar minimal: telefonlar qisman yashirilgan.
- **Haydovchi joylashuvi:** mobil ilovada reys davomida joylashuv avtomatik yuboriladi (masalan, har 2–5 daqiqada, batareyani tejagan holda). Bot orqali ishlovchi haydovchilar Telegram "jonli lokatsiya" ulashadi. Reys tugagach joylashuv kuzatilmaydi va bu haydovchiga oldindan aniq aytiladi (rozilik).
- **Bildirishnomalar qabul qiluvchiga:** yuk yuborildi, yuk mashinaga ortildi (pachka soni bilan), yo'lga chiqdi, shaharga kirdi, ~30 daqiqada yetib keladi, yetkazildi.

---

## 4. Majburiy texnik va qonuniy talablar

- **Ma'lumotlar O'zbekistonda saqlanadi.** O'zbekiston qonuniga ko'ra fuqarolarning shaxsiy ma'lumotlari (ism, telefon, hujjatlar) jismonan O'zbekistondagi serverlarda saqlanishi shart. Shuning uchun:
  - Baza va yuklangan rasmlar bizning serverimizda (deploy O'zbekistondagi hosting/data-markazga mo'ljallangan).
  - Shaxsiy ma'lumotlarni chet eldagi bulutli xizmatlarga (Supabase, Firebase, AWS va h.k.) yuborma.
  - Rasmlar uchun saqlash qatlami alohida modul bo'lsin (hozir lokal disk, keyin O'zbekistondagi S3-mos saqlash).
- Hujjat rasmlari (pasport, guvohnoma, litsenziya) faqat adminlarga ko'rinadi.
- Barcha maxfiy kalitlar `.env` da; `.env` gitga tushmaydi, `.env.example` bor.
- Bazani zaxiralash (backup) skripti va qo'llanmasi.
- Pul summalari butun son (so'm) sifatida saqlanadi, float emas.
- Vaqt zonasi: Asia/Tashkent.

---

## 5. Hozir QILINMAYDI (keyingi versiyalar, lekin arxitektura bunga tayyor bo'lsin)

- iOS versiyasi (App Store)
- Click/Payme orqali to'lov va haydovchiga tez to'lov
- Sug'urta kompaniyasi bilan integratsiya
- SMS orqali kod yuborish (mahalliy SMS provayder)
- Telefon orqali buyurtma: AI ovozli dispetcher (qo'ng'iroq qilib "qayerdan, qayerga, nechta qop" deydi va buyurtma tushadi)
- Yetib kelish vaqtini tirbandlik va tarixiy ma'lumotlar asosida aniqroq (AI bilan) bashorat qilish
- Litsenziyani davlat tizimlari orqali avtomatik tekshirish
- Boshqa sohalar va xalqaro yo'nalishlar

---

## 6. Ish tartibi (bosqichma-bosqich)

Har bir bosqich oxirida **to'xta**, menga nima qilinganini oddiy tilda tushuntir, qanday sinab ko'rishni (Ubuntu terminali buyruqlari bilan) ko'rsat va keyingi bosqichga o'tish uchun ruxsat so'ra.

Har bir funksiya bosqichida tartib bir xil: **avval backend API + testlar, keyin bot, keyin sayt, keyin mobil ilova.** Bitta mijoz tayyor bo'lmasa, keyingisiga o'tma.

- **A-bosqich — Arxitektura (hech qanday kod yozishdan OLDIN):** `docs/architecture.md` faylida loyiha tuzilmasini **Mermaid diagrammalari** bilan chizib chiq (GitHub va VS Code'da rasm bo'lib ko'rinadi). Har bir diagramma ostida 2–3 gapda oddiy o'zbek tilida tushuntirish bo'lsin:
    1. **Umumiy tizim sxemasi:** bot, sayt, mobil ilova → backend API → PostgreSQL, fayl (rasm) saqlash, bildirishnoma xizmati, joylashuv qabul qilish; nima nimaga ulanadi.
    2. **Ma'lumotlar bazasi sxemasi (ER-diagramma):** barcha jadvallar, asosiy maydonlar va bog'lanishlar (foydalanuvchi, rol, haydovchi hujjatlari, mashina, shahar, bozor, yuk tushirish joyi, yo'nalish, tarif, buyurtma, reys, joylashuv nuqtalari, holatlar tarixi, rasm, baho, bahs, bildirishnoma).
    3. **Buyurtma holatlari diagrammasi (state machine):** barcha holatlar, o'tishlar, har bir o'tishni kim qila oladi.
    4. **Asosiy jarayonlar (sequence diagram):** buyurtma berish → moslashtirish → yuk olish → yo'l (joylashuv yangilanishi) → yetkazish va kod bilan tasdiqlash; qabul qiluvchining yukni kuzatishi.
    5. **Papka tuzilmasi:** monorepodagi har bir papka nima uchun.
    6. **Deploy sxemasi:** O'zbekistondagi serverda nima qayerda ishlaydi, zaxira qanday olinadi.

  Shu bosqichda **to'xta**, menga diagrammalarni tushuntir va tasdiqlashimni kut. Tasdiqlangan arxitektura keyingi barcha bosqichlar uchun asos bo'ladi; keyin o'zgartirish kerak bo'lsa, avval shu faylni yangila.
- **0-bosqich:** Monorepo tuzilmasi (`backend/`, `bot/`, `web/`, `mobile/`), git, Docker Compose (PostgreSQL + backend), `.env.example`, `CLAUDE.md`, o'zbekcha `README.md` (Ubuntu'da qanday ishga tushirish). Natija: bot `/start` ga javob beradi, sayt bosh sahifasi ochiladi, ilova telefonda (Expo Go orqali) ochiladi — uchalasi ham backend'dan bitta test so'rovini oladi.
- **1-bosqich:** Bazaning to'liq modeli (barcha jadvallar va migratsiyalar) + ro'yxatdan o'tish + Telegram orqali kirish (uchala joyda) + rollar + haydovchini admin tasdiqlashi (sayt admin panelida).
- **2-bosqich:** Shahar/bozor/yo'nalish va tariflar (admin panel) + buyurtma berish + narx hisoblash.
- **3-bosqich:** Reyslar + moslashtirish + bitta reysga ko'p buyurtma yig'ish.
- **4-bosqich:** Holatlar, rasmlar, qabul qiluvchi kodi, audit log, bahs ochish, bildirishnomalar (Telegram + push).
- **4.5-bosqich:** Yukni kuzatish (3.11): haydovchi joylashuvi, "Menga kelayotgan yuklar", kuzatish havolasi, taxminiy yetib kelish vaqti, qabul qiluvchiga bildirishnomalar.
- **5-bosqich:** Reyting, bloklash, bozor xaritasi, bekor qilish.
- **6-bosqich:** Admin statistika, testlarni to'ldirish, zaxira skripti, serverga deploy qo'llanmasi, Android ilovani Google Play'ga chiqarish qo'llanmasi.

### Qoidalar
- Kichik, tushunarli commitlar; har bir bosqich oxirida commit.
- Asosiy biznes mantiq (narx hisoblash, moslashtirish, holat o'tishlari) uchun albatta testlar.
- Pullik xizmat, yangi katta kutubxona yoki arxitekturani o'zgartirishdan oldin menga sababini aytib, ruxsat so'ra.
- Biror narsa noaniq bo'lsa, taxmin qilma — so'ra.
- Bot, sayt va ilovadagi matnlar sodda, xushmuomala o'zbek tilida (lotin), bozor savdogarlari va haydovchilar tushunadigan qilib; tugmalar ko'p, matn yozish kam. Ilova va sayt dizayni oddiy, katta tugmali, arzon Android telefonlarda ham tez ishlaydigan bo'lsin.

A-bosqichdan (arxitektura) boshla.

---

## Loyiha holati (har bosqichdan keyin yangilanadi)

- [ ] **A-bosqich — Arxitektura:** `docs/architecture.md` yozildi, Habibullo tasdiqlashi kutilmoqda. Ochiq savollar shu faylning 8-bo'limida.
- [ ] 0-bosqich
- [ ] 1-bosqich
- [ ] 2-bosqich
- [ ] 3-bosqich
- [ ] 4-bosqich
- [ ] 4.5-bosqich
- [ ] 5-bosqich
- [ ] 6-bosqich

Arxitektura bo'yicha yagona manba — `docs/architecture.md`. Kod unga mos bo'lishi kerak; o'zgartirish kerak bo'lsa, avval shu fayl yangilanadi.
