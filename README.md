# New Talents UZ — tanlov arizalari boti

Telegram bot tanlovni e'lon qiladi va ishtirokchilardan ariza hamda to'lov chekini qabul qiladi:

- **Uch til:** birinchi `/start` da ishtirokchi o'zbek, rus yoki ingliz tilini tanlaydi; keyin
  «🌐 Til» tugmasi orqali o'zgartiradi. Admin panel o'zbekcha.
- **Admin** tanlov yaratadi (nomi, rasm bilan e'lon, muddat, yo'nalishlar, yosh toifalari) va
  belgilab qo'yib, e'lonni kanalga va/yoki barcha bot foydalanuvchilariga yuboradi.
- **Ishtirokchi** «📝 Ariza yuborish» tugmasini bosib, anketani bosqichma-bosqich to'ldiradi
  (yakka ijrochi yoki duet/ansambl/jamoa), so'ng to'lov qilib, **chekni** yuboradi.
- Bot rasmiy **Word ariza shaklini** (`templates/`) avtomatik to'ldiradi. Chek kelgach, admin
  guruhiga ariza va chek tushadi: «✅ Qabul qilish», «💳 To'lov qilinmagan» yoki «❌ Rad etish».
  «To'lov qilinmagan» bosilsa, ishtirokchiga chekni qayta yuklash tugmasi bilan xabar boradi.
- Barcha arizalarni **Excel** jadval yoki **ZIP** (Word fayllar) ko'rinishida yuklab olish mumkin.

## 1. Tayyorgarlik (bir marta)

1. **Bot yaratish.** Telegramda [@BotFather](https://t.me/BotFather) → `/newbot` → token oling.
2. **Admin ID.** [@userinfobot](https://t.me/userinfobot) ga yozing, u sizning ID ingizni beradi.
   Bu **asosiy adminlar** bo'ladi; boshqa adminlarni keyin botning o'zidan qo'shasiz.
3. **Admin guruhi** (tavsiya etiladi). Tashkilotchilar uchun yopiq guruh yarating va botni qo'shing.
   Bot ishga tushgach, guruhda `/id` deb yozing — guruh ID si (`-100…`) chiqadi.
4. **Kanal** (ixtiyoriy). Botni kanalga **admin** qilib qo'shing («Xabar joylash» huquqi bilan).

Hamma qiymatlar `.env` fayliga yoziladi (namuna: `.env.example`). `.env` o'zgarsa, botni qayta
ishga tushiring.

## 2. Serverga o'rnatish (Beget VPS, Ubuntu 24.04)

**Kompyuteringizdan** (PowerShell, loyiha papkasida) fayllarni serverga yuklang. `SERVER_IP` o'rniga
VPS IP manzilini yozing:

```powershell
ssh root@SERVER_IP "mkdir -p /opt/newtalentsuzb_bot"
scp -r bot templates deploy requirements.txt .env.example root@SERVER_IP:/opt/newtalentsuzb_bot/
```

**Serverda** (`ssh root@SERVER_IP`):

```bash
apt update && apt install -y python3-venv
useradd --system --home /opt/newtalentsuzb_bot --shell /usr/sbin/nologin bot

cd /opt/newtalentsuzb_bot
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

cp .env.example .env
nano .env                      # BOT_TOKEN, ADMIN_IDS, ADMIN_CHAT_ID, CHANNEL_ID ni to'ldiring

chown -R bot:bot /opt/newtalentsuzb_bot
cp deploy/newtalents-bot.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now newtalents-bot
```

Tekshirish:

```bash
systemctl status newtalents-bot      # "active (running)" bo'lishi kerak
journalctl -u newtalents-bot -f      # jonli log (chiqish: Ctrl+C)
```

Bot server qayta yoqilganda yoki xatodan keyin o'zi qayta ishga tushadi.

### Kodni yangilash

```powershell
scp -r bot templates root@SERVER_IP:/opt/newtalentsuzb_bot/
ssh root@SERVER_IP "chown -R bot:bot /opt/newtalentsuzb_bot && systemctl restart newtalents-bot"
```

### Zaxira nusxa

Hamma ma'lumot `data/` papkasida: `bot.db` (baza) va `applications/` (to'ldirilgan Word arizalar).
Kompyuterga nusxa olish:

```powershell
scp -r root@SERVER_IP:/opt/newtalentsuzb_bot/data ./zaxira
```

Beget VPS ning avtomatik bekap funksiyasini ham yoqib qo'ying.

### Kompyuterda sinab ko'rish

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env    # to'ldiring
.venv\Scripts\python -m bot
```

Bitta token bilan bot faqat bitta joyda ishlashi mumkin: kompyuterda sinayotganda serverdagisini
to'xtating (`systemctl stop newtalents-bot`), aks holda `Conflict` xatosi chiqadi.

## 3. Admin uchun yo'riqnoma

1. **⚙️ Admin panel** → **💳 To'lov ma'lumotlari** → karta raqami, karta egasi va summani kiriting.
   Karta kiritilgan bo'lsa, ishtirokchi arizani tasdiqlagach to'lov rekvizitlarini ko'radi va chek
   yuboradi; **🚫 To'lovni o'chirish** bosilsa, arizalar cheksiz yuboriladi.
2. **➕ Yangi tanlov e'lon qilish** — 6 qadam: nomi → e'lon (**rasm majburiy**, matn rasm izohida)
   → muddat → yo'nalishlar → yosh toifalari → video talab qilinadimi. Oldindan ko'rish ostida
   ikkita belgilanadigan band bor: **Kanalga e'lon berish** va **Barcha bot foydalanuvchilariga
   yuborish**. Belgilanganlariga yuboriladi; hech biri belgilanmasa, tanlov faqat saqlanadi.
   Kanal postining ostida «📝 Ariza yuborish» va «🤖 Botga o'tish» tugmalari bo'ladi.
3. Tanlov kartochkasida (keyinroq qayta e'lon qilish va boshqarish uchun):
   - **📢 Kanalga e'lon qilish** — e'lon tugmalar bilan kanalga qayta joylanadi;
   - **📨 Bot foydalanuvchilariga yuborish** — botga kirgan hammaga yuboriladi;
   - **🔗 Ariza havolasi** — `https://t.me/<bot>?start=apply_N` havolasini Instagram, sayt va
     boshqa joylarga qo'yish mumkin: bosilganda to'g'ridan-to'g'ri ariza to'ldirish boshlanadi;
   - **📊 Excel jadval**, **📦 Barcha arizalar (ZIP)** — yuklab olish;
   - **⏳ Muddatni o'zgartirish**, **🔒 Qabulni yopish / 🔓 qayta ochish**.
4. Ishtirokchi chek yuborgach, admin guruhiga Word ariza va uning ostida chek keladi (video bo'lsa,
   u ham). Chek ostidagi tugmalar: **✅ Qabul qilish**, **💳 To'lov qilinmagan**, **❌ Rad etish** —
   ishtirokchiga o'z tilida xabar boradi. Tugmalarni faqat adminlar bosa oladi.
5. **👥 Adminlar** (faqat asosiy adminlarda, ya'ni `.env` dagi `ADMIN_IDS`): **➕ Admin qo'shish**
   → «👤 Foydalanuvchini tanlash» bilan kontaktlardan tanlang yoki Telegram ID sini yozing.
   Yangi admin darhol kuchga kiradi (botni qayta ishga tushirish shart emas) va unga xabar boradi;
   🗑 tugmasi bilan olib tashlanadi. Qo'shilgan adminlar tanlov va arizalarni boshqaradi, lekin
   adminlar ro'yxatini o'zgartira olmaydi. `ADMIN_CHAT_ID` bo'sh bo'lsa, yangi arizalar barcha
   adminlarga keladi.

## 4. Moslashtirish

| Nimani | Qayerda |
|---|---|
| Ishtirokchiga ko'rinadigan matnlar (uz/ru/en) | `bot/locales.py` |
| Admin panel matnlari | `bot/texts.py` |
| Anketa savollari, tartibi, majburiy/ixtiyoriyligi | `bot/forms.py` (`SOLO_FIELDS`, `TEAM_FIELDS`) |
| Word shakllar | `templates/solo.docx`, `templates/team.docx` |

Word shablonni o'zgartirsangiz: sarlavhadagi `Танлов номи` so'zi tanlov nomi bilan almashtiriladi,
qatorlar esa yorlig'i bo'yicha topiladi (ro'yxat `bot/docgen.py` → `LABELS`). Yorliq matnini
o'zgartirsangiz, `LABELS` ni ham moslang.

## 5. Bilish kerak bo'lgan cheklovlar

- Bot qayta ishga tushirilsa, **yarim to'ldirilgan** anketalar yo'qoladi (yuborilganlari saqlanadi).
  Kodni yangilashni ariza oqimi kam paytda qiling.
- Telegram bot 50 MB dan katta fayl yubora olmaydi: ZIP juda katta bo'lsa, fayllarni serverdagi
  `data/applications/<tanlov_id>/` papkasidan oling.
- Anketada shaxsga doir ma'lumotlar (F.I.Sh., tug'ilgan sana, telefon) yig'iladi. O'zbekiston
  «Shaxsga doir ma'lumotlar to'g'risida»gi qonuni talablarini (ma'lumotlarni saqlash joyi) yurist bilan
  aniqlashtiring.
