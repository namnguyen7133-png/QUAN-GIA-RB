import sqlite3
import json
import os
from datetime import datetime, timedelta

# Đọc config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

DB_PATH = config["DB_PATH"]
JSON_OUTPUT = config["JSON_OUTPUT"]

# Hàm chuyển 2026-05-24 -> 2007-05-24
def chuyen_sang_nam_2007(ngay_str):
    parts = ngay_str.split("-")
    return f"2007-{parts[1]}-{parts[2]}"

# Hàm đổi định dạng ngày từ 2026-05-24 sang 24/05/2026
def dinh_dang_ngay_viet(ngay_str):
    try:
        return datetime.strptime(ngay_str, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return ngay_str

# Lời khuyên ăn uống
def tu_van_an_uong(t_min, t_max, rain):
    tb = (t_min + t_max) / 2
    if tb >= 33:
        khuyen = "🥵 Trời nóng – ăn thanh nhiệt: rau má, dưa hấu, cháo đậu xanh."
    elif tb <= 20:
        khuyen = "❄️ Trời lạnh – ăn ấm bụng: cháo gừng, súp nóng, gà hầm."
    else:
        khuyen = "🌤️ Mát mẻ – ăn uống đa dạng: rau xanh, cá, thịt nạc."

    if rain > 5:
        khuyen += " ☔ Trời mưa – hạn chế đồ lạnh."
    return khuyen

# Lấy dữ liệu từ database
def lay_du_lieu_ngay(ngay_tra):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    sql = """
        SELECT [temperature_2m_min (°C)],
               [temperature_2m_max (°C)],
               [rain_sum (mm)]
        FROM THOITIET_DINH_DUONG
        WHERE time = ?
    """
    cur.execute(sql, (ngay_tra,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {"t_min": row[0], "t_max": row[1], "rain": row[2] if row[2] else 0.0}

def main():
    ngay_mai = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    ngay_tra_db = chuyen_sang_nam_2007(ngay_mai)

    data = lay_du_lieu_ngay(ngay_tra_db)
    if not data:
        print("❌ Không có dữ liệu cho ngày", ngay_tra_db)
        return

    tu_van = tu_van_an_uong(data["t_min"], data["t_max"], data["rain"])

    # TẠO JSON - NGÀY ĐÃ ĐƯỢC ĐỊNH DẠNG VIỆT
    output = {
        "ngay_du_lich": dinh_dang_ngay_viet(ngay_mai),   # <--- ĐÃ SỬA
        "ngay_trong_db": ngay_tra_db,
        "nhiet_do_min": data["t_min"],
        "nhiet_do_max": data["t_max"],
        "luong_mua_mm": data["rain"],
        "loi_khuyen_an_uong": tu_van,
        "thoi_gian_cap_nhat": datetime.now().isoformat()
    }

    os.makedirs(os.path.dirname(JSON_OUTPUT), exist_ok=True)
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # IN RA MÀN HÌNH - CŨNG ĐÃ SỬA
    print("✅ Đã ghi JSON:", JSON_OUTPUT)
    print("📅 Ngày:", dinh_dang_ngay_viet(ngay_mai), "|", ngay_tra_db)
    print("🥗", tu_van)

if __name__ == "__main__":
    main()