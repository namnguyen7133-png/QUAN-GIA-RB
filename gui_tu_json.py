import json
import requests
import os
from datetime import datetime

JSON_PATH = "data/thoitiet_hom_nay.json"

# Lấy token (tự động: GitHub dùng secrets, local dùng file)
if os.environ.get("GITHUB_ACTIONS"):
    PUSHBULLET_TOKEN = os.environ.get("PUSHBULLET_TOKEN", "")
else:
    try:
        with open(r"D:\APP SCRIPT\PUSHBULLET_TOKEN.txt", "r") as f:
            PUSHBULLET_TOKEN = f.read().strip()
    except:
        PUSHBULLET_TOKEN = ""

def gui_pushbullet(title, body, token):
    if not token:
        print("❌ Không có token")
        return
    try:
        r = requests.post(
            "https://api.pushbullet.com/v2/pushes",
            json={"type": "note", "title": title, "body": body},
            headers={"Access-Token": token, "Content-Type": "application/json"}
        )
        if r.status_code == 200:
            print("✅ Đã gửi Pushbullet")
    except Exception as e:
        print(f"❌ Lỗi: {e}")

def main():
    if not os.path.exists(JSON_PATH):
        print("❌ Chưa có JSON")
        return
    
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    tieu_de = f"🌤️ Dự báo {data['ngay_du_lich']}"
    noi_dung = f"""
📅 {data['ngay_du_lich']}
🌡️ {data['nhiet_do_min']}°C - {data['nhiet_do_max']}°C
☔ Mưa: {data['luong_mua_mm']} mm

🥗 {data['loi_khuyen_an_uong']}
"""
    gui_pushbullet(tieu_de, noi_dung, PUSHBULLET_TOKEN)

if __name__ == "__main__":
    main()