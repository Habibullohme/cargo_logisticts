# Yuk platformasi

O'zbekiston bozorlari orasida yig'ma yuk (qop/korobka) tashish platformasi: yuk egasi o'zi mashina topadi, haydovchi o'zi yuk topadi.

- Arxitektura: [`docs/architecture.md`](docs/architecture.md)
- Loyiha qoidalari va bosqichlar: [`CLAUDE.md`](CLAUDE.md)

## Papkalar

| Papka | Nima | Texnologiya |
|---|---|---|
| `backend/` | API va barcha biznes mantiq | Python 3.12, FastAPI, PostgreSQL |
| `bot/` | Telegram bot | aiogram 3 |
| `web/` | Veb-sayt va admin panel | Next.js (TypeScript) |
| `mobile/` | Mobil ilova (avval Android) | React Native, Expo |
| `docs/` | Hujjatlar | Markdown + Mermaid |

---

## Ubuntu'da ishga tushirish

Quyidagi buyruqlarni **Terminal**da (Ctrl+Alt+T) ketma-ket bajaring.

### 1. Kerakli dasturlarni o'rnatish (bir marta)

```bash
# Git va Docker
sudo apt update
sudo apt install -y git curl docker.io docker-compose-v2

# Docker'ni sudo'siz ishlatish uchun (keyin kompyuterdan chiqib qayta kiring)
sudo usermod -aG docker $USER

# Node.js 22 (sayt va mobil ilova uchun)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

Tekshirish: `docker --version`, `docker compose version`, `node --version` — uchalasi ham versiya raqamini chiqarishi kerak.

### 2. Loyihani yuklab olish

```bash
git clone https://github.com/habibullohme/cargo_logisticts.git
cd cargo_logisticts
```

### 3. Sozlamalar (`.env`)

```bash
cp .env.example .env
nano .env
```

`.env` ichida:

1. `POSTGRES_PASSWORD` ga o'zingiz o'ylagan parolni yozing va **xuddi shu parolni** `DATABASE_URL` ichida ham almashtiring.
2. `BOT_TOKEN` — Telegram'da [@BotFather](https://t.me/BotFather) ga `/newbot` yozing, botga nom bering va bergan tokenni shu yerga qo'ying.

Saqlash: `Ctrl+O`, `Enter`, chiqish: `Ctrl+X`.

> `.env` faylida maxfiy kalitlar bor. U gitga tushmaydi — hech kimga yubormang.

### 4. Backend, baza va botni ishga tushirish

```bash
docker compose up --build -d
```

Birinchi marta bir necha daqiqa davom etadi. Keyin tekshiring:

```bash
docker compose ps                         # db, backend, bot — hammasi "running"
curl http://localhost:8000/api/v1/health  # "Server ishlayapti" degan javob
```

- API hujjatlari brauzerda: <http://localhost:8000/docs>
- Telegram'da botingizni oching va `/start` yozing — bot salomlashadi va "✅ Server bilan aloqa bor" deb javob beradi.

Loglarni ko'rish: `docker compose logs -f backend` (yoki `bot`). Chiqish: `Ctrl+C`.

### 5. Veb-sayt

Yangi terminal oynasida:

```bash
cd web
cp .env.example .env.local
npm install
npm run dev
```

Brauzerda <http://localhost:3000> ni oching — "Server bilan aloqa bor" degan yashil blok chiqadi.

### 6. Mobil ilova (telefonda, Expo Go orqali)

1. Telefoningizga Play Market'dan **Expo Go** ilovasini o'rnating.
2. Telefon va kompyuter **bitta Wi-Fi** tarmog'ida bo'lsin.
3. Kompyuteringiz IP manzilini bilib oling:
   ```bash
   hostname -I
   ```
   Birinchi raqam kerak (masalan, `192.168.1.10`).
4. Ilovani sozlang va ishga tushiring:
   ```bash
   cd mobile
   cp .env.example .env
   nano .env          # 192.168.1.10 o'rniga o'zingizning IP manzilingiz
   npm install
   npx expo start
   ```
5. Terminalda QR-kod chiqadi — uni Expo Go ilovasi bilan skanerlang. Ilova ochiladi va "Server bilan aloqa bor" deb ko'rsatadi.

Agar "Server bilan aloqa yo'q" chiqsa:

```bash
sudo ufw status            # "active" bo'lsa, 8000-portni oching:
sudo ufw allow 8000/tcp
```

### 7. Testlar

```bash
docker compose exec backend pytest        # backend testlari
docker compose run --rm bot pytest        # bot testlari
```

### 8. To'xtatish

```bash
docker compose down        # to'xtatadi, baza ma'lumotlari saqlanib qoladi
```

> ⚠️ `docker compose down -v` bazadagi **barcha ma'lumotni o'chiradi**. Faqat nima qilayotganingizni bilsangiz ishlating.
