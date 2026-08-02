import os
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 1. Khởi tạo Token Bot & Telegram Admin
TOKEN = os.getenv("BOT_TOKEN", "ĐIỀN_TOKEN_BOT_CỦA_BẠN_VÀO_ĐÂY")
ADMIN_USER = "@pphuc8386"

bot = telebot.TeleBot(TOKEN)

# 2. Tạo Web Server giả lập cho Render
app = Flask(__name__)

@app.route('/')
def home():
    return "TX68 Bot CSKH AI đang hoạt động 24/7!"

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# 3. KHO DỮ LIỆU BỘ NÃO AI (Bao phủ mọi tính năng trong App)
KNOWLEDGE_BASE = {
    "dang_ky": {
        "keywords": ["đăng ký", "dang ky", "tạo tài khoản", "tao tk", "dk sao", "đăng kí", "lập nick", "lap nick", "tạo nick"],
        "reply": "🎮 **HƯỚNG DẪN ĐĂNG KÝ TÀI KHOẢN TX68:**\n\n"
                 "1️⃣ Truy cập vào cổng game TX68.\n"
                 "2️⃣ Chọn **Đăng Ký** ở góc trên màn hình.\n"
                 "3️⃣ Điền Tên đăng nhập & Mật khẩu cá nhân.\n"
                 "4️⃣ Sau khi vào game, bấm mục **Tài khoản** xem Mã ID (Ví dụ: `8386888`).\n\n"
                 "👉 Báo ID cho Admin {admin} để nhận ngay **Code 50K Tân Thủ**!"
    },
    "nap_tien": {
        "keywords": ["nạp", "nap tien", "nạp sao", "chuyển tiền", "momo", "zalopay", "viettelpay", "usdt", "thẻ cào", "hn-pay1", "o-pay", "d-pay", "quy đổi", "điểm"],
        "reply": "💳 **HƯỚNG DẪN NẠP TIỀN TOÀN TẬP:**\n\n"
                 "📌 **Tỷ lệ quy đổi chuẩn:** `1 Điểm = 1.000 VNĐ` (Nạp 100K nhập `100`).\n\n"
                 "🔹 **Phương thức nạp:**\n"
                 "• Ngân Hàng (Cổng HN-Pay1, O-Pay, D-Pay)\n"
                 "• Ví điện tử: MOMOPAY, ZaloPay, ViettelPay\n"
                 "• Tiền điện tử: USDT (An toàn & Bảo mật)\n"
                 "• Thẻ cào điện thoại đủ mệnh giá\n\n"
                 "⚠️ *Lưu ý:* Cần chuyển đúng **Nội dung chuyển tiền** hiển thị trên màn hình để hệ thống cộng điểm tự động sau 30 giây!"
    },
    "rut_tien": {
        "keywords": ["rút", "rut tien", "rút sao", "rut bao lau", "rút tiền lâu", "không rút được", "kẹt tiền", "rút ngân hàng", "rút chưa về"],
        "reply": "🏧 **HƯỚNG DẪN RÚT TIỀN SIÊU TỐC:**\n\n"
                 "1️⃣ Vào mục **Tài Khoản** -> Chọn **Rút Tiền**.\n"
                 "2️⃣ Liên kết ngân hàng chính chủ & Nhập số tiền cần rút.\n"
                 "3️⃣ Xác nhận giao dịch (Tự động duyệt 1 - 3 phút).\n\n"
                 "👉 Sau 5 phút chưa nhận được tiền, nhắn ngay Admin {admin} kèm ID tài khoản để xử lý gấp!"
    },
    "khuyen_mai": {
        "keywords": ["khuyến mãi", "khuyen mai", "thưởng", "thuong nap", "nạp lần đầu", "hoàn trả", "điểm danh", "code", "quà", "lì xì"],
        "reply": "🎁 **SỰ KIỆN KHUYẾN MÃI HOT NHẤT TX68:**\n\n"
                 "🔥 **Thưởng Nạp Lần Đầu 100%:** Dành cho thành viên mới nạp lần đầu.\n"
                 "⭐ **Hoàn Trả Mỗi Ngày 1.5%:** Không giới hạn tiền cược cho tất cả sảnh game.\n"
                 "💎 **Báo Danh Nhận Quà VIP:** Đăng nhập mỗi ngày nhận lì xì ngẫu nhiên.\n\n"
                 "📩 Nhắn Admin {admin} đọc ID để kích hoạt KM nạp đầu!"
    },
    "vip_system": {
        "keywords": ["vip", "cấp vip", "nâng vip", "thăng hạng", "lì xì vip", "quà sinh nhật", "đặc quyền vip", "tiến trình vip", "vip 1", "vip 2"],
        "reply": "👑 **ĐẶC QUYỀN TRUNG TÂM VIP:**\n\n"
                 "📈 **Tiến trình thăng hạng:** Tự động tích lũy điểm cược (VD: VIP 1 lên VIP 2 cần `1.000.000đ` điểm cược).\n\n"
                 "🎁 **Quyền lợi Hội viên VIP:**\n"
                 "• 🧧 **Lì Xì Thăng Hạng:** Nhận thưởng nóng ngay khi lên cấp mới.\n"
                 "• 💸 **Hoàn Trả Cao Hơn:** Tỷ lệ hoàn trả cược theo ngày cực cao.\n"
                 "• 🎂 **Quà Sinh Nhật:** Tri ân quà tặng đặc biệt trong tháng sinh nhật.\n"
                 "• ⚡ **Ưu Tiên Rút Tiền:** Duyệt rút tiền hạn mức lớn, ưu tiên tốc độ cao."
    },
    "game_hot": {
        "keywords": ["game hay", "giờ nhả", "nổ hũ", "slots", "bắn cá", "đá gà", "casino", "game bài", "tài xỉu", "xổ số", "crash", "arcade", "khung giờ", "mẹo thắng"],
        "reply": "🎯 **DANH MỤC GAME & KHUNG GIỜ VÀNG TX68:**\n\n"
                 "🎮 **Sảnh HOT:** Slots Nổ Hũ (Super Ace, Fortune Gems, Dragon Gems), Bắn Cá 3D, Đá Gà, Live Casino, Game Bài, Crash, Arcade.\n\n"
                 "⏰ **Khung giờ Vàng nổ hũ / nhả phế:**\n"
                 "  - Trưa: **11h30 - 13h00**\n"
                 "  - Tối: **20h00 - 23h30**\n\n"
                 "💡 *Kinh nghiệm:* Căn đúng khung giờ vàng vào vốn để tỷ lệ nổ hũ cao nhất!"
    },
    "su_co": {
        "keywords": ["lỗi", "quên mật khẩu", "quen mk", "mất nick", "lịch sử giao dịch", "đổi thông tin", "bị khóa", "không vào được", "cskh"],
        "reply": "🛠 **HỖ TRỢ XỬ LÝ LỖI & TÀI KHOẢN:**\n\n"
                 "• **Quên MK / Khóa nick:** Cung cấp ID tài khoản cho Admin.\n"
                 "• **Xem lịch sử:** Vào *Tài Khoản* -> *Lịch Sử Giao Dịch* để tra cứu lệnh nạp/rút.\n"
                 "👉 Liên hệ Admin {admin} để được xử lý trực tiếp 1:1 trong 3 phút!"
    }
}

# 4. MENU NÚT BẤM THÔNG MINH (Inline Keyboard)
def get_main_keyboard():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎮 Đăng Ký Tài Khoản", callback_data="dang_ky"),
        InlineKeyboardButton("💳 Hướng Dẫn Nạp Tiền", callback_data="nap_tien"),
        InlineKeyboardButton("🏧 Hướng Dẫn Rút Tiền", callback_data="rut_tien"),
        InlineKeyboardButton("🎁 Sự Kiện Khuyến Mãi", callback_data="khuyen_mai"),
        InlineKeyboardButton("👑 Đặc Quyền VIP", callback_data="vip_system"),
        InlineKeyboardButton("🔥 Game Hot & Giờ Vàng", callback_data="game_hot"),
        InlineKeyboardButton("🛠 Sự Cố & Lỗi Giao Dịch", callback_data="su_co"),
        InlineKeyboardButton("💬 Chat 1:1 Với Admin", url="https://t.me/pphuc8386")
    )
    return markup

# 5. XỬ LÝ TIN NHẮN
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        f"🔥 **CHÀO MỪNG ĐẾN VỚI TX68 CSKH!** 🔥\n\n"
        f"Em là Trợ lý AI tự động. Bạn hãy **bấm trực tiếp vào các nút lựa chọn bên dưới** hoặc **gõ câu hỏi** để em hỗ trợ ngay lập tức nhé!\n\n"
        f"👤 **Admin hỗ trợ chính thức:** {ADMIN_USER}"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_main_keyboard())

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.lower()
    
    # Quét từ khóa tự động
    matched = False
    for topic, data in KNOWLEDGE_BASE.items():
        if any(kw in text for kw in data["keywords"]):
            reply_msg = data["reply"].format(admin=ADMIN_USER)
            bot.reply_to(message, reply_msg, parse_mode="Markdown", reply_markup=get_main_keyboard())
            matched = True
            break
            
    if not matched:
        fail_msg = (
            f"🤖 Em chưa hiểu rõ ý câu hỏi lắm!\n\n"
            f"Anh/chị chọn nhanh ở menu nút bấm bên dưới hoặc nhắn trực tiếp Admin **{ADMIN_USER}** để được hỗ trợ nhé!"
        )
        bot.reply_to(message, fail_msg, parse_mode="Markdown", reply_markup=get_main_keyboard())

# 6. XỬ LÝ KHI BẤM NÚT MENU
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    topic = call.data
    if topic in KNOWLEDGE_BASE:
        reply_msg = KNOWLEDGE_BASE[topic]["reply"].format(admin=ADMIN_USER)
        bot.send_message(call.message.chat.id, reply_msg, parse_mode="Markdown", reply_markup=get_main_keyboard())
        bot.answer_callback_query(call.id)

# 7. KHỞI CHẠY BOT
if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Bot AI TX68 đã sẵn sàng!")
    try:
        bot.remove_webhook()
    except Exception as e:
        print(f"Xóa webhook lỗi: {e}")
    bot.infinity_polling()
