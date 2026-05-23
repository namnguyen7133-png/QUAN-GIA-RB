import sqlite3

def fix_missing_column_temperature():
    """Fix cụ thể cho lỗi temperature_2m_min"""
    db_path = "D:/CASHFLOW/data/weather.db"  # Đường dẫn database của bạn
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Kiểm tra cấu trúc bảng hiện tại
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Các bảng:", tables)
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        print(f"\nBảng {table_name}:")
        for col in columns:
            print(f"  - {col[1]}: {col[2]}")
        
        # Thêm cột nếu thiếu
        col_names = [col[1] for col in columns]
        if 'temperature_2m_min' not in col_names:
            print(f"Đang thêm cột temperature_2m_min vào bảng {table_name}...")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN temperature_2m_min REAL")
            print("✅ Đã thêm thành công!")
        
        if 'temperature_2m_max' not in col_names:
            print(f"Đang thêm cột temperature_2m_max vào bảng {table_name}...")
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN temperature_2m_max REAL")
            print("✅ Đã thêm thành công!")
    
    conn.commit()
    conn.close()
    print("\n🎉 Đã sửa xong lỗi database!")

if __name__ == "__main__":
    fix_missing_column_temperature()