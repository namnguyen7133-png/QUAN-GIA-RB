import os
import sys
from datetime import datetime
import json
import requests

def get_token_smart(file_path, json_key, github_env_key):
    """Hàm thông minh: Ưu tiên đọc file Offline ổ D, nếu không thấy (như trên GitHub)

    thì tự động bốc từ Ngăn bí mật GitHub Secrets.
    """
    # 1. Thử lấy từ Ngăn bí mật GitHub trước (Dành cho môi trường GitHub Actions)
    token_cloud = os.environ.get(github_env_key)
    if token_cloud:
        return token_cloud

    # 2. Nếu không có (Dành cho máy tính Offline ở nhà), đi lục các file trong ổ D
    if os.path.exists(file_path):
        try:
            # Nếu là file JSON (như file key.json của Cashflow)
            if file_path.lower().endswith('.json'):
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get(json_key)
            # Nếu là file TXT thông thường
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception:
            pass
            
    return None

def send_system_alert(title, message, task_name, data_in, data_out, error_detail=None, platform="slack"):
    try:
        full_path = os.path.abspath(sys.argv[0])
        win_path = full_path.replace("/", "\\")
        folder = os.path.dirname(win_path)
    except Exception:
        folder = "No"
        win_path = "No"

    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    msg = f"🔔 *{title}*\n"
    msg += "--------------------------------💡\n"
    msg += f"{message}\n"
    if error_detail:
        msg += f"❌ LỖI:\n{error_detail}\n"
    msg += "--------------------------------🛠️\n"
    msg += f"🎯 NV: {task_name}\n"
    msg += f"📥 Vào: {data_in}\n"
    msg += f"📤 Ra: {data_out}\n"
    msg += f"⏰ Giờ: {now}\n\n"
    msg += f"📁 Thư mục: {folder}\n"
    msg += f"📍 File: {win_path}"

    # --- ĐỊNH NGHĨA CÁC ĐƯỜNG DẪN VÀ TÊN BIẾN BÍ MẬT ---
    # Luồng Slack
    SLACK_TXT = r"D:\APP SCRIPT\SLACK_WEBHOOK_URL.txt"
    slack_url = get_token_smart(SLACK_TXT, "slack_webhook", "SLACK_WEBHOOK_URL")

    # Nếu file txt riêng không có, thử tìm trong file json của Cashflow
    if not slack_url:
        slack_url = get_token_smart(r"D:\CASHFLOW\data\key.json", "slack_webhook", "SLACK_WEBHOOK_URL")

    # Luồng Pushbullet
    PB_TXT = r"D:\APP SCRIPT\PUSHBULLET_TOKEN.txt"
    pb_tok = get_token_smart(PB_TXT, "pushbullet_token", "PUSHBULLET_TOKEN")
    
    if not pb_tok:
        pb_tok = get_token_smart(r"D:\CASHFLOW\data\key.json", "pushbullet_token", "PUSHBULLET_TOKEN")

    # --- TIẾN HÀNH GỬI TIN ---
    if platform in ["slack", "both"] and slack_url:
        try: requests.post(slack_url, json={"text": msg})
        except Exception: pass

    if platform in ["pushbullet", "both"] and pb_tok:
        h = {"Access-Token": pb_tok, "Content-Type": "application/json"}
        try:
            requests.post("https://api.pushbullet.com/v2/pushes", headers=h, 
                          json={"body": msg.replace("*", ""), "title": title, "type": "note"})
        except Exception: pass

if __name__ == "__main__":
    print("Dang chay thu luong thong minh...")
    send_system_alert(
        title="TEST HE THONG LAI",
        message="Code tự động nhận diện: Máy tính bốc file ổ D, GitHub bốc ngăn bí mật!",
        task_name="Kiem tra thong bao song song",
        data_in="Config",
        data_out="Slack/Pushbullet",
        platform="slack"
    )
    print("Da xong!")
