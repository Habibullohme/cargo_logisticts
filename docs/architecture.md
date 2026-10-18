# Arxitektura — Yuk tashish platformasi

> **Holati:** A-bosqich, tasdiqlash kutilmoqda.
> Bu fayl keyingi barcha bosqichlar uchun asos. Arxitekturada biror narsa o'zgarsa, avval shu fayl yangilanadi, keyin kod.

## Mundarija

0. [Asosiy qarorlar qisqacha](#0-asosiy-qarorlar-qisqacha)
1. [Umumiy tizim sxemasi](#1-umumiy-tizim-sxemasi)
2. [Ma'lumotlar bazasi sxemasi (ER)](#2-malumotlar-bazasi-sxemasi-er)
3. [Buyurtma holatlari (state machine)](#3-buyurtma-holatlari-state-machine)
4. [Asosiy jarayonlar (sequence)](#4-asosiy-jarayonlar-sequence)
5. [Papka tuzilmasi](#5-papka-tuzilmasi)
6. [Deploy sxemasi va zaxira](#6-deploy-sxemasi-va-zaxira)
7. [Muhim texnik qoidalar](#7-muhim-texnik-qoidalar)
8. [Ochiq savollar (javobingiz kerak)](#8-ochiq-savollar-javobingiz-kerak)

---

## 0. Asosiy qarorlar qisqacha

| Qism | Tanlov | Nega |
|---|---|---|
| Backend API | Python 3.12 + FastAPI, REST, `/api/v1/...` | Tez, avtomatik hujjat (OpenAPI) beradi |
| Biznes mantiq | `backend/app/services/` | Narx, moslashtirish, holatlar faqat shu yerda — bot, sayt, ilova faqat API'ni chaqiradi |
| Baza | PostgreSQL 16, SQLAlchemy 2, Alembic | Ishonchli, bepul, tranzaksiyalar (joy band qilishda muhim) |
| Fon ishlari | Alohida **worker** jarayoni, navbat — PostgreSQL jadvalida | Redis kabi qo'shimcha xizmat kerak emas; keyin kerak bo'lsa almashtiriladi |
| Telegram bot | aiogram 3, bazaga emas, **API'ga** ulanadi | Mantiq bir joyda qoladi |
| Veb-sayt | Next.js (TypeScript), responsive | Kabinet + admin panel + ochiq kuzatish sahifasi |
| Mobil ilova | React Native (Expo, TypeScript), avval Android | Bitta kod, keyin iOS ham |
| API turlari | Backend `openapi.json` dan sayt va ilova uchun TypeScript turlari avtomatik yaratiladi | Qo'lda nusxa ko'chirish xatolarini yo'qotadi |
| Kirish | Telegram: saytda Telegram Login, ilovada bot yuborgan kod, botda Telegram ID | Pullik SMS kerak emas |
| Fayllar | `storage` moduli: hozir lokal disk, keyin O'zbekistondagi S3-mos saqlash | Kodni o'zgartirmasdan almashtirish mumkin |
| Pul | `BIGINT`, so'mda, butun son | Float yaxlitlash xatolari bo'lmaydi |
| Vaqt | Bazada UTC (`timestamptz`), ko'rsatish va "bugun/ertaga" — Asia/Tashkent | Standart va xatosiz usul |
| Ishga tushirish | Docker Compose (lokal va serverda bir xil) | "Menda ishlaydi, serverda yo'q" muammosi bo'lmaydi |

---

## 1. Umumiy tizim sxemasi

```mermaid
flowchart TB
    subgraph Qurilmalar["Foydalanuvchi qurilmalari"]
        TGAPP["Telegram ilovasi<br/>(savdogar, haydovchi)"]
        BROWSER["Brauzer<br/>(kabinet, admin, kuzatish havolasi)"]
        MOBILE["Mobil ilova<br/>React Native / Expo<br/>(asosan haydovchi)"]
    end

    subgraph Tashqi["Tashqi kanallar (faqat xabar yetkazish)"]
        TGCLOUD["Telegram serverlari"]
        PUSHSVC["Push xizmati<br/>Expo Push / FCM"]
    end

    subgraph Server["Bizning server — O'zbekiston"]
        NGINX["Nginx<br/>HTTPS, yo'naltirish"]
        BOT["Telegram bot<br/>aiogram 3"]
        WEB["Veb-sayt<br/>Next.js"]
        API["Backend API — FastAPI<br/>services: narx, moslashtirish,<br/>holatlar, kuzatish, ETA"]
        WORKER["Worker (fon ishchisi)<br/>bildirishnomalar, ETA, avto-yakunlash,<br/>eski joylashuvlarni tozalash"]
        DB[("PostgreSQL<br/>barcha ma'lumotlar")]
        FILES[("Fayl saqlash<br/>yuk rasmlari, hujjatlar")]
    end

    TGAPP <--> TGCLOUD
    TGCLOUD <-->|"yangilanishlar, jonli lokatsiya"| BOT
    BROWSER -->|HTTPS| NGINX
    MOBILE -->|"HTTPS: REST API, joylashuv, rasm"| NGINX
    NGINX --> WEB
    NGINX -->|"/api"| API
    WEB -->|REST API| API
    BOT -->|"REST API (ichki tarmoq, bot kaliti)"| API
    API --> DB
    API --> FILES
    API -->|"bildirishnoma navbatiga yozadi"| DB
    WORKER -->|"navbatni o'qiydi"| DB
    WORKER -->|"Bot API orqali xabar"| TGCLOUD
    WORKER -->|"push"| PUSHSVC
    PUSHSVC --> MOBILE
```

**Tushuntirish.** Uchta mijoz (bot, sayt, ilova) hech qachon bazaga to'g'ridan-to'g'ri ulanmaydi — hammasi bitta **Backend API** orqali ishlaydi, shuning uchun narx hisoblash yoki holat o'zgartirish qoidasi bir marta yoziladi. Bildirishnomalar ham bitta joyda: API "kimga, nima" yuborishni bazadagi navbatga yozadi, **worker** esa uni Telegram yoki push orqali yuboradi (internet uzilsa — qayta urinadi). Ma'lumotlar (baza va rasmlar) faqat O'zbekistondagi serverimizda turadi; Telegram va push xizmati faqat qisqa xabarni yetkazuvchi "pochtachi" vazifasida (8-bo'limdagi 5-savolga qarang).

---

## 2. Ma'lumotlar bazasi sxemasi (ER)

Jadvallar ko'p bo'lgani uchun sxema 4 qismga bo'lindi. Barcha jadvallarda `id` (BIGINT), `created_at` va kerak joyda `updated_at` bor — diagrammada takrorlanmadi.

### 2.1. Foydalanuvchilar, haydovchilar, kirish

```mermaid
erDiagram
    USERS ||--o{ USER_ROLES : "rollari"
    USERS ||--o| DRIVER_PROFILES : "haydovchi bo'lsa"
    USERS ||--o{ AUTH_SESSIONS : "kirish sessiyalari"
    USERS ||--o{ LOGIN_CODES : "bir martalik kodlar"
    USERS ||--o{ PUSH_DEVICES : "telefonlari"
    DRIVER_PROFILES ||--o{ DRIVER_DOCUMENTS : "hujjatlari"
    DRIVER_PROFILES ||--o{ VEHICLES : "mashinalari"
    DRIVER_PROFILES ||--o{ DRIVER_ROUTES : "ishlaydigan yo'nalishlari"
    DRIVER_ROUTES }o--|| ROUTES : "yo'nalish"
    DRIVER_DOCUMENTS }o--|| FILES : "rasm fayli"

    USERS {
        bigint id PK
        string phone UK "+998XXXXXXXXX ko'rinishida"
        string full_name
        bigint telegram_id UK "bo'sh bo'lishi mumkin"
        string telegram_username
        string language "uz_latn (keyin uz_cyrl, ru)"
        bool is_blocked
        string block_reason
        numeric rating_avg "kesh, 1-5"
        int rating_count
    }
    USER_ROLES {
        bigint user_id FK
        enum role "sender, driver, receiver, admin"
    }
    DRIVER_PROFILES {
        bigint user_id PK,FK
        enum status "tekshirilmoqda, tasdiqlangan, rad_etilgan, bloklangan"
        string reject_reason
        bigint reviewed_by FK "admin"
        timestamptz reviewed_at
        timestamptz location_consent_at "joylashuvga rozilik"
    }
    DRIVER_DOCUMENTS {
        bigint id PK
        bigint driver_id FK
        enum doc_type "guvohnoma, texpasport, litsenziya"
        bigint file_id FK
    }
    VEHICLES {
        bigint id PK
        bigint driver_id FK
        string plate_number UK "01A123BC"
        string vehicle_type "Isuzu va h.k."
        int capacity_units "taxminiy qop/korobka sig'imi"
        bool is_active
    }
    DRIVER_ROUTES {
        bigint driver_id FK
        bigint route_id FK
    }
    AUTH_SESSIONS {
        bigint id PK
        bigint user_id FK
        string refresh_token_hash
        enum client "bot, web, mobile"
        timestamptz expires_at
        timestamptz revoked_at
    }
    LOGIN_CODES {
        bigint id PK
        bigint user_id FK
        string code_hash
        int attempts
        timestamptz expires_at "5 daqiqa"
        timestamptz used_at
    }
    PUSH_DEVICES {
        bigint id PK
        bigint user_id FK
        string push_token UK
        string platform "android, ios"
    }
```

**Tushuntirish.** Har bir odam — bitta `USERS` yozuvi, telefon raqami bilan; u bir nechta rolga ega bo'lishi mumkin (masalan, ham yuboruvchi, ham qabul qiluvchi). Haydovchining qo'shimcha ma'lumotlari, hujjatlari va mashinasi alohida jadvallarda turadi va admin tasdiqlamaguncha holati `tekshirilmoqda` bo'ladi. `AUTH_SESSIONS` va `LOGIN_CODES` — Telegram orqali kirishni xavfsiz qilish uchun (kodlar va tokenlar bazada ochiq holda emas, faqat "hash" ko'rinishida saqlanadi).

### 2.2. Geografiya, yo'nalishlar, tariflar

```mermaid
erDiagram
    REGIONS ||--o{ CITIES : "shaharlari"
    CITIES ||--o{ MARKETS : "bozorlari"
    MARKETS ||--o{ DROP_POINTS : "yuk tushirish joylari"
    CITIES ||--o{ ROUTES : "qayerdan"
    CITIES ||--o{ ROUTES : "qayerga"
    ROUTES ||--o{ TARIFFS : "narxlari"
    CARGO_TYPES ||--o{ TARIFFS : "yuk turi bo'yicha"

    REGIONS {
        bigint id PK
        string name "Namangan viloyati"
        int sort_order
    }
    CITIES {
        bigint id PK
        bigint region_id FK
        string name "Namangan, Shahrixon..."
        numeric lat
        numeric lon
        int radius_km "shaharga kirdi hisobi uchun"
        bool is_active
    }
    MARKETS {
        bigint id PK
        bigint city_id FK
        string name "Chorsu, Abu Saxiy..."
        numeric lat
        numeric lon
        string note
        bool is_active
    }
    DROP_POINTS {
        bigint id PK
        bigint market_id FK
        string name
        string gate_zone "2-darvoza, B zona"
        numeric lat
        numeric lon
        string note "ertalab 6 dan 9 gacha"
        bool is_active
    }
    ROUTES {
        bigint id PK
        bigint from_city_id FK
        bigint to_city_id FK
        int distance_km
        int avg_duration_min "ETA uchun"
        bool is_active
    }
    CARGO_TYPES {
        bigint id PK
        string code UK "shoes"
        string name "Oyoq kiyim"
        bool is_active
    }
    TARIFFS {
        bigint id PK
        bigint route_id FK
        bigint cargo_type_id FK
        enum kind "standard, return"
        bigint price_per_unit_sum "1 qop/korobka narxi, so'm"
        timestamptz valid_from
        timestamptz valid_to "bo'sh = hozir amalda"
        bigint created_by FK "admin"
    }
```

**Tushuntirish.** Kodda hech qanday shahar yoki bozor nomi yozilmaydi: viloyat → shahar → bozor → yuk tushirish joyi zanjiri to'liq bazada va admin saytdan qo'shadi (xaritada belgilab). Yo'nalish ikki shahar orasida bo'ladi (Namangan → Toshkent va Toshkent → Namangan — alohida yo'nalishlar). Tarif o'zgarganda eski narx o'chirilmaydi, balki yangi yozuv qo'shiladi — shunda eski buyurtmalar qaysi narxda hisoblangani doim ko'rinadi.

### 2.3. Buyurtma, reys, kuzatish

```mermaid
erDiagram
    USERS ||--o{ ORDERS : "yuboradi"
    USERS |o--o{ ORDERS : "qabul qiladi (telefon orqali)"
    ROUTES ||--o{ ORDERS : "yo'nalish"
    MARKETS ||--o{ ORDERS : "qayerdan / qayerga"
    DROP_POINTS |o--o{ ORDERS : "tushirish joyi"
    TARIFFS ||--o{ ORDERS : "qo'llangan narx"
    DRIVER_PROFILES ||--o{ TRIPS : "reys e'lon qiladi"
    VEHICLES ||--o{ TRIPS : "qaysi mashina"
    ROUTES ||--o{ TRIPS : "yo'nalish"
    TRIPS |o--o{ ORDERS : "reysdagi buyurtmalar"
    TRIPS ||--o{ ORDER_OFFERS : "takliflar"
    ORDERS ||--o{ ORDER_OFFERS : "takliflar"
    TRIPS ||--o{ LOCATION_POINTS : "mashina joylashuvi"
    ORDERS ||--o{ ORDER_STATUS_HISTORY : "holatlar tarixi"
    ORDERS ||--o{ ORDER_PHOTOS : "rasmlar"
    ORDER_PHOTOS }o--|| FILES : "fayl"
    ORDERS ||--o{ RATINGS : "baholar"
    ORDERS ||--o{ DISPUTES : "bahslar"
    DISPUTES |o--o{ ORDER_PHOTOS : "bahs rasmlari"

    ORDERS {
        bigint id PK
        string public_no UK "Y-250117-0042"
        bigint sender_id FK
        bigint route_id FK
        bigint from_market_id FK
        bigint to_market_id FK
        bigint to_drop_point_id FK
        bigint cargo_type_id FK
        int units_declared "yuboruvchi aytgan son"
        int units_confirmed "haydovchi olganda sanagan son"
        bigint declared_value_sum "taxminiy qiymat"
        string receiver_name
        string receiver_phone "+998..."
        bigint receiver_user_id FK "bo'sh bo'lishi mumkin"
        date pickup_date "Toshkent vaqti bo'yicha"
        enum payer "sender, receiver"
        enum payment_method "cash (keyin click, payme)"
        bool insurance_requested
        string comment
        bigint tariff_id FK
        bigint unit_price_sum
        bigint total_price_sum
        enum status "3-bo'lim"
        bigint trip_id FK "bo'sh bo'lishi mumkin"
        string delivery_code "4 xonali"
        int delivery_code_attempts
        string tracking_token UK "taxmin qilib bo'lmaydigan"
        timestamptz sender_confirmed_pickup_at
        string cancel_reason
        bigint cancelled_by FK
    }
    TRIPS {
        bigint id PK
        bigint driver_id FK
        bigint vehicle_id FK
        bigint route_id FK
        date trip_date
        int capacity_units "e'lon qilingan bo'sh joy"
        int reserved_units "band qilingan joy"
        bool is_return "qaytish reysi"
        enum status "ochiq, yolda, tugadi, bekor_qilindi"
        timestamptz departed_at
        timestamptz finished_at
        numeric last_lat "kesh"
        numeric last_lon "kesh"
        timestamptz last_location_at
    }
    ORDER_OFFERS {
        bigint id PK
        bigint order_id FK
        bigint trip_id FK
        enum status "kutilmoqda, qabul_qilindi, rad_etildi, eskirdi"
        timestamptz expires_at
    }
    LOCATION_POINTS {
        bigint id PK
        bigint trip_id FK
        numeric lat
        numeric lon
        int accuracy_m
        enum source "app, telegram_live"
        timestamptz recorded_at
    }
    ORDER_STATUS_HISTORY {
        bigint id PK
        bigint order_id FK
        enum from_status
        enum to_status
        bigint changed_by FK "bo'sh = tizim"
        enum actor_role "sender, driver, receiver, admin, system"
        string note
        timestamptz created_at
    }
    ORDER_PHOTOS {
        bigint id PK
        bigint order_id FK
        bigint file_id FK
        enum stage "pickup, delivery, dispute"
        bigint dispute_id FK
        bigint uploaded_by FK
    }
    RATINGS {
        bigint id PK
        bigint order_id FK
        bigint from_user_id FK
        bigint to_user_id FK
        int score "1-5"
        string comment
    }
    DISPUTES {
        bigint id PK
        bigint order_id FK
        bigint opened_by FK
        enum status "ochiq, hal_qilindi, rad_etildi"
        string description
        string resolution
        bigint resolved_by FK "admin"
        timestamptz resolved_at
    }
```

**Tushuntirish.** `ORDERS` — bitta savdogarning bitta yuki; `TRIPS` — haydovchining bitta qatnovi, bitta reysga ko'p buyurtma yig'iladi (`trip_id` orqali) va `reserved_units` sig'imdan oshib ketmasligini tizim tekshiradi. Buyurtmadagi narx (`unit_price_sum`, `total_price_sum`) yaratilgan paytda "muzlatib" qo'yiladi — admin keyin tarifni o'zgartirsa ham eski buyurtma narxi o'zgarmaydi. Qabul qiluvchi telefon raqami orqali bog'lanadi: u ro'yxatdan o'tmagan bo'lsa ham yuk yaratiladi, ro'yxatdan o'tganda esa unga kelayotgan barcha yuklar avtomatik ko'rinadi.

### 2.4. Tizim jadvallari

```mermaid
erDiagram
    USERS ||--o{ NOTIFICATIONS : "oladi"
    USERS ||--o{ FILES : "yuklagan"
    USERS ||--o{ AUDIT_LOGS : "admin amallari"

    FILES {
        bigint id PK
        string storage_key UK "diskdagi yoki S3dagi yo'l"
        string mime_type
        int size_bytes
        enum visibility "private_admin, order_parties"
        bigint uploaded_by FK
    }
    NOTIFICATIONS {
        bigint id PK
        bigint user_id FK "bo'sh bo'lishi mumkin"
        string phone "ro'yxatdan o'tmagan qabul qiluvchi uchun"
        enum channel "telegram, push, sms"
        string template "order_delivered va h.k."
        jsonb payload
        enum status "kutilmoqda, yuborildi, xato"
        int attempts
        timestamptz send_after
        timestamptz sent_at
    }
    AUDIT_LOGS {
        bigint id PK
        bigint actor_id FK
        string action "tariff.update, user.block..."
        string entity
        bigint entity_id
        jsonb before
        jsonb after
    }
    SETTINGS {
        string key PK "cancel_penalty_sum va h.k."
        jsonb value
    }
```

**Tushuntirish.** `NOTIFICATIONS` — bildirishnomalar navbati: API bu yerga yozadi, worker o'qib yuboradi, xato bo'lsa qayta urinadi; `channel` ichida `sms` ham bor — keyin SMS qo'shilganda jadval o'zgarmaydi. `AUDIT_LOGS` admin qilgan har bir muhim ish (tarif o'zgartirish, bloklash, haydovchini tasdiqlash)ni "kim, qachon, nima edi, nima bo'ldi" ko'rinishida saqlaydi. `SETTINGS` — kodni o'zgartirmasdan sozlanadigan qiymatlar (masalan, bekor qilish jarimasi — hozircha 0).

---

## 3. Buyurtma holatlari (state machine)

```mermaid
stateDiagram-v2
    [*] --> yangi : Yuboruvchi buyurtma beradi

    yangi --> haydovchi_tayinlandi : Haydovchi taklifni qabul qiladi (yoki admin tayinlaydi)
    haydovchi_tayinlandi --> yangi : Haydovchi voz kechadi, yuk olinmasdan reys ketdi

    haydovchi_tayinlandi --> yuk_olindi : Haydovchi rasm + joy sonini kiritadi
    yuk_olindi --> yolda : Haydovchi "Yo'lga chiqdim" bosadi
    yolda --> yetkazildi : Haydovchi rasm + qabul qiluvchi kodi
    yetkazildi --> yakunlandi : Qabul qiluvchi tasdiqlaydi yoki 24 soatdan keyin tizim

    yangi --> bekor_qilindi : Yuboruvchi yoki admin
    haydovchi_tayinlandi --> bekor_qilindi : Yuboruvchi yoki admin
    yuk_olindi --> bekor_qilindi : Faqat admin
    yolda --> bekor_qilindi : Faqat admin

    yuk_olindi --> bahs : Har qaysi tomon "Muammo bor"
    yolda --> bahs : Har qaysi tomon "Muammo bor"
    yetkazildi --> bahs : Har qaysi tomon "Muammo bor"
    bahs --> yakunlandi : Admin hal qiladi
    bahs --> bekor_qilindi : Admin hal qiladi

    yakunlandi --> [*]
    bekor_qilindi --> [*]
```

Kim qaysi o'tishni qila oladi:

| O'tish | Kim | Shart / dalil |
|---|---|---|
| `yangi` → `haydovchi_tayinlandi` | Haydovchi (taklifni qabul qiladi), admin | Haydovchi `tasdiqlangan`, reysda bo'sh joy yetarli |
| `haydovchi_tayinlandi` → `yangi` | Haydovchi, tizim | Haydovchi voz kechsa yoki reys yo'lga chiqib, bu yuk olinmagan bo'lsa; yuboruvchiga xabar |
| `haydovchi_tayinlandi` → `yuk_olindi` | Haydovchi | Kamida 1 ta rasm + sanagan joy soni. Son farq qilsa — ogohlantirish. Yuboruvchi "Tasdiqlayman" bosadi (`sender_confirmed_pickup_at`) |
| `yuk_olindi` → `yolda` | Haydovchi | Reys bo'yicha bitta tugma: reysdagi barcha olingan yuklar birdan `yolda` bo'ladi, joylashuv kuzatish boshlanadi |
| `yolda` → `yetkazildi` | Haydovchi | Kamida 1 ta rasm + to'g'ri 4 xonali kod. 5 marta xato kiritilsa — kod bloklanadi, admin aralashadi |
| `yetkazildi` → `yakunlandi` | Qabul qiluvchi, tizim (24 soatdan keyin), admin | Bahs ochilmagan bo'lsa. Shundan keyin baho so'raladi |
| → `bekor_qilindi` | Yuk olinmaguncha: yuboruvchi, admin. Yuk olingandan keyin: faqat admin | Sabab majburiy. Jarima `SETTINGS` dan (hozir 0) |
| → `bahs` | Yuboruvchi, haydovchi, qabul qiluvchi | Izoh majburiy, rasm ixtiyoriy |
| `bahs` → yakuniy holat | Faqat admin | Qaror matni saqlanadi |

**Tushuntirish.** Buyurtma faqat chizmadagi strelkalar bo'yicha o'tadi — boshqa har qanday o'tishni backend rad etadi (masalan, `yangi` dan to'g'ridan-to'g'ri `yetkazildi` ga o'tib bo'lmaydi). Har bir o'tish `ORDER_STATUS_HISTORY` ga vaqt, kim va qaysi rolda qilgani bilan yoziladi — bahs paytida admin shuni ko'radi. Bu qoidalar `backend/app/services/order_status.py` da bitta joyda yoziladi va to'liq testlar bilan qoplanadi.

Reys (`TRIPS`) holatlari soddaroq: `ochiq` (buyurtma yig'ilmoqda) → `yolda` → `tugadi` (barcha yuklar yetkazilganda avtomatik), yoki `bekor_qilindi`.

---

## 4. Asosiy jarayonlar (sequence)

### 4.1. Kirish (login)

```mermaid
sequenceDiagram
    autonumber
    actor U as Foydalanuvchi
    participant BOT as Telegram bot
    participant WEB as Sayt
    participant APP as Mobil ilova
    participant API as Backend API
    participant DB as PostgreSQL

    Note over U,DB: Ro'yxatdan o'tish — faqat botda (telefonni Telegram tasdiqlaydi)
    U->>BOT: /start, "Kontaktni yuborish" tugmasi
    BOT->>API: POST /auth/bot/register (telegram_id, telefon, rol)
    API->>DB: USERS + USER_ROLES (+ DRIVER_PROFILES: tekshirilmoqda)
    API-->>BOT: foydalanuvchi ma'lumoti

    Note over U,DB: Saytga kirish
    U->>WEB: "Telegram orqali kirish" (Telegram Login)
    WEB->>API: POST /auth/telegram-login (Telegram imzolagan ma'lumot)
    API->>API: Imzoni bot tokeni bilan tekshiradi
    API-->>WEB: access token + refresh token

    Note over U,DB: Ilovaga kirish
    U->>APP: Telefon raqamini kiritadi
    APP->>API: POST /auth/code/request
    API->>DB: LOGIN_CODES (hash, 5 daqiqa)
    API-->>BOT: worker orqali kod Telegram'da yuboriladi
    U->>APP: Kodni kiritadi
    APP->>API: POST /auth/code/verify
    API-->>APP: access token + refresh token
```

**Tushuntirish.** Ro'yxatdan o'tish botda boshlanadi, chunki Telegram "kontakt yuborish" orqali telefon raqami haqiqatan shu odamniki ekanini kafolatlaydi — SMS kerak emas. Saytda Telegram'ning rasmiy kirish tugmasi ishlatiladi, ilovada esa bot yuborgan bir martalik kod. Bot o'zi API'ga maxsus "bot kaliti" bilan murojaat qiladi va qaysi Telegram foydalanuvchi nomidan ishlayotganini aytadi.

### 4.2. Buyurtma → moslashtirish → yuk olish → yo'l → yetkazish

```mermaid
sequenceDiagram
    autonumber
    actor S as Yuboruvchi
    participant C as Bot / Sayt / Ilova
    participant API as Backend API
    participant DB as PostgreSQL
    participant W as Worker
    actor D as Haydovchi
    actor R as Qabul qiluvchi

    S->>C: Qayerdan, qayerga, nechta qop, qabul qiluvchi, sana
    C->>API: POST /orders/quote
    API->>DB: Amaldagi tarifni oladi
    API-->>C: Narx: 12 qop x 15 000 = 180 000 so'm
    S->>C: "Tasdiqlayman"
    C->>API: POST /orders
    API->>DB: ORDERS (yangi) + kod + kuzatish tokeni + tarix
    API->>DB: Bildirishnoma navbati
    W-->>R: "Sizga yuk yuborildi" + kuzatish havolasi

    Note over API,DB: Moslashtirish: bir xil yo'nalish va sana, bo'sh joy yetarli
    API->>DB: Mos ochiq reyslarni topadi, ORDER_OFFERS yozadi
    W-->>D: "Yangi buyurtma: 12 qop, Namangan → Toshkent"
    D->>API: POST /offers/{id}/accept
    API->>DB: Reysni qulflaydi, joyni tekshiradi, buyurtma → haydovchi_tayinlandi
    W-->>S: Haydovchi: ism, mashina raqami, reyting, telefon
    W-->>D: Tushirish joyi lokatsiyasi (xarita / Telegram lokatsiya)

    D->>API: POST /orders/{id}/pickup (rasm, 12 ta)
    API->>DB: yuk_olindi, units_confirmed = 12
    W-->>S: "Yuk olindi, tasdiqlang"
    W-->>R: "Yukingiz mashinaga ortildi: 12 ta"
    S->>API: POST /orders/{id}/confirm-pickup

    D->>API: POST /trips/{id}/depart ("Yo'lga chiqdim")
    API->>DB: Reys va yuklari → yolda
    W-->>R: "Yuk yo'lga chiqdi"
    loop Har 2-5 daqiqada
        D->>API: POST /trips/{id}/locations
        API->>DB: LOCATION_POINTS, ETA qayta hisoblanadi
        W-->>R: "Shaharga kirdi" / "~30 daqiqada yetib keladi" (bir martadan)
    end

    R->>D: 4 xonali kodni aytadi
    D->>API: POST /orders/{id}/deliver (rasm, kod)
    API->>DB: Kodni tekshiradi → yetkazildi
    W-->>S: "Yuk yetkazildi"
    W-->>R: "Yuk yetkazildi"
    Note over API,W: 24 soat ichida bahs ochilmasa → yakunlandi, ikki tomondan baho so'raladi
```

**Tushuntirish.** Yuboruvchi buyurtma berishdan oldin narxni ko'radi; tasdiqlagach tizim mos reysli haydovchilarga taklif yuboradi (haydovchi reys e'lon qilganda ham shu qidiruv ishlaydi, faqat teskari yo'nalishda). Haydovchi taklifni qabul qilganda baza reysni qisqa vaqtga "qulflaydi" — ikki haydovchi yoki ikki buyurtma bir vaqtda oxirgi bo'sh joyni egallab, sig'imdan oshib ketolmaydi. Har bir muhim qadamda rasm va son (yuk olishda) yoki kod (yetkazishda) dalil sifatida saqlanadi.

### 4.3. Qabul qiluvchining yukni kuzatishi

```mermaid
sequenceDiagram
    autonumber
    actor R as Qabul qiluvchi
    participant C as Bot / Sayt / Ilova
    participant WEB as Kuzatish sahifasi (sayt)
    participant BOT as Telegram bot
    participant API as Backend API
    participant DB as PostgreSQL
    actor D as Haydovchi

    Note over D,DB: Joylashuv ikki yo'l bilan keladi
    D->>API: Ilova: POST /trips/{id}/locations (har 2-5 daqiqa)
    D->>BOT: Yoki Telegram "jonli lokatsiya" ulashadi
    BOT->>API: POST /trips/{id}/locations (source = telegram_live)
    API->>DB: LOCATION_POINTS + reysdagi oxirgi joy

    alt Ro'yxatdan o'tgan qabul qiluvchi
        R->>C: "Menga kelayotgan yuklar"
        C->>API: GET /me/incoming-orders
        API->>DB: receiver_phone = mening telefonim
        API-->>C: Ro'yxat: kimdan, nechta (e'lon / tasdiqlangan), holat, ETA
    else Ro'yxatdan o'tmagan — havola orqali
        R->>WEB: /t/{tracking_token}
        WEB->>API: GET /public/track/{tracking_token}
        API-->>WEB: Telefonlar qisman yashirilgan ma'lumot
    end

    R->>C: Bitta yukni ochadi
    C->>API: GET /orders/{id}/tracking
    API->>DB: Tarix, rasm, oxirgi joylashuv, ETA
    API-->>C: Xarita, "12 daqiqa oldin yangilangan", ~2 soat 10 daqiqa, kod, haydovchi
```

**Tushuntirish.** Qabul qiluvchi uchun ikki yo'l bor: ro'yxatdan o'tgan bo'lsa — telefon raqamiga bog'langan barcha yuklarni "Menga kelayotgan yuklar" bo'limida ko'radi; o'tmagan bo'lsa — yuboruvchi bergan maxsus havola orqali (login kerak emas, telefonlar `+998 90 *** ** 67` ko'rinishida). Mashina joylashuvi haydovchi ilovasidan yoki Telegram jonli lokatsiyasidan keladi va faqat reys `yolda` holatida qabul qilinadi. Taxminiy yetib kelish vaqti (ETA) boshida oddiy hisob: qolgan masofa ÷ yo'nalishning o'rtacha tezligi (`distance_km / avg_duration_min`); joylashuv bo'lmasa — jo'nash vaqti + `avg_duration_min`.

---

## 5. Papka tuzilmasi

```mermaid
flowchart LR
    ROOT["cargo_logisticts/"] --> BACK["backend/<br/>FastAPI, barcha mantiq"]
    ROOT --> BOTD["bot/<br/>aiogram 3"]
    ROOT --> WEBD["web/<br/>Next.js"]
    ROOT --> MOB["mobile/<br/>Expo"]
    ROOT --> DOCS["docs/<br/>hujjatlar"]
    ROOT --> DEPLOY["deploy/<br/>nginx, zaxira skriptlari"]
    BOTD -.->|REST API| BACK
    WEBD -.->|REST API| BACK
    MOB -.->|REST API| BACK
```

```text
cargo_logisticts/
├── CLAUDE.md                 # loyiha konteksti (sessiyalar uchun)
├── README.md                 # o'zbekcha: Ubuntu'da qanday ishga tushirish
├── .env.example              # maxfiy kalitlar namunasi (.env gitga tushmaydi)
├── docker-compose.yml        # lokal ishga tushirish
├── docker-compose.prod.yml   # serverdagi qo'shimchalar
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI ilovasi
│   │   ├── core/             # sozlamalar, baza ulanishi, xavfsizlik, vaqt zonasi
│   │   ├── models/           # SQLAlchemy jadvallari
│   │   ├── schemas/          # Pydantic: API kiradigan/chiqadigan ma'lumotlar
│   │   ├── api/v1/           # endpointlar (faqat qabul qiladi va services'ni chaqiradi)
│   │   ├── services/         # BIZNES MANTIQ: pricing, matching, order_status, tracking, eta...
│   │   ├── notifications/    # bildirishnoma yuborishning yagona joyi (telegram, push, keyin sms)
│   │   ├── storage/          # fayl saqlash: local.py (hozir), s3.py (keyin)
│   │   ├── workers/          # fon ishlari: navbat, avto-yakunlash, tozalash
│   │   └── i18n/             # xabar matnlari: uz_latn.json (keyin uz_cyrl, ru)
│   ├── migrations/           # Alembic migratsiyalari
│   ├── tests/                # pytest
│   └── pyproject.toml
├── bot/
│   ├── app/
│   │   ├── handlers/         # /start, ro'yxatdan o'tish, buyurtma, reys...
│   │   ├── keyboards/        # tugmalar
│   │   ├── api_client.py     # backend API bilan gaplashish
│   │   └── locales/          # bot matnlari
│   └── pyproject.toml
├── web/
│   ├── src/app/              # sahifalar: kabinet, admin/, t/[token] (kuzatish)
│   ├── src/components/
│   ├── src/lib/api/          # openapi.json dan yaratilgan turlar + mijoz
│   └── src/locales/
├── mobile/
│   ├── app/                  # ekranlar (Expo Router)
│   ├── src/lib/api/          # openapi.json dan yaratilgan turlar + mijoz
│   ├── src/location/         # reys davomida joylashuv yuborish
│   └── src/locales/
├── deploy/
│   ├── nginx/                # nginx sozlamalari
│   └── backup/               # backup.sh, restore.sh
└── docs/
    ├── architecture.md       # shu fayl
    ├── deploy.md             # serverga deploy qo'llanmasi (6-bosqich)
    ├── backup.md             # zaxira qo'llanmasi (6-bosqich)
    └── play-store.md         # Google Play'ga chiqarish (6-bosqich)
```

**Tushuntirish.** Bitta repozitoriyda beshta asosiy papka: `backend/` — miya (barcha qoidalar), `bot/`, `web/`, `mobile/` — faqat ko'rinish va tugmalar, `docs/` — hujjatlar. Promptdagi ro'yxatga faqat bitta `deploy/` papkasi qo'shildi — server sozlamalari va zaxira skriptlari kod bilan aralashmasligi uchun. Backend ichida `api/` faqat so'rovni qabul qiladi, haqiqiy ish esa `services/` da — shuning uchun mantiqni bot, sayt yoki ilovadan qat'i nazar bir xil testlash mumkin.

---

## 6. Deploy sxemasi va zaxira

```mermaid
flowchart TB
    INTERNET(("Internet<br/>foydalanuvchilar"))
    TG["Telegram serverlari"]

    subgraph UZ1["Asosiy server — O'zbekistondagi data-markaz (Ubuntu + Docker Compose)"]
        NGINX["nginx :443<br/>HTTPS (Let's Encrypt)"]
        WEB["web :3000<br/>Next.js"]
        API["backend :8000<br/>FastAPI (uvicorn)"]
        WORKER["worker<br/>(backend kodi, boshqa buyruq)"]
        BOT["bot<br/>aiogram"]
        PG[("postgres :5432<br/>faqat ichki tarmoq")]
        VOL_PG[["volume: pgdata"]]
        VOL_UP[["volume: uploads<br/>(rasmlar, hujjatlar)"]]
        CRON["cron, har kuni 03:00<br/>deploy/backup/backup.sh"]
        LOCALBK[["/var/backups/yuk<br/>7 kunlik + 4 haftalik"]]
    end

    subgraph UZ2["Zaxira joyi — boshqa O'zbekiston serveri yoki S3-mos saqlash"]
        REMOTEBK[["shifrlangan zaxira nusxalari"]]
    end

    INTERNET --> NGINX
    NGINX --> WEB
    NGINX -->|"/api"| API
    WEB --> API
    BOT --> API
    BOT <--> TG
    WORKER --> TG
    API --> PG
    WORKER --> PG
    PG --- VOL_PG
    API --- VOL_UP
    CRON -->|"pg_dump + uploads arxivi"| LOCALBK
    LOCALBK -->|"rsync / s3 sync, shifrlangan"| REMOTEBK
```

**Tushuntirish.** Hammasi bitta O'zbekistondagi serverda Docker Compose bilan ishlaydi: tashqariga faqat nginx (443-port, HTTPS) ochiq, baza esa faqat ichki tarmoqda — internetdan unga ulanib bo'lmaydi. Har kecha soat 03:00 da skript bazani (`pg_dump`) va yuklangan rasmlarni arxivlaydi, serverda 7 kunlik va 4 haftalik nusxani saqlaydi va shifrlangan holda O'zbekistondagi ikkinchi joyga ko'chiradi. Oyiga bir marta zaxiradan qayta tiklashni sinab ko'rish qo'llanmaga kiritiladi — tekshirilmagan zaxira zaxira emas.

Boshida bot Telegram'dan yangilanishlarni **long polling** bilan oladi (domen va sertifikatsiz ham ishlaydi); keyin kerak bo'lsa webhook'ga o'tkaziladi. Mobil ilova Expo EAS orqali yig'iladi — u yerga faqat dastur kodi boradi, foydalanuvchi ma'lumotlari emas.

---

## 7. Muhim texnik qoidalar

**Ma'lumotlar O'zbekistonda**
- Baza va barcha fayllar faqat bizning O'zbekistondagi serverda. Supabase, Firebase (ma'lumot saqlash), AWS va boshqa xorijiy bulutlar ishlatilmaydi.
- Telegram va push xabarlarida shaxsiy ma'lumot minimal: masalan, *"Y-250117-0042 yukingiz yetkazildi"*. Batafsil ma'lumot (telefon, ism) faqat bizning API'dan ilova yoki bot ichida olinadi. (8-bo'limdagi 5-savol.)

**Xavfsizlik**
- Hujjat rasmlari (`visibility = private_admin`) faqat adminlarga, yuk rasmlari faqat buyurtma tomonlariga; fayllar ochiq papkadan emas, ruxsatni tekshiradigan API orqali (yoki qisqa muddatli imzolangan havola bilan) beriladi.
- Kuzatish tokeni — kamida 128 bit tasodifiy (`secrets.token_urlsafe`), taxmin qilib bo'lmaydi.
- Yetkazish kodi — 4 xonali, 5 marta xato kiritilsa bloklanadi; bir martalik kirish kodlari va refresh tokenlar faqat hash ko'rinishida.
- Login, kod tekshirish va ochiq kuzatish endpointlariga so'rovlar soni cheklanadi (rate limit).
- Bloklangan foydalanuvchining tokenlari darhol bekor qilinadi.

**Ma'lumot formati**
- Pul — `BIGINT`, so'm. Narx = `price_per_unit_sum × units` — faqat butun sonlar.
- Vaqt — bazada `timestamptz` (UTC), foydalanuvchiga Asia/Tashkent bo'yicha. "Bugun/ertaga" va `pickup_date` Toshkent sanasi bo'yicha hisoblanadi.
- Telefon — doim `+998XXXXXXXXX` ko'rinishiga keltiriladi (qabul qiluvchini topish shunga bog'liq).

**Joylashuv**
- Haydovchi ro'yxatdan o'tishda joylashuv faqat reys `yolda` bo'lganda yuborilishini ko'radi va rozilik beradi (`location_consent_at`).
- Reys tugashi bilan ilova joylashuv yuborishni to'xtatadi, backend esa bu reysga joylashuv qabul qilmaydi.
- `LOCATION_POINTS` dagi eski nuqtalar ma'lum muddatdan keyin (masalan, 90 kun) worker tomonidan o'chiriladi.

**Kelajakka tayyorlik** (hozir qilinmaydi, lekin joy qoldirilgan)
- To'lov: `payment_method` enum + alohida `payments` servisi qo'shiladi (Click/Payme).
- SMS: `notifications` ichida `sms` kanali — mahalliy provayder ulanadi.
- Sug'urta: `insurance_requested` belgisi saqlanadi.
- Ko'p til: barcha matnlar `i18n` fayllarida.
- AI ovozli dispetcher va aniqroq ETA: ular ham xuddi shu `services/` funksiyalarini chaqiradi, alohida mantiq yozilmaydi.
- iOS: Expo bitta kod bilan.

---

## 8. Ochiq savollar (javobingiz kerak)

Quyidagilarni taxmin qilmadim, chunki ular biznes qaroringiz. Har biriga mening taklifim yozilgan — "ha" desangiz, shunday qilaman.

1. **Qaytish tarifi qanday qo'llanadi?** Yuboruvchi buyurtma berayotganda reys hali noma'lum.
   *Taklif:* buyurtma standart narx bilan ochiladi; agar u qaytish reysiga (`is_return = true`) tushsa, narx avtomatik arzon tarifga tushadi va yuboruvchiga xabar boriladi. Narx hech qachon oshmaydi.
2. **Qop va korobka narxi bir xilmi?** Hozircha sxemada bitta "joy" (qop yoki korobka) narxi bor.
   *Taklif:* boshida bir xil; farq kerak bo'lsa, tarifga `unit_type` qo'shamiz.
3. **Yuk olishda son farq qilsa nima bo'ladi?** Masalan, yuboruvchi 12 dedi, haydovchi 11 sanadi.
   *Taklif:* narx haydovchi tasdiqlagan son bo'yicha qayta hisoblanadi, yuboruvchi "Tasdiqlayman" yoki "Muammo bor" tugmasini bosadi; bosmasa 2 soatdan keyin avtomatik tasdiqlangan hisoblanadi. Yuboruvchi tasdig'i holatni to'xtatib turmaydi (haydovchi kutib qolmasin).
4. **`yetkazildi` → `yakunlandi` qachon?**
   *Taklif:* qabul qiluvchi "Oldim" bossa darhol, aks holda 24 soatdan keyin avtomatik (shu 24 soat ichida bahs ochish mumkin).
5. **Telegram va push xorijiy kanallar.** Telegram serverlari ham, Android push (Google FCM) ham O'zbekistonda emas — ularsiz bot va push umuman ishlamaydi.
   *Taklif:* ma'lumotlar bazasi to'liq O'zbekistonda; Telegram/push orqali faqat qisqa, shaxsiy ma'lumotsiz matn yuboriladi (7-bo'lim). Huquqiy jihatdan yuristga bir marta ko'rsatib olishni maslahat beraman.
6. **Xarita.** Saytda va ilovada xaritani nima bilan ko'rsatamiz?
   *Taklif:* boshida **OpenStreetMap** (bepul, saytda Leaflet kutubxonasi). O'zbekistonda Yandex xaritalari aniqroq bo'lishi mumkin, lekin kalit va limitlar kerak — keyin almashtirish oson bo'ladigan qilib yozaman. "Navigatorda ochish" tugmasi Yandex Navigator / Google Maps havolasini ochadi.
7. **Fon ishlari uchun Redis kerakmi?**
   *Taklif:* hozircha yo'q — navbat PostgreSQL jadvalida (`NOTIFICATIONS`), worker uni o'qiydi. Kamroq server qismi, kamroq tashvish.
8. **Bekor qilish qoidasi.** Yuk olingandan keyin yuboruvchi bekor qila olmasligi (faqat admin orqali) to'g'rimi?
   *Taklif:* ha, chunki yuk allaqachon mashinada.
