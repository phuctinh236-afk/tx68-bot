import os
import re
import random
from threading import Thread
from flask import Flask, request, jsonify
from flask_cors import CORS
import telebot

# ==================== 1. KHỞI TẠO BOT & NHÓM TELEGRAM ====================
TOKEN_AI = "8871256449:AAGaIlrsMouC2zT-aAmykabNltYSb-2WXCM"       # Bot 1: Bắn câu trả lời AI
TOKEN_STAFF = "8576597700:AAG6p0YhWf1-QXMwR1vNtHxx6r7eAFxvRFU"    # Bot 2: Bắn tin nhắn khách hỏi
STAFF_GROUP_ID = "-1004444253619"                                 # ID Nhóm CSKH

bot_ai = telebot.TeleBot(TOKEN_AI)
bot_staff = telebot.TeleBot(TOKEN_STAFF)

app = Flask(__name__)
CORS(app)  # Mở CORS để kết nối với Web Game

user_to_code = {}
code_to_user = {}
outbound_messages = {} # Bộ nhớ chờ tin nhắn trả về Game

def get_or_assign_code(user_id):
    """Gán mã 6 số cố định cho mỗi người chơi"""
    user_id_str = str(user_id)
    if user_id_str not in user_to_code:
        while True:
            new_code = f"{random.randint(100000, 999999)}"
            if new_code not in code_to_user:
                break
        user_to_code[user_id_str] = new_code
        code_to_user[new_code] = user_id_str
    return user_to_code[user_id_str]

# ==================== 2. KHO BỘ NÃO AI ====================
KNOWLEDGE_BASE = {
    "nap_tien": {
        "keywords": ["nạp", "nap tien", "momo", "zalopay", "usdt", "hn-pay1", "o-pay", "d-pay", "thẻ cào"],
        "reply": "💳 **HƯỚNG DẪN NẠP TIỀN:** Tỷ lệ quy đổi 1=1K. Bạn vào mục Nạp Tiền chọn cổng HN-Pay1, O-Pay, Momo hoặc USDT. Chuyển đúng nội dung hiển thị trên màn hình nhé!"
    },
    "rut_tien": {
        "keywords": ["rút", "rut tien", "kẹt tiền", "chưa về"],
        "reply": "🏧 **HƯỚNG DẪN RÚT TIỀN:** Vào mục Tài Khoản -> Rút Tiền, liên kết ngân hàng chính chủ và tạo lệnh. Tiền sẽ về trong 1-3 phút!"
    },
    "dang_ky": {
        "keywords": ["đăng ký", "dang ky", "tạo tk", "lập nick"],
        "reply": "🎮 **ĐĂNG KÝ TÀI KHOẢN:** Chọn nút Đăng Ký ở màn hình chính, tạo Tên & Mật khẩu. Báo Mã ID cho Admin để nhận Code Tân Thủ!"
    },
    "khuyen_mai": {
        "keywords": ["khuyến mãi", "khuyen mai", "code", "thưởng"],
        "reply": "🎁 **SỰ KIỆN HOT:** Thưởng nạp đầu 100%, Hoàn trả 1.5% mỗi ngày. Đăng nhập mỗi ngày nhận lì xì VIP!"
    }
}

def get_ai_answer(question):
    q_lower = question.lower()
    for topic, data in KNOWLEDGE_BASE.items():
        if any(kw in q_lower for kw in data["keywords"]):
            return data["reply"]
    return "🤖 Em đã tiếp nhận câu hỏi. Nhân viên CSKH sẽ hỗ trợ trực tiếp cho anh/chị ngay ạ!"

# ==================== 3. API KẾT NỐI VỚI WEB GAME ====================
@app.route('/')
def home():
    return "Hệ thống Server Bot CSKH TX68 đang hoạt động!"

@app.route('/api/send_from_game', methods=['POST'])
def send_from_game():
    data = request.json or {}
    user_id = data.get("user_id", "guest_123")
    user_msg = data.get("message", "")

    if not user_msg:
        return jsonify({"status": "error", "message": "Nội dung trống!"})

    customer_code = get_or_assign_code(user_id)

    # BƯỚC 1: Bot Game gửi câu hỏi của khách vào nhóm Telegram
    try:
        bot_staff.send_message(STAFF_GROUP_ID, f"📌 Mã KH: {customer_code}\n💬 Khách hỏi: {user_msg}")
    except Exception as e:
        print(f"Lỗi Bot Staff: {e}")

    # BƯỚC 2: AI tự động tìm câu trả lời
    ai_reply = get_ai_answer(user_msg)

    # BƯỚC 3: Bot AI lập tức bắn câu trả lời vào nhóm Telegram
    try:
        bot_ai.send_message(STAFF_GROUP_ID, f"📌 Mã KH: {customer_code}\n🤖 AI Trả Lời: {ai_reply}")
    except Exception as e:
        print(f"Lỗi Bot AI: {e}")

    # BƯỚC 4: Đẩy câu trả lời vào bộ nhớ chờ Web Game kéo về
    if customer_code not in outbound_messages:
        outbound_messages[customer_code] = []
    outbound_messages[customer_code].append(ai_reply)

    return jsonify({"status": "success", "customer_code": customer_code})

@app.route('/api/get_reply_for_game', methods=['GET'])
def get_reply_for_game():
    user_id = request.args.get("user_id", "")
    if not user_id or str(user_id) not in user_to_code:
        return jsonify({"replies": []})

    code = user_to_code[str(user_id)]
    messages = outbound_messages.get(code, [])
    outbound_messages[code] = [] # Lấy xong xóa luôn
    return jsonify({"customer_code": code, "replies": messages})

# ==================== 4. DÀNH CHO ADMIN NHÂN VIÊN TRẢ LỜI THỦ CÔNG ====================
@bot_staff.message_handler(func=lambda msg: True)
def handle_admin_reply(message):
    # Nếu Admin (người thật) gõ tin nhắn trong nhóm kèm mã
    if str(message.chat.id) == str(STAFF_GROUP_ID) and not message.from_user.is_bot:
        text = message.text or ""
        match = re.search(r"Mã KH:\s*(\d{6})", text)
        if match:
            code = match.group(1)
            reply_text = text.replace(f"Mã KH: {code}", "").replace(f"Mã KH:{code}", "").strip()
            if code not in outbound_messages:
                outbound_messages[code] = []
            outbound_messages[code].append(reply_text)

# ==================== 5. CHẠY KHỞI ĐỘNG ====================
def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    try:
        bot_staff.remove_webhook(drop_pending_updates=True)
        bot_ai.remove_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Lỗi Webhook: {e}")
    bot_staff.infinity_polling(skip_pending=True)
            
