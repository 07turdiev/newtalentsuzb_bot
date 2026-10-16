"""Ishtirokchilarga ko'rinadigan matnlar: o'zbek, rus va ingliz tillarida.

Matnni o'zgartirish uchun shu fayldagi tegishli til lug'atini tahrirlang. Kalitlar barcha
tillarda bir xil bo'lishi kerak; biror tilda kalit bo'lmasa, o'zbekcha matn ko'rsatiladi.
Admin panel matnlari texts.py da (faqat o'zbekcha).
"""

from __future__ import annotations

LANGS = {"uz": "🇺🇿 O'zbekcha", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
DEFAULT_LANG = "uz"
CHOOSE_LANG = "🌐 Tilni tanlang\n🌐 Выберите язык\n🌐 Choose your language"

UZ = {
    # --- tugmalar ---
    "btn.apply": "📝 Ariza yuborish",
    "btn.contests": "🏆 Tanlovlar",
    "btn.my_apps": "📋 Mening arizalarim",
    "btn.lang": "🌐 Til",
    "btn.cancel": "❌ Bekor qilish",
    "btn.back": "⬅️ Orqaga",
    "btn.skip": "⏭ O'tkazib yuborish",
    "btn.phone": "📱 Raqamni yuborish",
    "btn.confirm": "✅ Tasdiqlash va yuborish",
    "btn.confirm_pay": "✅ Tasdiqlash va to'lov qilish",
    "btn.edit": "✏️ Tahrirlash",
    "btn.receipt": "📎 №{id} — chek yuborish",
    "btn.receipt_again": "📎 Chekni qayta yuklash",
    "kind.solo": "👤 Yakka ijrochi",
    "kind.team": "👥 Duet, ansambl yoki jamoa",
    "status.awaiting_payment": "💳 To'lov cheki kutilmoqda",
    "status.new": "🆕 Ko'rib chiqilmoqda",
    "status.unpaid": "⚠️ To'lov tasdiqlanmadi",
    "status.accepted": "✅ Qabul qilindi",
    "status.rejected": "❌ Rad etildi",
    # --- umumiy ---
    "lang_set": "✅ Til o'zgartirildi.",
    "welcome.one": (
        "Assalomu alaykum, {name}!\n\n"
        "Bu bot orqali {contests} xalqaro tanloviga ariza topshirishingiz mumkin.\n\n"
        "Tanlovga ariza yuborish uchun «{btn}» tugmasini bosing."
    ),
    "welcome.many": (
        "Assalomu alaykum, {name}!\n\n"
        "Bu bot orqali {contests} xalqaro tanlovlariga ariza topshirishingiz mumkin.\n\n"
        "Tanlovga ariza yuborish uchun «{btn}» tugmasini bosing."
    ),
    "welcome.none": (
        "Assalomu alaykum, {name}!\n\n"
        "Hozircha ariza qabul qilinayotgan tanlov yo'q. Yangi tanlov e'lon qilinganda "
        "shu bot orqali xabar beramiz."
    ),
    "cancelled": "Bekor qilindi.",
    "no_contests": (
        "Hozircha ariza qabul qilinayotgan tanlov yo'q.\n"
        "Yangi tanlov e'lon qilinganda shu bot orqali xabar beramiz."
    ),
    "choose_contest": "Qaysi tanlovga ariza yuborasiz?",
    "contest_closed": "Kechirasiz, bu tanlovga ariza qabul qilish yakunlangan.",
    "stale": "Bu tugma faol emas.",
    "no_apps": "Siz hali ariza yubormagansiz.",
    "my_apps.head": "📋 <b>Sizning arizalaringiz</b>\n\n",
    "my_apps.hint": "To'ldirilgan ariza shaklini olish uchun 📄 tugmasini bosing.",
    "doc_not_found": "Ariza fayli topilmadi.",
    # --- ariza to'ldirish ---
    "form_started": (
        "📝 <b>{title}</b> tanloviga ariza to'ldirish boshlandi.\n"
        "To'xtatish uchun istalgan vaqtda «{cancel}» tugmasini bosing."
    ),
    "choose_kind": "Ishtirok turini tanlang:",
    "use_buttons": "Iltimos, yuqoridagi tugmalardan birini tanlang.",
    "optional_hint": "\n\n<i>Ixtiyoriy: bo'lmasa «{skip}» tugmasini bosing.</i>",
    "check_data": "🔎 <b>Ma'lumotlarni tekshiring</b>\n\n",
    "summary.contest": "Tanlov",
    "summary.kind": "Turi",
    "summary.persons": "nafar",
    "summary.more": "… yana {n} nafar",
    "consent": (
        "Hammasi to'g'rimi?\n\n"
        "«✅ Tasdiqlash» tugmasini bosib, siz ma'lumotlar to'g'riligini tasdiqlaysiz va ularni "
        "tanlov tashkilotchilariga qayta ishlash uchun berishga <b>rozilik</b> bildirasiz."
    ),
    "edit_which": "Qaysi ma'lumotni o'zgartirasiz?",
    "submitted": (
        "✅ <b>Arizangiz qabul qilindi!</b>\n"
        "Ariza raqami: <b>№{id}</b>\n\n"
        "To'ldirilgan ariza shakli ilova qilindi. Ariza ko'rib chiqilgach, natijasini shu bot "
        "orqali xabar qilamiz."
    ),
    "submit_failed": "Arizani saqlashda xatolik yuz berdi. Iltimos, birozdan so'ng qayta urinib ko'ring.",
    "video_sent": "video fayl yuborilgan",
    # --- to'lov ---
    "pay.amount": "To'lov summasi",
    "pay.card": "Karta raqami",
    "pay.holder": "Karta egasi",
    "payment": (
        "💳 <b>To'lov</b>\n\n"
        "№{id} arizangiz saqlandi. U to'lov tasdiqlangandan keyin ko'rib chiqiladi.\n\n"
        "{details}\n\n"
        "To'lovni amalga oshiring va <b>to'lov chekini</b> (skrinshot yoki PDF fayl) shu yerga yuboring."
    ),
    "receipt.prompt": "№{id} ariza uchun to'lov chekini (skrinshot yoki PDF fayl) yuboring.\n\n{details}",
    "receipt.expected": "Iltimos, to'lov chekini rasm yoki fayl ko'rinishida yuboring.",
    "receipt.later": (
        "Chekni keyinroq «{my_apps}» bo'limidan yuborishingiz mumkin. "
        "Chek yuborilmaguncha ariza ko'rib chiqilmaydi."
    ),
    "receipt.ok": (
        "✅ <b>To'lov cheki qabul qilindi!</b>\n"
        "№{id} arizangiz ko'rib chiqishga yuborildi. Natijasini shu bot orqali xabar qilamiz."
    ),
    "receipt.not_needed": "Bu ariza uchun chek yuborish shart emas.",
    # --- holat haqida xabarlar ---
    "notify.accepted": "✅ <b>{title}</b> tanloviga yuborgan №{id} arizangiz <b>qabul qilindi</b>.",
    "notify.rejected": (
        "❌ <b>{title}</b> tanloviga yuborgan №{id} arizangiz <b>rad etildi</b>.\n"
        "Savollar bo'lsa, tanlov tashkilotchilariga murojaat qiling."
    ),
    "notify.unpaid": (
        "⚠️ <b>{title}</b> tanloviga yuborgan №{id} arizangiz bo'yicha <b>to'lov tasdiqlanmadi</b>.\n"
        "Iltimos, to'lovni tekshiring va to'lov chekini qayta yuklang.\n\n{details}"
    ),
    # --- tekshiruv xatolari ---
    "err.text": "Iltimos, javobni matn ko'rinishida yozing.",
    "err.short": "Juda qisqa. Iltimos, to'liqroq yozing.",
    "err.long": "Juda uzun: ko'pi bilan {n} ta belgi bo'lishi mumkin.",
    "err.date": "Sana noto'g'ri. Kun.oy.yil ko'rinishida yozing, masalan: <code>05.03.2012</code>",
    "err.date_future": "Tug'ilgan sana kelajakda bo'lishi mumkin emas.",
    "err.phone": "Telefon raqami noto'g'ri. Masalan: <code>+998 90 123 45 67</code>",
    "err.choice": "Iltimos, pastdagi tugmalardan birini tanlang.",
    "err.participants": "Kamida 2 nafar ishtirokchini yozing, har birini alohida qatorda.",
    "err.participants_many": "Ishtirokchilar soni {n} tadan oshmasligi kerak.",
    "err.video": "Video fayl yuboring yoki <code>https://</code> bilan boshlanadigan havola yozing.",
    "err.card": "Karta raqami 16–19 ta raqamdan iborat bo'lishi kerak, masalan: <code>8600 1234 5678 9012</code>",
    # --- anketa maydonlari ---
    "f.full_name": "F.I.Sh.",
    "f.full_name.prompt": (
        "Ishtirokchining familiyasi, ismi va otasining ismini yozing:\n"
        "<i>Masalan: Karimova Madina Rustamovna</i>"
    ),
    "f.birth_date": "Tug'ilgan sana",
    "f.birth_date.prompt": "Tug'ilgan sanasini kun.oy.yil ko'rinishida yozing:\n<i>Masalan: 05.03.2012</i>",
    "f.team_name": "Jamoa / ansambl nomi",
    "f.team_name.prompt": "Jamoa yoki ansambl nomini yozing:\n<i>Masalan: «Navo» xalq cholg'ulari ansambli</i>",
    "f.participants": "Ishtirokchilar",
    "f.participants.prompt": (
        "Har bir ishtirokchining familiyasi, ismi va otasining ismini <b>alohida qatorda</b> yozing:\n"
        "<i>Karimova Madina Rustamovna\nAliyev Jasur Akmalovich</i>"
    ),
    "f.institution": "Ta'lim muassasasi",
    "f.institution.prompt": (
        "Tahsil olayotgan ta'lim muassasasini yozing (o'quvchi va talabalar uchun):\n"
        "<i>Masalan: Toshkent shahar 1-son bolalar musiqa va san'at maktabi</i>"
    ),
    "f.direction": "Yo'nalish",
    "f.direction.prompt": "Ishtirok etadigan yo'nalishni tanlang:",
    "f.direction.free": "Ishtirok etadigan yo'nalish nomini yozing:",
    "f.age_category": "Yosh toifasi",
    "f.age_category.prompt": "Ishtirok etadigan yosh toifasini tanlang:",
    "f.age_category.free": "Ishtirok etadigan yosh toifasini yozing:",
    "f.piece": "Asar nomi va muallifi",
    "f.piece.prompt": "Ijro etiladigan asar nomi va muallifini yozing:\n<i>Masalan: «Bahor valsi» — F. Shopen</i>",
    "f.teacher": "O'qituvchi",
    "f.teacher.prompt": "O'qituvchisining F.I.Sh.:",
    "f.accompanist": "Konsertmeyster",
    "f.accompanist.prompt": "Konsertmeysterining F.I.Sh.:",
    "f.parents": "Ota-onasi",
    "f.parents.prompt": (
        "Otasi va onasining F.I.Sh.:\n"
        "<i>Masalan: Karimov Rustam Aliyevich, Karimova Dilnoza Ahmedovna</i>"
    ),
    "f.head": "Muassasa rahbari",
    "f.head.prompt": "Ta'lim muassasasi rahbarining F.I.Sh. (o'quvchi va talabalar uchun):",
    "f.phone": "Telefon",
    "f.phone.prompt": (
        "Ishtirokchining telefon raqami: «{btn}» tugmasini bosing yoki qo'lda yozing.\n"
        "<i>Masalan: +998 90 123 45 67</i>"
    ),
    "f.video": "Ijro videosi",
    "f.video.prompt": (
        "Ijro videosini yuboring: video faylni shu yerga tashlang yoki havolasini yozing "
        "(YouTube, Google Drive va h.k.)."
    ),
}

RU = {
    # --- кнопки ---
    "btn.apply": "📝 Подать заявку",
    "btn.contests": "🏆 Конкурсы",
    "btn.my_apps": "📋 Мои заявки",
    "btn.lang": "🌐 Язык",
    "btn.cancel": "❌ Отмена",
    "btn.back": "⬅️ Назад",
    "btn.skip": "⏭ Пропустить",
    "btn.phone": "📱 Отправить номер",
    "btn.confirm": "✅ Подтвердить и отправить",
    "btn.confirm_pay": "✅ Подтвердить и оплатить",
    "btn.edit": "✏️ Изменить",
    "btn.receipt": "📎 №{id} — отправить чек",
    "btn.receipt_again": "📎 Загрузить чек повторно",
    "kind.solo": "👤 Солист",
    "kind.team": "👥 Дуэт, ансамбль или коллектив",
    "status.awaiting_payment": "💳 Ожидается чек об оплате",
    "status.new": "🆕 На рассмотрении",
    "status.unpaid": "⚠️ Оплата не подтверждена",
    "status.accepted": "✅ Принята",
    "status.rejected": "❌ Отклонена",
    # --- общее ---
    "lang_set": "✅ Язык изменён.",
    "welcome.one": (
        "Здравствуйте, {name}!\n\n"
        "Через этого бота вы можете подать заявку на международный конкурс {contests}.\n\n"
        "Чтобы отправить заявку, нажмите кнопку «{btn}»."
    ),
    "welcome.many": (
        "Здравствуйте, {name}!\n\n"
        "Через этого бота вы можете подать заявку на международные конкурсы {contests}.\n\n"
        "Чтобы отправить заявку, нажмите кнопку «{btn}»."
    ),
    "welcome.none": (
        "Здравствуйте, {name}!\n\n"
        "Сейчас нет конкурсов, на которые принимаются заявки. Мы сообщим через этого бота, "
        "когда будет объявлен новый конкурс."
    ),
    "cancelled": "Отменено.",
    "no_contests": (
        "Сейчас нет конкурсов, на которые принимаются заявки.\n"
        "Мы сообщим через этого бота, когда будет объявлен новый конкурс."
    ),
    "choose_contest": "На какой конкурс вы подаёте заявку?",
    "contest_closed": "К сожалению, приём заявок на этот конкурс завершён.",
    "stale": "Эта кнопка больше не активна.",
    "no_apps": "Вы ещё не подавали заявок.",
    "my_apps.head": "📋 <b>Ваши заявки</b>\n\n",
    "my_apps.hint": "Нажмите 📄, чтобы получить заполненную форму заявки.",
    "doc_not_found": "Файл заявки не найден.",
    # --- заполнение заявки ---
    "form_started": (
        "📝 Начато заполнение заявки на конкурс <b>{title}</b>.\n"
        "Чтобы остановить, в любой момент нажмите «{cancel}»."
    ),
    "choose_kind": "Выберите тип участия:",
    "use_buttons": "Пожалуйста, выберите одну из кнопок выше.",
    "optional_hint": "\n\n<i>Необязательно: если нет, нажмите «{skip}».</i>",
    "check_data": "🔎 <b>Проверьте данные</b>\n\n",
    "summary.contest": "Конкурс",
    "summary.kind": "Тип",
    "summary.persons": "чел.",
    "summary.more": "… и ещё {n} чел.",
    "consent": (
        "Всё верно?\n\n"
        "Нажимая «✅ Подтвердить», вы подтверждаете правильность данных и даёте <b>согласие</b> "
        "на их обработку организаторами конкурса."
    ),
    "edit_which": "Какие данные вы хотите изменить?",
    "submitted": (
        "✅ <b>Ваша заявка принята!</b>\n"
        "Номер заявки: <b>№{id}</b>\n\n"
        "Заполненная форма заявки приложена. После рассмотрения мы сообщим результат через этого бота."
    ),
    "submit_failed": "Не удалось сохранить заявку. Пожалуйста, попробуйте ещё раз чуть позже.",
    "video_sent": "видеофайл отправлен",
    # --- оплата ---
    "pay.amount": "Сумма оплаты",
    "pay.card": "Номер карты",
    "pay.holder": "Владелец карты",
    "payment": (
        "💳 <b>Оплата</b>\n\n"
        "Ваша заявка №{id} сохранена. Она будет рассмотрена после подтверждения оплаты.\n\n"
        "{details}\n\n"
        "Произведите оплату и отправьте сюда <b>чек об оплате</b> (скриншот или PDF-файл)."
    ),
    "receipt.prompt": "Отправьте чек об оплате (скриншот или PDF-файл) для заявки №{id}.\n\n{details}",
    "receipt.expected": "Пожалуйста, отправьте чек об оплате в виде изображения или файла.",
    "receipt.later": (
        "Вы можете отправить чек позже в разделе «{my_apps}». "
        "Пока чек не отправлен, заявка не рассматривается."
    ),
    "receipt.ok": (
        "✅ <b>Чек об оплате получен!</b>\n"
        "Ваша заявка №{id} отправлена на рассмотрение. Результат мы сообщим через этого бота."
    ),
    "receipt.not_needed": "Для этой заявки отправлять чек не нужно.",
    # --- уведомления о статусе ---
    "notify.accepted": "✅ Ваша заявка №{id} на конкурс <b>{title}</b> <b>принята</b>.",
    "notify.rejected": (
        "❌ Ваша заявка №{id} на конкурс <b>{title}</b> <b>отклонена</b>.\n"
        "Если у вас есть вопросы, обратитесь к организаторам конкурса."
    ),
    "notify.unpaid": (
        "⚠️ По вашей заявке №{id} на конкурс <b>{title}</b> <b>оплата не подтверждена</b>.\n"
        "Пожалуйста, проверьте оплату и загрузите чек повторно.\n\n{details}"
    ),
    # --- ошибки проверки ---
    "err.text": "Пожалуйста, напишите ответ текстом.",
    "err.short": "Слишком коротко. Пожалуйста, напишите подробнее.",
    "err.long": "Слишком длинно: не более {n} символов.",
    "err.date": "Неверная дата. Напишите в формате дд.мм.гггг, например: <code>05.03.2012</code>",
    "err.date_future": "Дата рождения не может быть в будущем.",
    "err.phone": "Неверный номер телефона. Например: <code>+998 90 123 45 67</code>",
    "err.choice": "Пожалуйста, выберите одну из кнопок ниже.",
    "err.participants": "Укажите не менее 2 участников, каждого с новой строки.",
    "err.participants_many": "Количество участников не должно превышать {n}.",
    "err.video": "Отправьте видеофайл или ссылку, начинающуюся с <code>https://</code>.",
    # --- поля анкеты ---
    "f.full_name": "Ф.И.О.",
    "f.full_name.prompt": "Напишите фамилию, имя и отчество участника:\n<i>Например: Каримова Мадина Рустамовна</i>",
    "f.birth_date": "Дата рождения",
    "f.birth_date.prompt": "Напишите дату рождения в формате дд.мм.гггг:\n<i>Например: 05.03.2012</i>",
    "f.team_name": "Название коллектива / ансамбля",
    "f.team_name.prompt": "Напишите название коллектива или ансамбля:\n<i>Например: Ансамбль народных инструментов «Наво»</i>",
    "f.participants": "Участники",
    "f.participants.prompt": (
        "Напишите фамилию, имя и отчество каждого участника <b>с новой строки</b>:\n"
        "<i>Каримова Мадина Рустамовна\nАлиев Жасур Акмалович</i>"
    ),
    "f.institution": "Учебное заведение",
    "f.institution.prompt": (
        "Напишите учебное заведение (для учащихся и студентов):\n"
        "<i>Например: Детская школа музыки и искусств №1 г. Ташкента</i>"
    ),
    "f.direction": "Направление",
    "f.direction.prompt": "Выберите направление участия:",
    "f.direction.free": "Напишите направление участия:",
    "f.age_category": "Возрастная категория",
    "f.age_category.prompt": "Выберите возрастную категорию:",
    "f.age_category.free": "Напишите возрастную категорию:",
    "f.piece": "Произведение и автор",
    "f.piece.prompt": "Напишите название исполняемого произведения и автора:\n<i>Например: «Весенний вальс» — Ф. Шопен</i>",
    "f.teacher": "Преподаватель",
    "f.teacher.prompt": "Ф.И.О. преподавателя:",
    "f.accompanist": "Концертмейстер",
    "f.accompanist.prompt": "Ф.И.О. концертмейстера:",
    "f.parents": "Родители",
    "f.parents.prompt": (
        "Ф.И.О. отца и матери:\n"
        "<i>Например: Каримов Рустам Алиевич, Каримова Дилноза Ахмедовна</i>"
    ),
    "f.head": "Руководитель учреждения",
    "f.head.prompt": "Ф.И.О. руководителя учебного заведения (для учащихся и студентов):",
    "f.phone": "Телефон",
    "f.phone.prompt": (
        "Номер телефона участника: нажмите «{btn}» или напишите вручную.\n"
        "<i>Например: +998 90 123 45 67</i>"
    ),
    "f.video": "Видео выступления",
    "f.video.prompt": (
        "Отправьте видео выступления: загрузите видеофайл сюда или напишите ссылку "
        "(YouTube, Google Drive и т.п.)."
    ),
}

EN = {
    # --- buttons ---
    "btn.apply": "📝 Apply",
    "btn.contests": "🏆 Competitions",
    "btn.my_apps": "📋 My applications",
    "btn.lang": "🌐 Language",
    "btn.cancel": "❌ Cancel",
    "btn.back": "⬅️ Back",
    "btn.skip": "⏭ Skip",
    "btn.phone": "📱 Share phone number",
    "btn.confirm": "✅ Confirm and submit",
    "btn.confirm_pay": "✅ Confirm and pay",
    "btn.edit": "✏️ Edit",
    "btn.receipt": "📎 №{id} — send receipt",
    "btn.receipt_again": "📎 Re-upload receipt",
    "kind.solo": "👤 Soloist",
    "kind.team": "👥 Duet, ensemble or group",
    "status.awaiting_payment": "💳 Awaiting payment receipt",
    "status.new": "🆕 Under review",
    "status.unpaid": "⚠️ Payment not confirmed",
    "status.accepted": "✅ Accepted",
    "status.rejected": "❌ Rejected",
    # --- general ---
    "lang_set": "✅ Language changed.",
    "welcome.one": (
        "Hello, {name}!\n\n"
        "With this bot you can apply for the {contests} international competition.\n\n"
        "To submit an application, press the «{btn}» button."
    ),
    "welcome.many": (
        "Hello, {name}!\n\n"
        "With this bot you can apply for the {contests} international competitions.\n\n"
        "To submit an application, press the «{btn}» button."
    ),
    "welcome.none": (
        "Hello, {name}!\n\n"
        "There are no competitions accepting applications right now. We will let you know "
        "through this bot when a new competition is announced."
    ),
    "cancelled": "Cancelled.",
    "no_contests": (
        "There are no competitions accepting applications right now.\n"
        "We will let you know through this bot when a new competition is announced."
    ),
    "choose_contest": "Which competition are you applying for?",
    "contest_closed": "Sorry, applications for this competition are closed.",
    "stale": "This button is no longer active.",
    "no_apps": "You have not submitted any applications yet.",
    "my_apps.head": "📋 <b>Your applications</b>\n\n",
    "my_apps.hint": "Press 📄 to get the completed application form.",
    "doc_not_found": "Application file not found.",
    # --- filling in the application ---
    "form_started": (
        "📝 You started an application for <b>{title}</b>.\n"
        "To stop at any time, press «{cancel}»."
    ),
    "choose_kind": "Choose the type of participation:",
    "use_buttons": "Please choose one of the buttons above.",
    "optional_hint": "\n\n<i>Optional: if not applicable, press «{skip}».</i>",
    "check_data": "🔎 <b>Please check your details</b>\n\n",
    "summary.contest": "Competition",
    "summary.kind": "Type",
    "summary.persons": "people",
    "summary.more": "… and {n} more",
    "consent": (
        "Is everything correct?\n\n"
        "By pressing «✅ Confirm» you confirm that the details are correct and give your "
        "<b>consent</b> to their processing by the competition organisers."
    ),
    "edit_which": "Which detail would you like to change?",
    "submitted": (
        "✅ <b>Your application has been received!</b>\n"
        "Application number: <b>№{id}</b>\n\n"
        "The completed application form is attached. We will let you know the result through this bot."
    ),
    "submit_failed": "Could not save the application. Please try again a little later.",
    "video_sent": "video file sent",
    # --- payment ---
    "pay.amount": "Amount",
    "pay.card": "Card number",
    "pay.holder": "Card holder",
    "payment": (
        "💳 <b>Payment</b>\n\n"
        "Your application №{id} has been saved. It will be reviewed once the payment is confirmed.\n\n"
        "{details}\n\n"
        "Please make the payment and send the <b>payment receipt</b> (screenshot or PDF file) here."
    ),
    "receipt.prompt": "Send the payment receipt (screenshot or PDF file) for application №{id}.\n\n{details}",
    "receipt.expected": "Please send the payment receipt as an image or a file.",
    "receipt.later": (
        "You can send the receipt later from «{my_apps}». "
        "The application will not be reviewed until the receipt is sent."
    ),
    "receipt.ok": (
        "✅ <b>Payment receipt received!</b>\n"
        "Your application №{id} has been sent for review. We will let you know the result through this bot."
    ),
    "receipt.not_needed": "No receipt is needed for this application.",
    # --- status notifications ---
    "notify.accepted": "✅ Your application №{id} for <b>{title}</b> has been <b>accepted</b>.",
    "notify.rejected": (
        "❌ Your application №{id} for <b>{title}</b> has been <b>rejected</b>.\n"
        "If you have any questions, please contact the competition organisers."
    ),
    "notify.unpaid": (
        "⚠️ The <b>payment was not confirmed</b> for your application №{id} for <b>{title}</b>.\n"
        "Please check your payment and upload the receipt again.\n\n{details}"
    ),
    # --- validation errors ---
    "err.text": "Please write your answer as text.",
    "err.short": "Too short. Please write in more detail.",
    "err.long": "Too long: at most {n} characters.",
    "err.date": "Invalid date. Use the dd.mm.yyyy format, for example: <code>05.03.2012</code>",
    "err.date_future": "The date of birth cannot be in the future.",
    "err.phone": "Invalid phone number. For example: <code>+998 90 123 45 67</code>",
    "err.choice": "Please choose one of the buttons below.",
    "err.participants": "List at least 2 participants, each on a new line.",
    "err.participants_many": "The number of participants must not exceed {n}.",
    "err.video": "Send a video file or a link starting with <code>https://</code>.",
    # --- form fields ---
    "f.full_name": "Full name",
    "f.full_name.prompt": "Write the participant's surname, first name and patronymic:\n<i>For example: Karimova Madina Rustamovna</i>",
    "f.birth_date": "Date of birth",
    "f.birth_date.prompt": "Write the date of birth in the dd.mm.yyyy format:\n<i>For example: 05.03.2012</i>",
    "f.team_name": "Group / ensemble name",
    "f.team_name.prompt": "Write the name of the group or ensemble:\n<i>For example: «Navo» folk instruments ensemble</i>",
    "f.participants": "Participants",
    "f.participants.prompt": (
        "Write the full name of each participant <b>on a new line</b>:\n"
        "<i>Karimova Madina Rustamovna\nAliyev Jasur Akmalovich</i>"
    ),
    "f.institution": "Educational institution",
    "f.institution.prompt": (
        "Write the educational institution (for pupils and students):\n"
        "<i>For example: Children's School of Music and Arts No. 1, Tashkent</i>"
    ),
    "f.direction": "Category",
    "f.direction.prompt": "Choose the category you are entering:",
    "f.direction.free": "Write the category you are entering:",
    "f.age_category": "Age group",
    "f.age_category.prompt": "Choose the age group:",
    "f.age_category.free": "Write the age group:",
    "f.piece": "Piece and composer",
    "f.piece.prompt": "Write the title of the piece and its composer:\n<i>For example: «Spring Waltz» — F. Chopin</i>",
    "f.teacher": "Teacher",
    "f.teacher.prompt": "Teacher's full name:",
    "f.accompanist": "Accompanist",
    "f.accompanist.prompt": "Accompanist's full name:",
    "f.parents": "Parents",
    "f.parents.prompt": (
        "Full names of the father and mother:\n"
        "<i>For example: Karimov Rustam Aliyevich, Karimova Dilnoza Ahmedovna</i>"
    ),
    "f.head": "Head of institution",
    "f.head.prompt": "Full name of the head of the educational institution (for pupils and students):",
    "f.phone": "Phone",
    "f.phone.prompt": (
        "Participant's phone number: press «{btn}» or type it in.\n"
        "<i>For example: +998 90 123 45 67</i>"
    ),
    "f.video": "Performance video",
    "f.video.prompt": (
        "Send the performance video: upload the video file here or write a link "
        "(YouTube, Google Drive, etc.)."
    ),
}

TEXTS = {"uz": UZ, "ru": RU, "en": EN}


def t(lang: str | None, key: str, **kwargs) -> str:
    text = TEXTS.get(lang or DEFAULT_LANG, UZ).get(key) or UZ[key]
    return text.format(**kwargs) if kwargs else text


def variants(key: str) -> set[str]:
    """Tugma matnining barcha tillardagi variantlari (reply-tugmalarni ushlash uchun)."""
    return {texts[key] for texts in TEXTS.values() if key in texts}
