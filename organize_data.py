import os
import re

def organize_smart():
    # Tạo các thư mục nếu chưa có
    folders = ['SUC_KHOE', 'CHAM_SOC_GIA_DINH', 'LAP_TRINH_ROBOT']
    for f in folders:
        if not os.path.exists(f): os.makedirs(f)

    files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']
    
    for filename in files:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            
            # 1. Tìm ngày tháng
            date_match = re.search(r'(\d{1,2})[/|-](\d{1,2})[/|-](\d{4})', content)
            date_prefix = f"{date_match.group(3)}-{date_match.group(2).zfill(2)}-{date_match.group(1).zfill(2)}" if date_match else "0000-00-00"

            # 2. Phân loại sáng tạo
            target_folder = 'SUC_KHOE' # Mặc định
            if any(word in content for word in ['vợ', 'massage', 'ngâm chân', 'ông bà']):
                target_folder = 'CHAM_SOC_GIA_DINH'
            elif any(word in content for word in ['github', 'nes', 'python', 'robot']):
                target_folder = 'LAP_TRINH_ROBOT'

            # 3. Đổi tên và di chuyển
            new_name = f"{target_folder}/{date_prefix}-{filename}"
            try:
                os.rename(filename, new_name)
                print(f"✅ Đã đưa {filename} vào {new_name}")
            except:
                pass

if __name__ == "__main__":
    organize_smart()
