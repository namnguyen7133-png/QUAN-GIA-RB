import sqlite3
import requests
import os
from datetime import datetime, timedelta

DB_PATH = r"D:\LICH\THOITIET\THOITIET.db"

def get_weather_for_tomorrow():
    # Lấy ngày mai (ví dụ: 2026-05-24)
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Chuyển thành ngày 2007 (2026-05-24 -> 2007-05-24)
    # Cắt lấy phần tháng-ngày rồi ghép với năm 2007
    ngay_2007 = "2007-" + tomorrow.split("-")[1] + "-" + tomorrow.split("-")[2]
    
    print(f"🔍 Ngày mai dương lịch: {tomorrow}")
    print(f"🔍 Tra cứu trong DB ngày: {ngay_2007}")
    
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"❌ Không thấy file: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            [temperature_2m_min (°C)],
            [temperature_2m_max (°C)],
            [rain_sum (mm)]
        FROM THOITIET_DINH_DUONG
        WHERE time = ?
    """
    
    cursor.execute(query, (ngay_2007,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise Exception(f"❌ Không có dữ liệu ngày {ngay_2007} trong database")
    
    return {
        "date": tomorrow,      # Ngày dương lịch để hiển thị
        "date_2007": ngay_2007, # Ngày trong DB
        "t_min": row[0],
        "t_max": row[1],
        "rain": row[2] if row[2] is not None else 0.0
    }

def main():
    print("🚀 BẮT ĐẦU CHẠY...")
    print("=" * 50)
    
    try:
        data = get_weather_for_tomorrow()
        print(f"\n✅ KẾT QUẢ:")
        print(f"   📅 Ngày: {data['date']}")
        print(f"   📅 Tra DB: {data['date_2007']}")
        print(f"   🌡️ Nhiệt độ: {data['t_min']}°C - {data['t_max']}°C")
        print(f"   ☔ Lượng mưa: {data['rain']} mm")
        print("\n✅ THÀNH CÔNG!")
        
    except Exception as e:
        print(f"\n❌ LỖI: {e}")

if __name__ == "__main__":
    main()