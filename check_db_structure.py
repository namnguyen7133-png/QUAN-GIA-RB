import sqlite3
import sys

db_path = r"D:\SUA LOI GITHUB SHEET PYTHON\deepseek\THOITIET.db"
# Hoặc đường dẫn đến file bạn vừa tải từ GitHub về

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Lấy tên tất cả các bảng
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("=== CÁC BẢNG TRONG DATABASE ===")
    for table in tables:
        print(f"\n📋 Bảng: {table[0]}")
        # Lấy cấu trúc của bảng
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"   - Cột: {col[1]} | Kiểu: {col[2]} | Null: {col[3]}")

    # Thử lấy một vài dòng dữ liệu từ bảng đầu tiên
    if tables:
        first_table = tables[0][0]
        print(f"\n📊 DỮ LIỆU MẪU TỪ BẢNG '{first_table}' (5 dòng):")
        cursor.execute(f"SELECT * FROM {first_table} LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

    conn.close()
except Exception as e:
    print(f"❌ Lỗi: {e}")
    sys.exit(1)