import os
import re
import random
from threading import Thread
from flask import Flask, request, jsonify
from flask_cors import CORS
import telebot

# ==================== 1. KHỞI TẠO 2 BOT & NHÓM TELEGRAM ====================
TOKEN_AI = "8871256449:AAGaIlrsMouC2zT-aAmykabNltYSb-2WXCM"       # Bot 1: Chuyên trả lời AI
TOKEN_STAFF = "8576597700:AAG6p0YhWf1-QXMwR1vNtHxx6r7eAFxvRFU"    # Bot 2: Chuyên chuyển tiếp & dán tin nhắn
STAFF_GROUP_ID = "-1004444253619"                                 # ID Nhóm Telegram CSKH

bot_ai = telebot.TeleBot(TOKEN_AI)
bot_staff = telebot.TeleBot(TOKEN_STAFF)

# ==================== 2. KHỞI TẠO FLASK SERVER + CORS ====================
app = Flask(__name__)
CORS(app)  # Cho phép Web Game kết nối không bị chặn CORS

# Quản lý mã số 6 chữ số cố định cho người chơi
user_to_code = {}
code_to_user = {}
outbound_messages = {} # Hộp thư chờ gửi về Game { "011200": ["Nội dung trả lời"] }

def get_or_assign_code(user_id):
    """Cấp mã 6 chữ số cố định vĩnh viễn cho từng khách"""
    user_id_str = str(user_id)
    if user_id_str not in user_to_code:
        while True:
            new_code = f"{random.randint(100000, 999999)}"
            if new_code not in code_to_user:
                break
        user_to_code[user_id_str] = new_code
        code_to_user[new_code] = user_id_str
    return user_to_code[user_id_str]

# ==================== 3. KHO BỘ NÃO AI (BOT 1) ====================
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
    """Bot 1 dò từ khóa để đưa ra câu trả lời thích hợp"""
    q_lower = question.lower()
    for topic, data in KNOWLEDGE_BASE.items():
        if any(kw in q_lower for kw in data["keywords"]):
            return data["reply"]
    return "🤖 Em đã tiếp nhận câu hỏi. Nhân viên CSKH sẽ hỗ trợ trực tiếp cho anh/chị ngay ạ!"

# ==================== 4. WEB SERVER (KẾT NỐI VỚI GAME) ====================
@app.route('/')
def home():
    return "Hệ thống 2 Bot CSKH TX68 đang vận hành mượt mà!"

# API 1: Nơi Game gửi tin nhắn của Khách lên cho Bot 2
@app.route('/api/send_from_game', methods=['POST'])
def send_from_game():
    data = request.json or {}
    user_id = data.get("user_id", "guest_123")
    user_msg = data.get("message", "")

    if not user_msg:
        return jsonify({"status": "error", "message": "Nội dung trống!"})

    # BƯỚC 1: Bot 2 cấp Mã 6 chữ số cố định cho khách
    customer_code = get_or_assign_code(user_id)

    # BƯỚC 2: Bot 2 bắn tin nhắn kèm Mã lên Nhóm CSKH Telegram
    telegram_text = f"📌 Mã KH: {customer_code}\n💬 Khách hỏi: {user_msg}"
    try:
        bot_staff.send_message(STAFF_GROUP_ID, telegram_text)
    except Exception as e:
        print(f"Lỗi Bot 2 gửi lên nhóm: {e}")

    return jsonify({
        "status": "success", 
        "customer_code": customer_code,
        "message": "Tin nhắn đã gửi sang hệ thống CSKH"
    })

# API 2: Nơi Game liên tục gọi xuống để lấy câu trả lời
@app.route('/api/get_reply_for_game', methods=['GET'])
def get_reply_for_game():
    user_id = request.args.get("user_id", "")
    if not user_id or str(user_id) not in user_to_code:
        return jsonify({"replies": []})

    code = user_to_code[str(user_id)]
    messages = outbound_messages.get(code, [])
    
    # Lấy xong thì xóa tin nhắn trong bộ nhớ chờ
    outbound_messages[code] = []
    return jsonify({"customer_code": code, "replies": messages})

# ==================== 5. XỬ LÝ TIN NHẮN TRONG NHÓM TELEGRAM ====================

# BOT 1: Đọc tin nhắn do Bot 2 bắn lên -> Dò Mã -> Bắn câu trả lời AI vào nhóm
@bot_ai.message_handler(func=lambda msg: True)
def bot_ai_process(message):
    if str(message.chat.id) != str(STAFF_GROUP_ID):
        return

    text = message.text or ""
    match = re.search(r"Mã KH:\s*(\d{6})", text)
    if match and "Khách hỏi:" in text:
        code = match.group(1)
        question = text.split("Khách hỏi:")[1].strip()

        # Bot 1 tìm câu trả lời
        ai_reply = get_ai_answer(question)

        # Bot 1 gửi trả lời kèm Mã số vào nhóm
        response_text = f"📌 Mã KH: {code}\n🤖 AI Trả Lời: {ai_reply}"
        bot_ai.send_message(STAFF_GROUP_ID, response_text)

# BOT 2: Quét câu trả lời trong nhóm -> Dò Mã -> Lưu vào bộ nhớ chờ để Game kéo về
@bot_staff.message_handler(func=lambda msg: True)
def bot_staff_process(message):
    if str(message.chat.id) != str(STAFF_GROUP_ID):
        return

    text = message.text or ""
    match = re.search(r"Mã KH:\s*(\d{6})", text)
    if match and ("AI Trả Lời:" in text or "Trả lời:" in text or not message.from_user.is_bot):
        code = match.group(1)
        
        lines = text.split("\n", 1)
        reply_content = lines[1] if len(lines) > 1 else lines[0]
        reply_content = reply_content.replace("🤖 AI Trả Lời:", "").strip()

        if code not in outbound_messages:
            outbound_messages[code] = []
        outbound_messages[code].append(reply_content)

# ==================== 6. CHẠY KHỞI ĐỘNG HỆ THỐNG ====================
def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

def run_bot_ai():
    try:
        bot_ai.remove_webhook(drop_pending_updates=True) # Xóa sạch kẹt Webhook gây lỗi 409
    except Exception as e:
        print(f"Lỗi remove webhook Bot AI: {e}")
    bot_ai.infinity_polling(skip_pending=True)

def run_bot_staff():
    try:
        bot_staff.remove_webhook(drop_pending_updates=True) # Xóa sạch kẹt Webhook gây lỗi 409
    except Exception as e:
        print(f"Lỗi remove webhook Bot Staff: {e}")
    bot_staff.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    Thread(target=run_bot_ai).start()
    Thread(target=run_bot_staff).start()
    print("🚀 Hệ thống 2 Bot CSKH TX68 đã sẵn sàng hoạt động!")
            
