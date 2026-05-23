"""
TỰ ĐỘNG GỬI THÔNG BÁO THỜI TIẾT
Chạy mỗi ngày lúc 22h30
"""

import sqlite3
import requests
import json
import os
from datetime import datetime

# ==================== ĐỌC CẤU HÌNH ====================
def doc_token(duong_dan):
    try:
        with open(duong_dan, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

SLACK_URL = doc_token("D:/APP SCRIPT/SLACK_WEBHOOK_URL.txt")
PUSHBULLET_TOKEN = doc_token("D:/APP SCRIPT/PUSHBULLET_TOKEN.txt")

# ==================== LẤY DỮ LIỆU THỜI TIẾT ====================
def lay_nhiet_do():
    """Lấy nhiệt độ từ database"""
    db_paths = [
        "D:/CASHFLOW/data/weather.db",
        "weather.db"
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT date, temperature_2m_min, temperature_2m_max, humidity 
                    FROM weather_data 
                    ORDER BY date DESC 
                    LIMIT 1
                """)
                data = cursor.fetchone()
                conn.close()
                
                if data:
                    return {
                        "ngay": data[0],
                        "nhiet_do_min": data[1],
                        "nhiet_do_max": data[2],
                        "do_am": data[3]
                    }
            except Exception as e:
                print(f"Loi doc db {db_path}: {e}")
    
    return None

# ==================== TƯ VẤN ĂN GÌ ====================
def tu_van_theo_thoi_tiet(nhiet_do_max, do_am):
    """Đưa ra lời khuyên ăn uống dựa trên nhiệt độ và độ ẩm"""
    
    if nhiet_do_max >= 35:
        return """🌡️ THỜI TIẾT NÓNG (≥35°C)
🍉 NÊN ĂN: Dưa hấu, bí đao, cháo đậu xanh, rau má
🥤 UỐNG: Nước dừa, nước cam, trà xanh
❌ TRÁNH: Đồ nóng, nhiều dầu mỡ, rượu bia"""
    
    elif nhiet_do_max <= 20:
        return """❄️ THỜI TIẾT LẠNH (≤20°C)
🍲 NÊN ĂN: Cháo gừng, lẩu, súp nóng, gà hầm
🥤 UỐNG: Trà gừng mật ong, sữa nóng
✅ NÊN: Bổ sung vitamin C, ăn đồ ấm bụng"""
    
    elif do_am and do_am >= 80:
        return """💧 THỜI TIẾT NỒM ẨM (≥80%)
🌿 NÊN ĂN: Đồ khô ráo, hạn chế đồ lạnh
🥤 UỐNG: Trà gừng nóng, nước ấm
🏠 BẬT: Điều hòa chế độ khô"""
    
    elif do_am and do_am <= 40:
        return """🏜️ THỜI TIẾT HANH KHÔ (≤40%)
💧 NÊN ĂN: Canh, súp, trái cây mọng nước
🍊 UỐNG: Nước ép cam, bưởi, thanh long
✅ NHỚ: Dưỡng ẩm da, uống nhiều nước"""
    
    else:
        return """🌤️ THỜI TIẾT MÁT MẺ (20-35°C)
🥗 NÊN ĂN: Rau xanh, cá hấp, thịt nạc, hải sản
🥤 UỐNG: Nước lọc, trà thảo mộc
✅ LÝ TƯỞNG: Ăn đa dạng các loại thực phẩm"""

# ==================== GỬI THÔNG BÁO ====================
def gui_slack(noi_dung):
    if SLACK_URL:
        try:
            requests.post(SLACK_URL, json={"text": noi_dung}, timeout=10)
            print("✅ Đã gửi Slack")
            return True
        except Exception as e:
            print(f"Slack lỗi: {e}")
    return False

def gui_pushbullet(tieu_de, noi_dung):
    if PUSHBULLET_TOKEN:
        try:
            requests.post(
                "https://api.pushbullet.com/v2/pushes",
                json={"type": "note", "title": tieu_de, "body": noi_dung},
                headers={"Access-Token": PUSHBULLET_TOKEN},
                timeout=10
            )
            print("✅ Đã gửi Pushbullet")
            return True
        except Exception as e:
            print(f"Pushbullet lỗi: {e}")
    return False

def gui_thong_minh(tieu_de, noi_dung):
    """Tin ngắn gửi Pushbullet, tin dài gửi Slack"""
    if len(noi_dung) < 200:
        return gui_pushbullet(tieu_de, noi_dung)
    else:
        return gui_slack(f"*{tieu_de}*\n{noi_dung}")

# ==================== TẠO THÔNG BÁO ====================
def tao_thong_bao_thoi_tiet():
    """Tạo nội dung thông báo thời tiết hoàn chỉnh"""
    data = lay_nhiet_do()
    
    if not data:
        return "❌ Không thể lấy dữ liệu thời tiết từ database"
    
    ngay = data["ngay"] or datetime.now().strftime("%d/%m/%Y")
    nhiet_min = data["nhiet_do_min"] or "N/A"
    nhiet_max = data["nhiet_do_max"] or "N/A"
    do_am = data["do_am"] or "N/A"
    
    tu_van = tu_van_theo_thoi_tiet(nhiet_max, do_am)
    
    thong_bao = f"""
📅 {ngay}
🌡️ Nhiệt độ: {nhiet_min}°C - {nhiet_max}°C
💧 Độ ẩm: {do_am}%

{tu_van}
"""
    return thong_bao

# ==================== HÀM CHÍNH ====================
def main():
    print(f"=== GỬI THÔNG BÁO THỜI TIẾT - {datetime.now().strftime('%H:%M:%S')} ===")
    
    # Kiểm tra giờ (chỉ gửi 22h-7h)
    gio = datetime.now().hour
    if not (22 <= gio or gio < 7):
        print(f"⏰ Hiện tại {gio}h - Chỉ gửi từ 22h đến 7h")
        print("📝 Đã lưu thông báo, sẽ gửi vào khung giờ cho phép")
        
        # Lưu lại để gửi sau
        with open("cho_gui.json", "a", encoding='utf-8') as f:
            f.write(json.dumps({
                "thoi_gian": datetime.now().isoformat(),
                "noi_dung": tao_thong_bao_thoi_tiet()
            }, ensure_ascii=False))
            f.write("\n")
        return
    
    # Tạo và gửi thông báo
    noi_dung = tao_thong_bao_thoi_tiet()
    print(noi_dung)
    
    gui_thong_minh("🌤️ LỜI KHUYÊN THỜI TIẾT HÔM NAY", noi_dung)

if __name__ == "__main__":
    main()