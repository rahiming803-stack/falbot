import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, ADMIN_ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ---------- داده‌های ثابت ----------

FORTUNE_TYPES = {
    "kamel":      {"title": "🔮 فال کامل",         "intentions": 3},
    "ehsasi":     {"title": "❤️ فال احساسی",        "intentions": 1},
    "ezdevaj":    {"title": "💍 فال ازدواج",         "intentions": 1},
    "kari_mali":  {"title": "💼 فال کاری و مالی",   "intentions": 1},
    "tanasokh":   {"title": "🌀 فال تناسخ",         "intentions": 1},
    "telesm":     {"title": "🪬 فال طلسم و جادو",   "intentions": 1},
    "dadgahi":    {"title": "⚖️ فال دادگاهی",       "intentions": 1},
    "salamati":   {"title": "🩺 فال سلامتی",        "intentions": 1},
    "tahsili":    {"title": "📚 فال تحصیلی",        "intentions": 1},
    "mohajerat":  {"title": "✈️ فال مهاجرت",        "intentions": 1},
    "tak_niyat":  {"title": "1️⃣ فال تک‌نیت",       "intentions": 1},
    "gomshodeh":  {"title": "🔍 فال گمشده",         "intentions": 1},
}

KAMEL_SUBTYPES = {
    "kamel_21": "🔮 فال کامل ۲۱ کارتی",
    "kamel_28": "🔮 فال کامل ۲۸ کارتی",
    "kamel_48": "🔮 فال کامل ۴۸ کارتی",
}

INFO_FORM_TEXT = (
    "لطفا اطلاعات زیر را کامل کنید و همه را در یک پیام ارسال کنید 👇\n\n"
    "نام:\n"
    "نام مادر:\n"
    "تاریخ تولد:\n\n"
    "اگر فال افراد دیگری را هم شامل می‌شود، اطلاعات آن‌ها را هم کامل بنویسید.\n"
    "اگر نام مادر و تاریخ تولد را نمی‌دانید، مشکلی نیست؛ بنویسید «نمی‌دانم»."
)

INTRO_TEXT = (
    "🌙 به ربات فال‌گیری خوش آمدید\n\n"
    "✨ اینجا می‌توانید انواع فال را با بالاترین کیفیت دریافت کنید\n\n"
    "🔮 فال قهوه | تاروت | ازدواج | احساسی | کاری و مالی و...\n\n"
    "برای شروع دکمه زیر را بزنید 👇"
)

WELCOME_TEXT = "سلام و خوش آمدید 🌙\n\nلطفا یکی از گزینه‌های زیر را انتخاب کنید 👇"

def build_persistent_menu():
    keyboard = [[KeyboardButton("🏠 شروع مجدد")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ---------- حالت‌های مکالمه ----------
(
    CHOOSING_TYPE,
    CHOOSING_KAMEL_SUB,
    WAITING_INTENTION,
    WAITING_INFO,
    WAITING_RECEIPT,
    WAITING_CONTACT_TYPE,
    WAITING_CONTACT_INFO,
) = range(7)


# ---------- توابع ساخت کیبورد ----------

def build_main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🧿 ثبت سفارش", callback_data="new_order"),
            InlineKeyboardButton("📜 راهنما",     callback_data="guide"),
            InlineKeyboardButton("💌 پشتیبانی",   callback_data="support"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def build_fortune_menu():
    keyboard = [[InlineKeyboardButton(data["title"], callback_data=f"type:{key}")]
                for key, data in FORTUNE_TYPES.items()]
    return InlineKeyboardMarkup(keyboard)


def build_kamel_menu():
    keyboard = [[InlineKeyboardButton(title, callback_data=f"kamel:{key}")]
                for key, title in KAMEL_SUBTYPES.items()]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_types")])
    return InlineKeyboardMarkup(keyboard)


def ordinal_fa(n):
    return {1: "اول", 2: "دوم", 3: "سوم"}.get(n, str(n))


# ---------- هندلرهای اصلی ----------

async def check_membership(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member("@destinyoracle", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_membership(user_id, context)
    
    if not is_member:
        keyboard = [[InlineKeyboardButton("🌙 عضویت در کانال", url="https://t.me/destinyoracle")]]
        await update.message.reply_text(
            "⚠️ برای استفاده از ربات ابتدا باید در کانال ما عضو شوید 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return
    
    context.user_data.clear()
    await update.message.reply_text(INTRO_TEXT, reply_markup=build_persistent_menu())
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_main_menu())


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(WELCOME_TEXT, reply_markup=build_main_menu())


async def guide_support_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "guide":
        await query.edit_message_text(
            "📜 راهنمای استفاده:\n\n"
            "۱. روی ثبت سفارش بزنید\n"
            "۲. نوع فال را انتخاب کنید\n"
            "۳. نیت خود را بنویسید\n"
            "۴. اطلاعات را کامل کنید\n"
            "۵. منتظر قیمت از ادمین باشید\n"
            "۶. واریز کنید و فیش بفرستید\n"
            "۷. پس از تأیید، فال شما ارسال می‌شود 🌙"
        )
    elif query.data == "support":
        await query.edit_message_text(
            "💌 پشتیبانی:\n\n"
            "برای ارتباط با پشتیبانی:\n"
            "@Destiny_guide"
        )


# ---------- مکالمه ثبت سفارش ----------

async def new_order_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("لطفا نوع فال را انتخاب کنید 👇", reply_markup=build_fortune_menu())
    return CHOOSING_TYPE


async def fortune_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":")[1]

    if key == "kamel":
        await query.edit_message_text("یکی از انواع فال کامل را انتخاب کنید 👇", reply_markup=build_kamel_menu())
        return CHOOSING_KAMEL_SUB

    data = FORTUNE_TYPES[key]
    context.user_data["fortune_type"] = data["title"]
    context.user_data["intentions_needed"] = data["intentions"]
    context.user_data["intentions"] = []

    await query.edit_message_text(f"✅ {data['title']} انتخاب شد.\n\nلطفا نیت خود را کامل بنویسید:")
    return WAITING_INTENTION


async def back_to_types(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("لطفا نوع فال را انتخاب کنید 👇", reply_markup=build_fortune_menu())
    return CHOOSING_TYPE


async def kamel_sub_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    key = query.data.split(":")[1]
    title = KAMEL_SUBTYPES[key]

    context.user_data["fortune_type"] = title
    context.user_data["intentions_needed"] = 3
    context.user_data["intentions"] = []

    await query.edit_message_text(f"✅ {title} انتخاب شد.\n\nلطفا نیت اول خود را کامل بنویسید:")
    return WAITING_INTENTION


async def intention_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["intentions"].append(update.message.text)

    needed = context.user_data["intentions_needed"]
    have = len(context.user_data["intentions"])

    if have < needed:
        await update.message.reply_text(f"لطفا نیت {ordinal_fa(have + 1)} خود را کامل بنویسید:")
        return WAITING_INTENTION

    await update.message.reply_text(INFO_FORM_TEXT)
    return WAITING_INFO


async def info_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["info"] = update.message.text

    await update.message.reply_text("✅ اطلاعات دریافت شد.\nمنتظر تعیین قیمت از طرف ادمین باشید ⏳")

    user = update.effective_user
    intentions_text = ""
    for i, niyat in enumerate(context.user_data["intentions"], start=1):
        label = "نیت" if context.user_data["intentions_needed"] == 1 else f"نیت {ordinal_fa(i)}"
        intentions_text += f"\n{label}: {niyat}"

    order_id = context.bot_data.get("order_counter", 0) + 1
    context.bot_data["order_counter"] = order_id

    admin_message = (
        f"📥 سفارش جدید #{order_id}\n\n"
        f"👤 کاربر: {user.full_name} (@{user.username if user.username else '---'})\n"
        f"🆔 آیدی: {user.id}\n\n"
        f"🔮 نوع فال: {context.user_data['fortune_type']}"
        f"{intentions_text}\n\n"
        f"📝 اطلاعات:\n{context.user_data['info']}\n\n"
        f"――――――――――――\n"
        f"برای تعیین قیمت، روی همین پیام Reply بزنید و بنویسید:\n"
        f"خط اول: قیمت (مثلاً 200000)\n"
        f"خط دوم: شماره کارت"
    )

    sent = await context.bot.send_message(chat_id=ADMIN_ID, text=admin_message)

    context.bot_data.setdefault("orders", {})
    context.bot_data["orders"][sent.message_id] = {
        "order_id": order_id,
        "user_chat_id": update.effective_chat.id,
        "user_id": user.id,
    }

    return WAITING_RECEIPT


# ---------- دریافت فیش از کاربر ----------

async def receipt_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # پیدا کردن سفارش این کاربر
    orders = context.bot_data.get("orders", {})
    order_msg_id = None
    order = None
    for mid, o in orders.items():
        if o.get("user_chat_id") == update.effective_chat.id and not o.get("receipt_received"):
            order_msg_id = mid
            order = o
            break

    if not order:
        await update.message.reply_text("⚠️ سفارش فعالی یافت نشد.")
        return WAITING_RECEIPT

    order["receipt_received"] = True

    await update.message.reply_text("✅ فیش شما دریافت شد.\nمنتظر تأیید ادمین باشید ⏳")

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ تأیید پرداخت", callback_data=f"confirm:{order_msg_id}"),
            InlineKeyboardButton("❌ رد پرداخت",    callback_data=f"reject:{order_msg_id}"),
        ]
    ])

    caption = f"🧾 فیش پرداخت سفارش #{order['order_id']}\n👤 کاربر: {user.full_name} (@{user.username if user.username else '---'})"

    if update.message.photo:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=update.message.photo[-1].file_id,
            caption=caption,
            reply_markup=keyboard,
        )
    elif update.message.document:
        await context.bot.send_document(
            chat_id=ADMIN_ID,
            document=update.message.document.file_id,
            caption=caption,
            reply_markup=keyboard,
        )
    else:
        await update.message.reply_text("❌ لطفا تصویر فیش را ارسال کنید.")
        return WAITING_RECEIPT

    return ConversationHandler.END


# ---------- تأیید / رد پرداخت توسط ادمین ----------

async def admin_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if update.effective_user.id != ADMIN_ID:
        await query.answer("❌ شما ادمین نیستید.")
        return

    await query.answer("✅ تأیید شد")
    order_msg_id = int(query.data.split(":")[1])
    order = context.bot_data.get("orders", {}).get(order_msg_id)

    if not order:
        await query.edit_message_caption("⚠️ سفارش یافت نشد.")
        return

    try:
        await query.edit_message_caption(
            query.message.caption + "\n\n✅ تأیید شد"
        )
    except:
        pass

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🎙 ویس",    callback_data=f"contact:voice:{order_msg_id}"),
            InlineKeyboardButton("📞 تماس تلفنی", callback_data=f"contact:call:{order_msg_id}"),
        ]
    ])

    await context.bot.send_message(
        chat_id=order["user_chat_id"],
        text=(
            "✅ پرداخت شما تأیید شد!\n\n"
            "فال شما در حال آماده‌سازی است 🔮\n\n"
            "برای ارسال فال، روش دریافت را انتخاب کنید:"
        ),
        reply_markup=keyboard,
    )


async def admin_reject_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if update.effective_user.id != ADMIN_ID:
        await query.answer("❌ شما ادمین نیستید.")
        return

    await query.answer("❌ رد شد")
    order_msg_id = int(query.data.split(":")[1])
    order = context.bot_data.get("orders", {}).get(order_msg_id)

    try:
        await query.edit_message_caption(
            query.message.caption + "\n\n❌ رد شد"
        )
    except:
        pass

    if order:
        await context.bot.send_message(
            chat_id=order["user_chat_id"],
            text="❌ پرداخت شما تأیید نشد.\n\nلطفا فیش صحیح را ارسال کنید یا با پشتیبانی تماس بگیرید:\n@Destiny_guide",
        )


# ---------- انتخاب روش دریافت فال ----------

async def contact_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts = query.data.split(":")
    contact_type = parts[1]
    order_msg_id = int(parts[2])

    order = context.bot_data.get("orders", {}).get(order_msg_id)
    if order:
        order["contact_type"] = contact_type

    if contact_type == "voice":
        await query.edit_message_text(
            "🎙 برای ارسال فال به صورت ویس،\nلطفا *آیدی تلگرام* خود را بفرستید:\n\nمثال: @username",
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(
            "📞 برای تماس تلفنی،\nلطفا *شماره موبایل* خود را بفرستید:",
            parse_mode="Markdown",
        )

    context.bot_data[f"waiting_contact_{query.message.chat_id}"] = order_msg_id


async def contact_info_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    order_msg_id = context.bot_data.get(f"waiting_contact_{chat_id}")

    if not order_msg_id:
        return

    order = context.bot_data.get("orders", {}).get(order_msg_id)
    contact_info = update.message.text
    contact_type = order.get("contact_type", "voice") if order else "voice"

    context.bot_data.pop(f"waiting_contact_{chat_id}", None)

    await update.message.reply_text(
        "✅ اطلاعات شما ثبت شد!\n\nفال شما به زودی ارسال می‌شود 🌙\nممنون از اعتماد شما 🙏"
    )

    user = update.effective_user
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"📋 اطلاعات تماس کاربر\n\n"
            f"سفارش: #{order['order_id'] if order else '---'}\n"
            f"👤 {user.full_name} (@{user.username if user.username else '---'})\n"
            f"🆔 آیدی: {user.id}\n"
            f"روش: {'🎙 ویس' if contact_type == 'voice' else '📞 تماس تلفنی'}\n"
            f"{'آیدی' if contact_type == 'voice' else 'شماره'}: {contact_info}"
        )
    )


# ---------- بخش ادمین: تعیین قیمت و شماره کارت ----------

async def admin_price_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    reply_to = message.reply_to_message

    orders = context.bot_data.get("orders", {})
    order = orders.get(reply_to.message_id)

    if not order:
        await message.reply_text("⚠️ این پیام به هیچ سفارشی متصل نیست.")
        return

    lines = [line.strip() for line in message.text.strip().split("\n") if line.strip()]
    if len(lines) < 2:
        await message.reply_text("⚠️ خط اول: قیمت — خط دوم: شماره کارت")
        return

    price, card_number = lines[0], lines[1]
    order["price"] = price
    order["card_number"] = card_number

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 شماره کارت", callback_data=f"showcard:{reply_to.message_id}"),
            InlineKeyboardButton("❌ کنسل",        callback_data=f"cancelorder:{reply_to.message_id}"),
        ]
    ])

    await context.bot.send_message(
        chat_id=order["user_chat_id"],
        text=f"💰 هزینه‌ی فال شما: {price} تومان\n\nلطفا یکی از گزینه‌های زیر را انتخاب کنید 👇",
        reply_markup=keyboard,
    )

    await message.reply_text(f"✅ قیمت برای سفارش #{order['order_id']} ارسال شد.")


async def user_show_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_msg_id = int(query.data.split(":")[1])
    order = context.bot_data.get("orders", {}).get(order_msg_id)

    if not order:
        await query.edit_message_text("⚠️ خطایی رخ داد.")
        return

    await query.edit_message_reply_markup(reply_markup=None)

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"💳 شماره کارت:\n`{order['card_number']}`\n\nلطفا فیش واریز خود را ارسال کنید 🧾",
        parse_mode="Markdown",
    )


async def user_cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_msg_id = int(query.data.split(":")[1])
    order = context.bot_data.get("orders", {}).get(order_msg_id)

    await query.edit_message_text("❌ سفارش شما لغو شد.")

    if order:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❌ کاربر سفارش #{order['order_id']} را لغو کرد."
        )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("سفارش لغو شد. برای شروع دوباره /start را بزنید.")
    return ConversationHandler.END


# ---------- اجرای برنامه ----------

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(new_order_entry, pattern="^new_order$")],
        states={
            CHOOSING_TYPE: [
                CallbackQueryHandler(fortune_type_chosen, pattern="^type:")
            ],
            CHOOSING_KAMEL_SUB: [
                CallbackQueryHandler(kamel_sub_chosen, pattern="^kamel:"),
                CallbackQueryHandler(back_to_types, pattern="^back_to_types$"),
            ],
            WAITING_INTENTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, intention_received)
            ],
            WAITING_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, info_received)
            ],
            WAITING_RECEIPT: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receipt_received)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Text(["🏠 شروع مجدد"]), restart))
    app.add_handler(order_conv)
    app.add_handler(CallbackQueryHandler(guide_support_handler, pattern="^(guide|support)$"))
    app.add_handler(CallbackQueryHandler(user_show_card,    pattern="^showcard:"))
    app.add_handler(CallbackQueryHandler(user_cancel_order, pattern="^cancelorder:"))
    app.add_handler(CallbackQueryHandler(admin_confirm_payment, pattern="^confirm:"))
    app.add_handler(CallbackQueryHandler(admin_reject_payment,  pattern="^reject:"))
    app.add_handler(CallbackQueryHandler(contact_type_chosen,   pattern="^contact:"))

    app.add_handler(MessageHandler(
        filters.User(user_id=ADMIN_ID) & filters.REPLY & filters.TEXT,
        admin_price_reply
    ))

    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        contact_info_received
    ))

    print("🤖 ربات فال در حال اجراست...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
