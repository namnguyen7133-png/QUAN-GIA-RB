import os
import re
import shutil

def organize_smart():
    folders = ['SUC_KHOE', 'CHAM_SOC_GIA_DINH', 'LAP_TRINH_ROBOT']
    for f in folders:
        os.makedirs(f, exist_ok=True)

    # Lấy danh sách file, loại trừ index.html và các file đã nằm trong thư mục
    files = [f for f in os.listdir('.') if f.endswith('.html') and os.path.isfile(f) and f != 'index.html']
    
    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
            
            # 1. Tìm ngày tháng (Regex tối ưu hơn)
            date_match = re.search(r'(\d{1,2})[/|-](\d{1,2})[/|-](\d{4})', content)
            if date_match:
                date_prefix = f"{date_match.group(3)}-{date_match.group(2).zfill(2)}-{date_match.group(1).zfill(2)}"
            else:
                date_prefix = "0000-00-00"

            # 2. Phân loại
            target_folder = 'SUC_KHOE'
            if any(word in content for word in ['vợ', 'massage', 'ngâm chân', 'ông bà', 'gia đình']):
                target_folder = 'CHAM_SOC_GIA_DINH'
            elif any(word in content for word in ['github', 'nes', 'python', 'robot', 'code']):
                target_folder = 'LAP_TRINH_ROBOT'

            # 3. Đổi tên và di chuyển (Tránh trùng file)
            new_filename = f"{date_prefix}-{filename}"
            target_path = os.path.join(target_folder, new_filename)
            
            # Nếu file đã tồn tại thì thêm hậu tố để không bị ghi đè
            counter = 1
            while os.path.exists(target_path):
                name, ext = os.path.splitext(new_filename)
                target_path = os.path.join(target_folder, f"{name}_{counter}{ext}")
                counter += 1

            shutil.move(filename, target_path)
            print(f"✅ Moved: {filename} -> {target_path}")
        except Exception as e:
            print(f"❌ Lỗi xử lý {filename}: {e}")

if __name__ == "__main__":
    organize_smart()
