"""Admin panel matnlari (o'zbekcha). Ishtirokchilarga ko'rinadigan matnlar — locales.py da."""

BTN_ADMIN = "⚙️ Admin panel"
BTN_SKIP = "⏭ O'tkazib yuborish"
BTN_CANCEL = "❌ Bekor qilish"

# --- Admin panel ---
ADMIN_PANEL = "⚙️ <b>Admin panel</b>"
BTN_NEW_CONTEST = "➕ Yangi tanlov e'lon qilish"
BTN_CONTEST_LIST = "🏆 Tanlovlar va arizalar"
BTN_PAYMENT = "💳 To'lov ma'lumotlari"
BTN_STATS = "📊 Statistika"
STATS = (
    "📊 <b>Statistika</b>\n\n"
    "Bot foydalanuvchilari: <b>{users}</b> (faol: {active})\n"
    "Tanlovlar: <b>{contests}</b>\n"
    "Arizalar jami: <b>{apps}</b>"
)
NO_CONTESTS_ADMIN = "Hali tanlov yaratilmagan."
CONTESTS_HEAD = "🏆 <b>Tanlovlar</b>\n🟢 — ariza qabul qilinmoqda, 🔴 — yopiq"
CANCELLED = "Bekor qilindi."

# --- Adminlar ---
BTN_ADMINS = "👥 Adminlar"
BTN_ADMIN_ADD = "➕ Admin qo'shish"
BTN_PICK_USER = "👤 Foydalanuvchini tanlash"
BTN_YES_REMOVE = "✅ Ha, olib tashlansin"
ADMINS_HEAD = "👥 <b>Adminlar</b>"
ADMINS_MAIN = "<b>Asosiy adminlar</b> (.env faylida, botdan o'chirilmaydi):"
ADMINS_ADDED = "<b>Botdan qo'shilgan adminlar:</b>"
ADMINS_NONE = "hali yo'q"
ADMINS_HINT = (
    "<i>Adminlar tanlovlarni boshqaradi va arizalarni ko'rib chiqadi. "
    "Adminlarni faqat asosiy adminlar qo'sha va olib tashlay oladi.</i>"
)
ADMIN_ADD_PROMPT = (
    "➕ <b>Yangi admin</b>\n\n"
    f"«{BTN_PICK_USER}» tugmasini bosib, kontaktlaringizdan tanlang "
    "yoki uning Telegram ID raqamini yozing.\n"
    "<i>ID ni bilish uchun u botga /id deb yozsin.</i>"
)
ADMIN_ADD_EXPECTED = (
    f"Foydalanuvchini «{BTN_PICK_USER}» tugmasi orqali tanlang yoki ID raqamini yozing (faqat raqamlar)."
)
ADMIN_ALREADY = "Bu foydalanuvchi allaqachon admin."
ADMIN_ADDED = "✅ {name} admin etib qo'shildi."
ADMIN_NOT_STARTED = (
    "\n\n⚠️ U hali botga /start bosmagan. Bosgach, unda «⚙️ Admin panel» tugmasi paydo bo'ladi."
)
ADMIN_REMOVE_CONFIRM = "{name} adminlikdan olib tashlansinmi?"
ADMIN_REMOVED = "Admin olib tashlandi."
YOU_ARE_ADMIN = (
    "✅ Siz botda admin etib tayinlandingiz.\n"
    "Pastdagi «⚙️ Admin panel» tugmasi orqali tanlovlar va arizalarni boshqarasiz."
)
YOU_ARE_NOT_ADMIN = "Botdagi admin huquqingiz olib tashlandi."

# --- Yangi tanlov ---
NC_TITLE = (
    "<b>1/6. Tanlov nomi</b>\n\n"
    "Tanlov nomini qo'shtirnoqsiz yozing. Ariza shaklida u "
    "<i>“Nomi” Халқаро танловида иштирок этиш учун АРИЗА</i> ko'rinishida chiqadi.\n"
    "Masalan: <code>Yangi iste'dodlar</code>"
)
NC_ANNOUNCEMENT = (
    "<b>2/6. E'lon: rasm va matn</b>\n\n"
    "Tanlov <b>rasmini</b> yuboring va e'lon matnini rasm <b>izohiga</b> yozing "
    "(Telegram cheklovi: 1024 belgigacha). Qalin, kursiv va havolalar saqlanadi.\n\n"
    "E'lon ostiga «📝 Ariza yuborish» tugmasi avtomatik qo'shiladi."
)
NC_ERR_PHOTO = "Tanlov rasmi majburiy: rasmni yuboring va e'lon matnini uning izohiga yozing."
NC_ERR_CAPTION = "Rasm izohiga e'lon matnini ham yozing (rasmni qayta yuboring)."
NC_DEADLINE = (
    "<b>3/6. Ariza qabul qilish muddati</b>\n\n"
    "Oxirgi kunni kun.oy.yil ko'rinishida yozing, masalan: <code>31.10.2026</code>\n"
    "Shu kun oxirigacha ariza qabul qilinadi. Muddatsiz bo'lsa — "
    f"«{BTN_SKIP}»."
)
NC_DIRECTIONS = (
    "<b>4/6. Yo'nalishlar</b>\n\n"
    "Har bir yo'nalishni alohida qatorda yozing, masalan:\n"
    "<code>Fortepiano\nVokal\nXalq cholg'ulari\nXoreografiya</code>\n\n"
    "Ishtirokchilar ulardan birini tugma orqali tanlaydi. Ro'yxatsiz (erkin yozish) bo'lsa — "
    f"«{BTN_SKIP}»."
)
NC_AGES = (
    "<b>5/6. Yosh toifalari</b>\n\n"
    "Har birini alohida qatorda yozing, masalan:\n"
    "<code>7–10 yosh\n11–14 yosh\n15–18 yosh\n19–25 yosh</code>\n\n"
    f"Ro'yxatsiz bo'lsa — «{BTN_SKIP}»."
)
NC_VIDEO = (
    "<b>6/6. Ijro videosi</b>\n\n"
    "Ishtirokchilardan ijro videosi (fayl yoki havola) talab qilinsinmi?"
)
NC_VIDEO_YES = "🎬 Ha, talab qilinsin"
NC_VIDEO_NO = "Yo'q"
NC_PREVIEW_HEAD = "👆 E'lon shunday ko'rinadi.\n\n"
NC_PUBLISH_HINT = (
    "\n\n<b>E'lon qayerga yuborilsin?</b> Kerakli bandlarni belgilang. "
    "Hech biri belgilanmasa, tanlov faqat saqlanadi va e'lon yuborilmaydi."
)
NC_TOGGLE_CHANNEL = "Kanalga e'lon berish"
NC_TOGGLE_BROADCAST = "Barcha bot foydalanuvchilariga yuborish"
NC_SAVE_PUBLISH = "✅ Saqlash va e'lon qilish"
NC_SAVE_ONLY = "✅ Saqlash (e'lonsiz)"
NC_SAVED = "✅ Tanlov saqlandi, arizalar qabul qilinmoqda."
NC_ERR_TITLE = "Nom 3–150 belgi oralig'ida bo'lishi kerak."
NC_ERR_DEADLINE_PAST = "Muddat bugundan oldin bo'lishi mumkin emas."
NC_ERR_LIST_ITEM = "Har bir band 1–100 belgi, jami ko'pi bilan 30 ta bo'lishi kerak."
NC_UNEXPECTED = "Kutilgan javob emas. Ko'rsatmaga qarab yuboring yoki «❌ Bekor qilish»ni bosing."

# --- Tanlov kartochkasi ---
BTN_POST_CHANNEL = "📢 Kanalga e'lon qilish"
BTN_BROADCAST = "📨 Bot foydalanuvchilariga yuborish"
BTN_PREVIEW = "👁 E'lonni ko'rish"
BTN_EXCEL = "📊 Excel jadval"
BTN_ZIP = "📦 Barcha arizalar (ZIP)"
BTN_DEADLINE = "⏳ Muddatni o'zgartirish"
BTN_CLOSE = "🔒 Qabulni yopish"
BTN_OPEN = "🔓 Qabulni qayta ochish"
BTN_TO_LIST = "⬅️ Tanlovlar ro'yxati"
BTN_TO_MENU = "⬅️ Admin panel"
BTN_YES_SEND = "✅ Ha, yuborilsin"
BTN_NO = "Yo'q"
BTN_OPEN_BOT = "🤖 Botga o'tish"

CONTEST_CARD = (
    "🏆 <b>{title}</b>\n\n"
    "Holati: {state}\n"
    "Muddat: {deadline}\n"
    "Yo'nalishlar: {directions}\n"
    "Yosh toifalari: {ages}\n"
    "Ijro videosi: {video}\n\n"
    "📥 Arizalar: <b>{total}</b> (yakka: {solo}, jamoaviy: {team})\n"
    "💳 chek kutilmoqda: {awaiting_payment} · 🆕 ko'rilmagan: {new} · "
    "⚠️ to'lov tasdiqlanmagan: {unpaid}\n"
    "✅ qabul: {accepted} · ❌ rad: {rejected}\n\n"
    "🔗 Ariza havolasi:\n{link}"
)
STATE_OPEN = "🟢 Ariza qabul qilinmoqda"
STATE_CLOSED = "🔴 Qabul yopilgan"
STATE_EXPIRED = "🔴 Muddat tugagan"
DEADLINE_NONE = "cheklanmagan"
LIST_FREE = "erkin yoziladi"
VIDEO_REQUIRED = "talab qilinadi"
VIDEO_NOT_REQUIRED = "talab qilinmaydi"

EDIT_DEADLINE = (
    "⏳ <b>{title}</b>\nHozirgi muddat: {current}\n\n"
    "Yangi oxirgi kunni kun.oy.yil ko'rinishida yozing, masalan: <code>15.11.2026</code>\n"
    f"Muddatsiz qilish uchun — «{BTN_SKIP}»."
)
DEADLINE_SAVED = "✅ Muddat yangilandi."
NO_CHANNEL = "Kanal sozlanmagan: .env faylida CHANNEL_ID ni kiriting va botni qayta ishga tushiring."
POSTED = "✅ E'lon kanalga joylandi."
POST_FAILED = "Kanalga yuborib bo'lmadi. Bot kanalga admin qilib qo'shilganini tekshiring.\n\n{error}"
BROADCAST_CONFIRM = "📨 E'lon <b>{n}</b> nafar bot foydalanuvchisiga yuboriladi. Davom etasizmi?"
BROADCAST_STARTED = "📨 Bot foydalanuvchilariga yuborish boshlandi. Tugagach, natijani xabar qilaman."
BROADCAST_DONE = (
    "📨 <b>{title}</b> e'loni yuborildi.\n"
    "Yetkazildi: <b>{sent}</b>\nYetkazilmadi: {failed}"
)
NO_APPLICATIONS = "Bu tanlovga hali ariza kelmagan."
ZIP_TOO_BIG = (
    "Arizalar hajmi Telegram cheklovidan (50 MB) katta. Fayllar serverdagi "
    "data/applications/{id}/ papkasida saqlangan."
)

# --- To'lov ma'lumotlari ---
PAYMENT_INFO = (
    "💳 <b>To'lov ma'lumotlari</b>\n\n"
    "Karta raqami: {card}\n"
    "Karta egasi: {holder}\n"
    "To'lov summasi: {amount}\n\n"
    "{state}"
)
PAYMENT_ON = (
    "🟢 To'lov yoqilgan: ishtirokchi arizani tasdiqlagach, shu rekvizitlarni ko'radi va "
    "to'lov chekini yuboradi."
)
PAYMENT_OFF = "⚪️ To'lov o'chirilgan: arizalar chek so'ralmasdan to'g'ridan-to'g'ri yuboriladi."
NOT_SET = "—"
BTN_PAYMENT_EDIT = "✏️ Kiritish / o'zgartirish"
BTN_PAYMENT_OFF = "🚫 To'lovni o'chirish"
PAY_CARD = (
    "<b>1/3. Karta raqami</b>\n\n"
    "To'lov qabul qilinadigan karta raqamini yozing, masalan: <code>8600 1234 5678 9012</code>"
)
PAY_HOLDER = f"<b>2/3. Karta egasi</b>\n\nKarta egasining ismini yozing yoki «{BTN_SKIP}»."
PAY_AMOUNT = (
    "<b>3/3. To'lov summasi</b>\n\n"
    "Ishtirokchiga ko'rsatiladigan summani yozing, masalan: <code>200 000 so'm</code> "
    "yoki <code>Yakka — 200 000 so'm, jamoa — 350 000 so'm</code>.\n"
    f"Ko'rsatmaslik uchun — «{BTN_SKIP}»."
)
PAY_SAVED = "✅ To'lov ma'lumotlari saqlandi."
PAY_DISABLED = "To'lov o'chirildi."
PAY_ERR_TEXT = "1–200 belgi oralig'ida yozing."

# --- Arizani ko'rib chiqish ---
BTN_ACCEPT = "✅ Qabul qilish"
BTN_UNPAID = "💳 To'lov qilinmagan"
BTN_REJECT = "❌ Rad etish"
NEW_APPLICATION = "📥 <b>Yangi ariza №{id}</b>"
DOC_CAPTION = "📄 Ariza №{id} — to'ldirilgan shakl"
VIDEO_CAPTION = "🎬 Ariza №{id} — ijro videosi"
RECEIPT_ATTACHED = "💳 To'lov cheki ilova qilingan"
RECEIPT_RESENT = "🔁 To'lov cheki qayta yuborildi"
ALREADY_STATUS = "Holat allaqachon shunday."
