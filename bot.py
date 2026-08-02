import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. Khởi tạo Token Bot & Telegram Admin chính thức
TOKEN = os.getenv("BOT_TOKEN", "ĐIỀN_TOKEN_BOT_CỦA_BẠN_VÀO_ĐÂY")
ADMIN_USER = "@pphuc8386"

bot = telebot.TeleBot(TOKEN)

# 2. Tạo Web Server giả lập cho Render
app = Flask(__name__)

@app.route('/')
def home():
    return "TX68 Bot CSKH đang hoạt động 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# 3. Kho dữ liệu câu trả lời
KNOWLEDGE_BASE = {
    "dang_ky": {
        "keywords": ["đăng ký", "dang ky", "tạo tài khoản", "tao tk", "dk sao", "đăng kí", "lập nick", "lap nick"],
        "reply": "🎮 **HƯỚNG DẪN ĐĂNG KÝ TX68:**\n\n1️⃣ Nhấp vào đường link chính thức của cổng game.\n2️⃣ Bấm chọn **Đăng Ký** ở góc màn hình.\n3️⃣ Tự điền Tên đăng nhập & Mật khẩu cá nhân.\n4️⃣ Liên hệ Admin {admin} để nhận ngay **Code 50K Tân Thủ** trải nghiệm!"
    },
    "nap_rut": {
        "keywords": ["nạp", "nap tien", "nạp sao", "rút tiền", "rut tien", "nạp qua đâu", "chuyển tiền", "rút sao", "rut sao"],
        "reply": "💳 **HƯỚNG DẪN NẠP / RÚT TỐC ĐỘ:**\n\n- **Nạp tiền:** Vào mục *Nạp Tiền* -> Chọn Ngân Hàng/Momo -> Chuyển đúng nội dung hiển thị.\n- **Rút tiền:** Rút về ngân hàng chính chủ, xử lý tự động từ 1 - 3 phút.\n👉 Nếu gặp sự cố kẹt tiền, nhắn ngay Admin {admin} để hỗ trợ khẩn cấp!"
    },
    "gio_vang": {
        "keywords": ["game nào hay", "giờ nào nhả", "gio nao nha", "dễ ăn", "de an", "quay giờ nào", "hũ nổ", "khung giờ", "mẹo thắng", "keo ngon"],
        "reply": "🔥 **KHUNG GIỜ VÀNG & GAME HOT TX68:**\n\n🌟 **Game dễ nổ hũ nhất:** Nổ Hũ Jackpot, Bắn Cá 3D, Tài Xỉu.\n⏰ **Khung giờ nhả thưởng cực cao:**\n  - Trưa: **11h30 - 13h00**\n  - Tối: **20h00 - 23h30**\n👉 Anh em căn đúng giờ này vào tiền tỷ lệ húp phế là cực cao!"
    },
    "vip": {
        "keywords": ["vip", "nâng vip", "nang vip", "quyền lợi vip", "cấp vip", "lên vip"],
        "reply": "👑 **ĐẶC QUYỀN NÂNG CẤP VIP:**\n\n- Điểm cược tích lũy tự động đẩy cấp VIP của bạn.\n- VIP càng cao -> Hoàn trả cược càng khủng + Quà tặng sinh nhật & Code tuần riêng biệt.\n👉 Inbox Admin {admin} đọc ID để check tiến độ lên VIP nhé!"
    }
}

# Tạo bảng Nút Bấm Tự Động (Inline Keyboard)
def create_main_keyboard():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(
        InlineKeyboardButton("🎮 Đăng ký tài khoản thế nào?", callback_data="dang_ky"),
        InlineKeyboardButton("💳 Cách nạp / rút tiền?", callback_data="nap_rut"),
        InlineKeyboardButton("🔥 Game nào hay / Khung giờ nổ hũ?", callback_data="gio_vang"),
        InlineKeyboardButton("👑 Quyền lợi nâng VIP?", callback_data="vip")
    )
    return markup

# 4. Bộ xử lý tin nhắn gõ chữ
@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    text = message.text.lower()
    
    # Câu chào mở đầu / Lệnh Start
    if text in ['/start', 'hi', 'hello', 'chào', 'chao', 'bot']:
        welcome_text = (
            f"🔥 **Chào mừng bạn đến với TX68 CSKH!** 🔥\n\n"
            f"Em là AI hỗ trợ tự động. Bạn hãy **chạm trực tiếp vào các nút lựa chọn bên dưới** để xem nhanh câu trả lời nhé:\n\n"
            f"💬 Hỗ trợ trực tiếp 1:1 bởi Admin: {ADMIN_USER}"
        )
        bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=create_main_keyboard())
        return

    # Quét từ khóa khi người dùng tự nhập chữ
    matched = False
    for topic, data in KNOWLEDGE_BASE.items():
        if any(kw in text for kw in data["keywords"]):
            response_text = data["reply"].format(admin=ADMIN_USER)
            bot.reply_to(message, response_text, parse_mode="Markdown", reply_markup=create_main_keyboard())
            matched = True
            break
            
    if not matched:
        bot.reply_to(
            message, 
            f"🤖 Em chưa hiểu rõ ý anh lắm! Anh có thể chọn các nút chức năng bên dưới hoặc nhắn trực tiếp Admin {ADMIN_USER} nhé!", 
            parse_mode="Markdown",
            reply_markup=create_main_keyboard()
        )

# 5. Bộ xử lý sự kiện khi người dùng BẤM VÀO NÚT
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    topic = call.data
    if topic in KNOWLEDGE_BASE:
        response_text = KNOWLEDGE_BASE[topic]["reply"].format(admin=ADMIN_USER)
        # Gửi tin nhắn phản hồi kèm theo Menu nút bấm tiếp theo
        bot.send_message(call.message.chat.id, response_text, parse_mode="Markdown", reply_markup=create_main_keyboard())
        # Đóng trạng thái loading của nút
        bot.answer_callback_query(call.id)

# 6. Khởi chạy Bot
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot TX68 đã sẵn sàng hoạt động!")
    try:
        bot.remove_webhook()
    except Exception as e:
        print(f"Xóa webhook lỗi: {e}")
    bot.infinity_polling()
