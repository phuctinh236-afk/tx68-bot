import os
from threading import Thread
from flask import Flask
import telebot

# 1. Khởi tạo Token Bot từ môi trường (hoặc điền trực tiếp Token vào đây)
TOKEN = os.getenv("BOT_TOKEN", "ĐIỀN_TOKEN_BOT_CỦA_BẠN_VÀO_ĐÂY")
ADMIN_USER = "@pphuc836"

bot = telebot.TeleBot(TOKEN)

# 2. Tạo Web Server giả lập để Render nhận diện PORT (Tránh lỗi Web Service)
app = Flask(__name__)

@app.route('/')
def home():
    return "TX68 Bot CSKH đang hoạt động 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# 3. Kho dữ liệu câu trả lời thông minh
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

# 4. Bộ xử lý tin nhắn
@bot.message_handler(func=lambda message: True)
def auto_reply(message):
    text = message.text.lower()
    
    # Câu chào mở đầu / Lệnh Start
    if text in ['/start', 'hi', 'hello', 'chào', 'chao', 'bot']:
        welcome_text = (
            f"🔥 **Chào mừng bạn đến với TX68 CSKH!** 🔥\n\n"
            f"Em là AI hỗ trợ tự động. Bạn cần hỏi gì cứ gõ trực tiếp nhé:\n"
            f"• *Đăng ký tài khoản thế nào?*\n"
            f"• *Cách nạp / rút tiền?*\n"
            f"• *Game nào hay / Khung giờ nổ hũ?*\n"
            f"• *Quyền lợi nâng VIP?*\n\n"
            f"💬 Hỗ trợ trực tiếp 1:1 bởi Admin: {ADMIN_USER}"
        )
        bot.reply_to(message, welcome_text, parse_mode="Markdown")
        return

    # Quét từ khóa thông minh
    matched = False
    for topic, data in KNOWLEDGE_BASE.items():
        if any(kw in text for kw in data["keywords"]):
            response_text = data["reply"].format(admin=ADMIN_USER)
            bot.reply_to(message, response_text, parse_mode="Markdown")
            matched = True
            break
            
    # Trường hợp không nhận diện được câu hỏi
    if not matched:
        bot.reply_to(
            message, 
            f"🤖 Em chưa hiểu rõ ý anh lắm! Anh có thể nhắn trực tiếp cho Admin {ADMIN_USER} để được giải đáp 1:1 ngay lập tức nhé!", 
            parse_mode="Markdown"
        )

# 5. Chạy Bot và Web Server song song
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot TX68 đã sẵn sàng hoạt động!")
    
    # Xóa Webhook cũ để tránh lỗi Conflict Error 409
    try:
        bot.remove_webhook()
    except Exception as e:
        print(f"Xóa webhook lỗi (có thể bỏ qua): {e}")
        
    bot.infinity_polling()
    
