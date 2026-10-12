"""Botdagi barcha matnlar shu yerda. Matnni o'zgartirish uchun faqat shu faylni tahrirlang."""

# --- Tugmalar ---
BTN_APPLY = "📝 Ariza topshirish"
BTN_CONTESTS = "🏆 Tanlovlar"
BTN_MY_APPS = "📋 Mening arizalarim"
BTN_ADMIN = "⚙️ Admin panel"
BTN_CANCEL = "❌ Bekor qilish"
BTN_BACK = "⬅️ Orqaga"
BTN_SKIP = "⏭ O'tkazib yuborish"
BTN_PHONE = "📱 Raqamni yuborish"

KIND_LABELS = {
    "solo": "👤 Yakka ijrochi",
    "team": "👥 Duet, ansambl yoki jamoa",
}

STATUS = {
    "new": "🆕 Ko'rib chiqilmoqda",
    "accepted": "✅ Qabul qilindi",
    "rejected": "❌ Rad etildi",
}

# --- Foydalanuvchi ---
WELCOME = (
    "Assalomu alaykum, {name}!\n\n"
    "Bu bot orqali ijodiy tanlovlarga ariza topshirishingiz mumkin.\n\n"
    f"{BTN_APPLY} — ochiq tanlovga ariza to'ldirish\n"
    f"{BTN_CONTESTS} — e'lon qilingan tanlovlar\n"
    f"{BTN_MY_APPS} — yuborgan arizalaringiz va ularning holati"
)
CANCELLED = "Bekor qilindi. Asosiy menyu:"
NO_CONTESTS = (
    "Hozircha ariza qabul qilinayotgan tanlov yo'q.\n"
    "Yangi tanlov e'lon qilinganda shu bot orqali xabar beramiz."
)
CHOOSE_CONTEST = "Qaysi tanlovga ariza topshirasiz?"
CONTEST_CLOSED = "Kechirasiz, bu tanlovga ariza qabul qilish yakunlangan."
NO_APPS = "Siz hali ariza topshirmagansiz."
MY_APPS_HEAD = "📋 <b>Sizning arizalaringiz</b>\n"
MY_APPS_HINT = "\nTo'ldirilgan ariza shaklini olish uchun raqamini bosing."
DOC_NOT_FOUND = "Ariza fayli topilmadi."
STALE_BUTTON = "Bu tugma faol emas."

# --- Ariza to'ldirish ---
FORM_STARTED = (
    "📝 <b>{title}</b> tanloviga ariza to'ldirish boshlandi.\n"
    f"To'xtatish uchun istalgan vaqtda «{BTN_CANCEL}» tugmasini bosing."
)
CHOOSE_KIND = "Ishtirok turini tanlang:"
USE_BUTTONS = "Iltimos, yuqoridagi tugmalardan birini tanlang."
OPTIONAL_HINT = f"\n\n<i>Ixtiyoriy: bo'lmasa «{BTN_SKIP}» tugmasini bosing.</i>"
CHECK_DATA = "🔎 <b>Ma'lumotlarni tekshiring</b>\n\n"
CONSENT = (
    "Hammasi to'g'rimi?\n\n"
    "«✅ Tasdiqlash» tugmasini bosib, siz ma'lumotlar to'g'riligini tasdiqlaysiz va ularni "
    "tanlov tashkilotchilariga qayta ishlash uchun berishga <b>rozilik</b> bildirasiz "
    "(ariza shaklidagi «розилик имзоси» o'rniga)."
)
BTN_CONFIRM = "✅ Tasdiqlash va yuborish"
BTN_EDIT = "✏️ Tahrirlash"
EDIT_WHICH = "Qaysi ma'lumotni o'zgartirasiz?"
SUBMITTED = (
    "✅ <b>Arizangiz qabul qilindi!</b>\n"
    "Ariza raqami: <b>№{id}</b>\n\n"
    "To'ldirilgan ariza shakli ilova qilindi. Ariza ko'rib chiqilgach, natijasini shu bot "
    "orqali xabar qilamiz."
)
SUBMIT_FAILED = (
    "Arizani saqlashda xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring."
)
USER_STATUS = {
    "accepted": "✅ <b>{title}</b> tanloviga yuborgan №{id} arizangiz <b>qabul qilindi</b>.",
    "rejected": (
        "❌ <b>{title}</b> tanloviga yuborgan №{id} arizangiz <b>rad etildi</b>.\n"
        "Savollar bo'lsa, tanlov tashkilotchilariga murojaat qiling."
    ),
}

# --- Tekshiruv xatolari ---
ERR_TEXT = "Iltimos, javobni matn ko'rinishida yozing."
ERR_SHORT = "Juda qisqa. Iltimos, to'liqroq yozing."
ERR_LONG = "Juda uzun: ko'pi bilan {n} ta belgi bo'lishi mumkin."
ERR_DATE = "Sana noto'g'ri. Kun.oy.yil ko'rinishida yozing, masalan: <code>05.03.2012</code>"
ERR_DATE_FUTURE = "Tug'ilgan sana kelajakda bo'lishi mumkin emas."
ERR_PHONE = "Telefon raqami noto'g'ri. Masalan: <code>+998 90 123 45 67</code>"
ERR_CHOICE = "Iltimos, pastdagi tugmalardan birini tanlang."
ERR_PARTICIPANTS = "Kamida 2 nafar ishtirokchini yozing, har birini alohida qatorda."
ERR_PARTICIPANTS_MANY = "Ishtirokchilar soni {n} tadan oshmasligi kerak."
ERR_VIDEO = "Video fayl yuboring yoki <code>https://</code> bilan boshlanadigan havola yozing."

# --- Admin ---
ADMIN_PANEL = "⚙️ <b>Admin panel</b>"
BTN_NEW_CONTEST = "➕ Yangi tanlov e'lon qilish"
BTN_CONTEST_LIST = "🏆 Tanlovlar va arizalar"
BTN_STATS = "📊 Statistika"
STATS = (
    "📊 <b>Statistika</b>\n\n"
    "Bot foydalanuvchilari: <b>{users}</b> (faol: {active})\n"
    "Tanlovlar: <b>{contests}</b>\n"
    "Arizalar jami: <b>{apps}</b>"
)
NO_CONTESTS_ADMIN = "Hali tanlov yaratilmagan."
CONTESTS_HEAD = "🏆 <b>Tanlovlar</b>\n🟢 — ariza qabul qilinmoqda, 🔴 — yopiq"

NC_TITLE = (
    "<b>1/6. Tanlov nomi</b>\n\n"
    "Tanlov nomini qo'shtirnoqsiz yozing. Ariza shaklida u "
    "<i>“Nomi” Халқаро танловида иштирок этиш учун АРИЗА</i> ko'rinishida chiqadi.\n"
    "Masalan: <code>Yangi iste'dodlar</code>"
)
NC_ANNOUNCEMENT = (
    "<b>2/6. E'lon matni</b>\n\n"
    "Kanalga va foydalanuvchilarga yuboriladigan e'lonni yuboring. Rasm bilan "
    "(matnni rasm izohiga yozing) yoki faqat matn bo'lishi mumkin. Qalin, kursiv va "
    "havolalar saqlanadi.\n\n"
    "E'lon ostiga «📝 Ariza topshirish» tugmasi avtomatik qo'shiladi."
)
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
NC_SAVE = "✅ Saqlash va qabulni ochish"
NC_SAVED = "✅ Tanlov saqlandi, arizalar qabul qilinmoqda."
NC_ERR_TITLE = "Nom 3–150 belgi oralig'ida bo'lishi kerak."
NC_ERR_ANNOUNCEMENT = "E'lonni matn yoki rasm (izohi bilan) ko'rinishida yuboring."
NC_ERR_DEADLINE_PAST = "Muddat bugundan oldin bo'lishi mumkin emas."
NC_ERR_LIST = "Ro'yxatni matn ko'rinishida, har bir bandni alohida qatorda yozing."
NC_ERR_LIST_ITEM = "Har bir band 1–100 belgi, jami ko'pi bilan 30 ta bo'lishi kerak."
NC_UNEXPECTED = "Kutilgan javob emas. Ko'rsatmaga qarab yuboring yoki «❌ Bekor qilish»ni bosing."

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

CONTEST_CARD = (
    "🏆 <b>{title}</b>\n\n"
    "Holati: {state}\n"
    "Muddat: {deadline}\n"
    "Yo'nalishlar: {directions}\n"
    "Yosh toifalari: {ages}\n"
    "Ijro videosi: {video}\n\n"
    "📥 Arizalar: <b>{total}</b> (yakka: {solo}, jamoaviy: {team})\n"
    "🆕 ko'rilmagan: {new} · ✅ qabul: {accepted} · ❌ rad: {rejected}\n\n"
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
NO_CHANNEL ="Kanal sozlanmagan: .env faylida CHANNEL_ID ni kiriting va botni qayta ishga tushiring."
POSTED = "✅ E'lon kanalga joylandi."
POST_FAILED = "Kanalga yuborib bo'lmadi. Bot kanalga admin qilib qo'shilganini tekshiring.\n\n{error}"
BROADCAST_CONFIRM = (
    "📨 E'lon <b>{n}</b> nafar bot foydalanuvchisiga yuboriladi. Davom etasizmi?"
)
BROADCAST_STARTED = "Yuborish boshlandi. Tugagach, natijani xabar qilaman."
BROADCAST_DONE = (
    "📨 <b>{title}</b> e'loni yuborildi.\n"
    "Yetkazildi: <b>{sent}</b>\nYetkazilmadi: {failed}"
)
NO_APPLICATIONS = "Bu tanlovga hali ariza kelmagan."
ZIP_TOO_BIG = (
    "Arizalar hajmi Telegram cheklovidan (50 MB) katta. Fayllar serverdagi "
    "data/applications/{id}/ papkasida saqlangan."
)

BTN_ACCEPT = "✅ Qabul qilish"
BTN_REJECT = "❌ Rad etish"
NEW_APPLICATION = "📥 <b>Yangi ariza №{id}</b>"
VIDEO_CAPTION = "🎬 Ariza №{id} — ijro videosi"
ALREADY_STATUS = "Holat allaqachon shunday."
