import sqlite3

db_path = r"D:\LICH\THOITIET\THOITIET.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Xem cấu trúc bảng THOITIET_DINH_DUONG
cursor.execute("PRAGMA table_info(THOITIET_DINH_DUONG)")
columns = cursor.fetchall()

print("=== CẤU TRÚC BẢNG THOITIET_DINH_DUONG ===")
for col in columns:
    print(f"  Cột: {col[1]} -> Kiểu dữ liệu: {col[2]}")

# Xem 3 dòng dữ liệu đầu tiên
print("\n=== DỮ LIỆU MẪU (3 dòng đầu) ===")
cursor.execute("SELECT * FROM THOITIET_DINH_DUONG LIMIT 3")
rows = cursor.fetchall()

# Lấy tên cột để hiển thị
col_names = [col[1] for col in columns]

for row in rows:
    print("\n---")
    for i, col_name in enumerate(col_names):
        print(f"  {col_name}: {row[i]}")

conn.close()