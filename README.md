# New Talents UZ — tanlov arizalari boti

Telegram bot tanlovni e'lon qiladi va ishtirokchilardan ariza qabul qiladi:

- **Admin** tanlov yaratadi (nomi, e'lon matni/rasmi, muddat, yo'nalishlar, yosh toifalari),
  uni kanalga joylaydi yoki bot foydalanuvchilariga tarqatadi.
- **Ishtirokchi** «📝 Ariza topshirish» tugmasini bosib, anketani bosqichma-bosqich to'ldiradi:
  yakka ijrochi yoki duet/ansambl/jamoa uchun.
- Bot rasmiy **Word ariza shaklini** (`templates/`) avtomatik to'ldiradi va uni ishtirokchiga hamda
  admin guruhiga yuboradi. Admin «✅ Qabul qilish» yoki «❌ Rad etish» tugmasini bosadi, ishtirokchiga
  natija haqida xabar boradi.
- Barcha arizalarni **Excel** jadval yoki **ZIP** (Word fayllar) ko'rinishida yuklab olish mumkin.

## 1. Tayyorgarlik (bir marta)

1. **Bot yaratish.** Telegramda [@BotFather](https://t.me/BotFather) → `/newbot` → token oling.
2. **Admin ID.** [@userinfobot](https://t.me/userinfobot) ga yozing, u sizning ID ingizni beradi.
   Bir nechta admin bo'lsa, har birining ID sini oling.
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

1. Botga `/start` → **⚙️ Admin panel** → **➕ Yangi tanlov e'lon qilish**. 6 qadam:
   nomi → e'lon (rasm + matn yoki faqat matn) → muddat → yo'nalishlar → yosh toifalari → video
   talab qilinadimi. Oldindan ko'rib, **Saqlash** ni bosing — ariza qabul qilish boshlanadi.
2. Tanlov kartochkasida:
   - **📢 Kanalga e'lon qilish** — e'lon «📝 Ariza topshirish» tugmasi bilan kanalga joylanadi;
   - **📨 Bot foydalanuvchilariga yuborish** — botga kirgan hammaga yuboriladi;
   - **🔗 Ariza havolasi** — `https://t.me/<bot>?start=apply_N` havolasini Instagram, sayt va
     boshqa joylarga qo'yish mumkin: bosilganda to'g'ridan-to'g'ri ariza to'ldirish boshlanadi;
   - **📊 Excel jadval**, **📦 Barcha arizalar (ZIP)** — yuklab olish;
   - **⏳ Muddatni o'zgartirish**, **🔒 Qabulni yopish / 🔓 qayta ochish**.
3. Har bir yangi ariza admin guruhiga Word fayl ko'rinishida keladi (video bo'lsa, unga javob
   sifatida). **✅ Qabul qilish** / **❌ Rad etish** ni bosing — ishtirokchiga xabar boradi.
   Tugmalarni faqat `ADMIN_IDS` dagi adminlar bosa oladi.

## 4. Moslashtirish

| Nimani | Qayerda |
|---|---|
| Botdagi barcha matnlar va tugmalar | `bot/texts.py` |
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
