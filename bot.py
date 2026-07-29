import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import json
import os
import time

TOKEN = "8909171042:AAH8MUy9h_k_e2QNw4RXcOWWrp1jxMipj78"
ADMIN_ID = 7775328471
SUPPORT_USERNAME = "iWas_Mamad"

DATA_FILE = "users_data.json"
SUPPORT_FILE = "support_data.json"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_support():
    if os.path.exists(SUPPORT_FILE):
        with open(SUPPORT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_support(data):
    with open(SUPPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("👥 حساب کاربری", callback_data="profile")],
        [InlineKeyboardButton("🔗 لینک دعوت", callback_data="invite")],
        [InlineKeyboardButton("📞 پشتیبانی", callback_data="support")]
    ]
    return InlineKeyboardMarkup(keyboard)

def admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton("📊 آمار کاربران", callback_data="admin_stats")],
        [InlineKeyboardButton("📩 پیام‌های پشتیبانی", callback_data="admin_support_msgs")],
        [InlineKeyboardButton("➕ افزایش دعوت", callback_data="admin_add_invite")],
        [InlineKeyboardButton("➖ کاهش دعوت", callback_data="admin_remove_invite")],
        [InlineKeyboardButton("📢 پیام همگانی", callback_data="admin_broadcast")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "کاربر"
    username = user.username or "ندارد"
    
    bot_username = (await context.bot.get_me()).username
    
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {
            "invites": 0,
            "username": username,
            "first_name": first_name,
            "invite_link": f"https://t.me/{bot_username}?start={user_id_str}"
        }
        save_data(data)
    
    args = context.args
    if args and args[0].isdigit():
        referrer_id = args[0]
        if int(referrer_id) != user_id:
            data = load_data()
            if referrer_id in data:
                data[referrer_id]["invites"] += 1
                save_data(data)
                try:
                    await context.bot.send_message(
                        chat_id=int(referrer_id),
                        text=f"🎉 کاربر {first_name} با لینک دعوت شما به ربات پیوست!\n"
                             f"👥 تعداد دعوت‌های شما: {data[referrer_id]['invites']}"
                    )
                except:
                    pass
    
    if user_id == ADMIN_ID:
        welcome_text = f"👋 سلام ادمین {first_name}!\n\n👑 به پنل مدیریت خوش آمدی.\nاز دکمه‌های زیر استفاده کن:"
        await update.message.reply_text(welcome_text, reply_markup=admin_panel_keyboard())
        return
    
    welcome_text = f"👋 سلام {first_name} به ربات خوش آمدی..👋"
    await update.message.reply_text(welcome_text, reply_markup=main_menu_keyboard())

async def profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        await query.edit_message_text("❌ اطلاعات شما پیدا نشد! لطفاً دوباره /start رو بزنید.")
        return
    
    user_data = data[user_id_str]
    profile_text = f"👤 اطلاعات حساب کاربری\n\n"
    profile_text += f"👤 نام: {user_data.get('first_name', 'ندارد')}\n"
    profile_text += f"🆔 آیدی: {user_id}\n"
    profile_text += f"👥 تعداد دعوت‌ها: {user_data.get('invites', 0)}"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]
    await query.edit_message_text(profile_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def invite_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = load_data()
    user_id_str = str(user_id)
    
    if user_id_str not in data:
        await query.edit_message_text("❌ اطلاعات شما پیدا نشد! لطفاً دوباره /start رو بزنید.")
        return
    
    user_data = data[user_id_str]
    invite_text = f"🔗 لینک دعوت شما\n\n"
    invite_text += f"👥 تعداد دعوت‌ها: {user_data.get('invites', 0)}\n"
    invite_text += f"🔗 لینک: {user_data.get('invite_link', 'ندارد')}\n\n"
    invite_text += "💡 این لینک رو برای دوستانت بفرست تا به ربات بیان!"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")]]
    await query.edit_message_text(invite_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard), disable_web_page_preview=True)

async def support_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    support_text = f"📞 پشتیبانی\n\n"
    support_text += f"برای ارتباط با پشتیبانی روی دکمه زیر کلیک کن:\n"
    support_text += f"@{SUPPORT_USERNAME}"
    
    keyboard = [[InlineKeyboardButton("📩 ارتباط با پشتیبانی", url=f"https://t.me/{SUPPORT_USERNAME}")]]
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    
    await query.edit_message_text(
        support_text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def back_to_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['admin_mode'] = False
    user = query.from_user
    
    if user.id == ADMIN_ID:
        welcome_text = f"👋 سلام ادمین {user.first_name}!\n\n👑 به پنل مدیریت خوش آمدی.\nاز دکمه‌های زیر استفاده کن:"
        await query.edit_message_text(welcome_text, reply_markup=admin_panel_keyboard())
        return
    
    welcome_text = f"👋 سلام {user.first_name} به ربات خوش آمدی..👋"
    await query.edit_message_text(welcome_text, reply_markup=main_menu_keyboard())

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("⛔ شما دسترسی ندارید!")
        return
    
    data = load_data()
    if not data:
        text = "📭 هنوز کاربری ثبت نشده!"
    else:
        total_users = len(data)
        total_invites = sum(user.get('invites', 0) for user in data.values())
        text = f"📊 آمار ربات\n\n👥 تعداد کل کاربران: {total_users}\n🔗 مجموع دعوت‌ها: {total_invites}\n\n🏆 ۱۰ کاربر برتر:\n"
        sorted_users = sorted(data.items(), key=lambda x: x[1].get('invites', 0), reverse=True)[:10]
        for i, (user_id, info) in enumerate(sorted_users, 1):
            text += f"{i}. {info.get('first_name', 'ناشناس')} - {info.get('invites', 0)} دعوت\n"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="back_to_main")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_support_msgs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("⛔ شما دسترسی ندارید!")
        return
    
    support_data = load_support()
    if not support_data:
        text = "📭 هیچ پیام پشتیبانی جدیدی وجود ندارد!"
    else:
        text = "📩 لیست پیام‌های پشتیبانی:\n\n"
        for msg_id, info in list(support_data.items())[:10]:
            text += f"• {info.get('user_name', 'ناشناس')} (@{info.get('username', 'ندارد')})\n  ⏰ {info.get('time', 'نامشخص')}\n  🆔 {info.get('user_id')}\n\n"
        if len(support_data) > 10:
            text += f"... و {len(support_data)-10} پیام دیگر"
    
    keyboard = [[InlineKeyboardButton("🔙 بازگشت به پنل", callback_data="back_to_main")]]
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def admin_add_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("⛔ شما دسترسی ندارید!")
        return
    await query.message.reply_text("➕ افزایش دعوت کاربر\n\nدستور زیر رو وارد کن:\n/addinvite [آیدی کاربر] [تعداد]\n\nمثال:\n/addinvite 7775328471 5", parse_mode="Markdown")

async def admin_remove_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("⛔ شما دسترسی ندارید!")
        return
    await query.message.reply_text("➖ کاهش دعوت کاربر\n\nدستور زیر رو وارد کن:\n/removeinvite [آیدی کاربر] [تعداد]\n\nمثال:\n/removeinvite 7775328471 3", parse_mode="Markdown")

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID:
        await query.message.reply_text("⛔ شما دسترسی ندارید!")
        return
    
    context.user_data['broadcast_mode'] = True
    await query.message.reply_text(
        "📢 ارسال پیام همگانی\n\n"
        "پیام خود را بفرستید تا برای همه کاربران ارسال شود.\n"
        "⚠️ این پیام برای همه کاربران ربات فرستاده می‌شود!\n\n"
        "برای لغو /cancel رو بزنید."
    )

async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_ID:
        return
    if not context.user_data.get('broadcast_mode'):
        return
    if update.message.text and update.message.text.startswith('/'):
        return
    
    message = update.message
    data = load_data()
    
    if not data:
        await message.reply_text("❌ هیچ کاربری برای ارسال پیام وجود ندارد!")
        context.user_data['broadcast_mode'] = False
        return
    
    await message.reply_text("📤 در حال ارسال پیام همگانی...")
    
    success_count = 0
    fail_count = 0
    
    for user_id in data.keys():
        try:
            if message.text:
                await context.bot.send_message(chat_id=int(user_id), text=f"📢 پیام همگانی:\n\n{message.text}", parse_mode="Markdown")
            elif message.photo:
                await context.bot.send_photo(chat_id=int(user_id), photo=message.photo[-1].file_id, caption=f"📢 پیام همگانی:\n\n{message.caption or ''}")
            elif message.voice:
                await context.bot.send_voice(chat_id=int(user_id), voice=message.voice.file_id, caption="📢 پیام همگانی")
            elif message.document:
                await context.bot.send_document(chat_id=int(user_id), document=message.document.file_id, caption=f"📢 پیام همگانی:\n\n{message.caption or ''}")
            else:
                await message.reply_text("❌ نوع فایل پشتیبانی نمی‌شود!")
                context.user_data['broadcast_mode'] = False
                return
            success_count += 1
            time.sleep(0.05)
        except:
            fail_count += 1
    
    context.user_data['broadcast_mode'] = False
    await message.reply_text(f"✅ پیام همگانی ارسال شد!\n\n📤 ارسال موفق: {success_count}\n❌ ارسال ناموفق: {fail_count}")

async def add_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ شما دسترسی ندارید!")
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("❌ استفاده صحیح:\n/addinvite [آیدی] [تعداد]\n\nمثال: /addinvite 7775328471 5", parse_mode="Markdown")
        return
    try:
        user_id = args[0]
        count = int(args[1])
        if count <= 0:
            await update.message.reply_text("❌ تعداد باید بیشتر از صفر باشه!")
            return
        data = load_data()
        if user_id not in data:
            await update.message.reply_text(f"❌ کاربر با آیدی {user_id} پیدا نشد!", parse_mode="Markdown")
            return
        data[user_id]["invites"] += count
        save_data(data)
        await update.message.reply_text(f"✅ {count} دعوت به کاربر {user_id} اضافه شد.\n📊 مجموع دعوت‌ها: {data[user_id]['invites']}", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ تعداد باید عدد باشد!")

async def remove_invite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ شما دسترسی ندارید!")
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("❌ استفاده صحیح:\n/removeinvite [آیدی] [تعداد]\n\nمثال: /removeinvite 7775328471 3", parse_mode="Markdown")
        return
    try:
        user_id = args[0]
        count = int(args[1])
        if count <= 0:
            await update.message.reply_text("❌ تعداد باید بیشتر از صفر باشه!")
            return
        data = load_data()
        if user_id not in data:
            await update.message.reply_text(f"❌ کاربر با آیدی {user_id} پیدا نشد!", parse_mode="Markdown")
            return
        data[user_id]["invites"] = max(0, data[user_id]["invites"] - count)
        save_data(data)
        await update.message.reply_text(f"✅ {count} دعوت از کاربر {user_id} کم شد.\n📊 مجموع دعوت‌ها: {data[user_id]['invites']}", parse_mode="Markdown")
    except ValueError:
        await update.message.reply_text("❌ تعداد باید عدد باشد!")

async def cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    context.user_data['reply_to_user'] = None
    context.user_data['reply_msg_id'] = None
    context.user_data['admin_mode'] = False
    context.user_data['broadcast_mode'] = False
    await update.message.reply_text("✅ عملیات لغو شد!")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel_reply))
    app.add_handler(CommandHandler("addinvite", add_invite))
    app.add_handler(CommandHandler("removeinvite", remove_invite))
    
    app.add_handler(CallbackQueryHandler(profile_callback, pattern="profile"))
    app.add_handler(CallbackQueryHandler(invite_callback, pattern="invite"))
    app.add_handler(CallbackQueryHandler(support_callback, pattern="support"))
    app.add_handler(CallbackQueryHandler(back_to_main, pattern="back_to_main"))
    app.add_handler(CallbackQueryHandler(admin_stats, pattern="admin_stats"))
    app.add_handler(CallbackQueryHandler(admin_support_msgs, pattern="admin_support_msgs"))
    app.add_handler(CallbackQueryHandler(admin_add_invite, pattern="admin_add_invite"))
    app.add_handler(CallbackQueryHandler(admin_remove_invite, pattern="admin_remove_invite"))
    app.add_handler(CallbackQueryHandler(admin_broadcast, pattern="admin_broadcast"))
    
    app.add_handler(MessageHandler((filters.PHOTO | filters.VOICE | filters.TEXT) & ~filters.COMMAND, handle_broadcast), group=1)
    
    print("🚀 ربات روشن شد...")
    print(f"👑 آیدی ادمین: {ADMIN_ID}")
    print(f"📞 پشتیبانی: @{SUPPORT_USERNAME}")
    app.run_polling()

if __name__ == "__main__":
    main()
