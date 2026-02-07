import os
import re
import shutil
from datetime import datetime

# ❌ Các thư mục CẤM đụng tới
EXCLUDE_DIRS = {'cua-hang-di-dong', '.git'}

def organize_smart():
    folders = ['SUC_KHOE', 'CHAM_SOC_GIA_DINH', 'LAP_TRINH_ROBOT']
    for f in folders:
        os.makedirs(f, exist_ok=True)

    # Lấy ngày hiện tại để phục vụ việc mở tệp theo ngày
    hom_nay = datetime.now().strftime("%d-%m-%Y")
    da_thong_bao = False

    files = [f for f in os.listdir('.') if f.endswith('.html') and os.path.isfile(f) and f != 'index.html']

    for filename in files:
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()

            # --- PHẦN THÊM MỚI: NHẮC NHỞ TỪ LỊCH SỬ ---
            # Kiểm tra nếu file có chứa thông tin ngày hôm nay thì thông báo
            if hom_nay in content or hom_nay.replace('-', '/') in content:
                print(f"⚠️ THÔNG BÁO TỪ TỆP {filename}:")
                if "đau lưng" in content or "thức đêm" in content:
                    print("👉 CẢNH BÁO: Hôm qua bạn đã ghi chép là ĐAU LƯNG và THỨC ĐÊM. Nghỉ ngơi ngay!")
                da_thong_bao = True

            # 1️⃣ Tìm ngày tháng để đặt tiền tố
            date_match = re.search(r'(\d{1,2})[/|-](\d{1,2})[/|-](\d{4})', content)
            date_prefix = f"{date_match.group(3)}-{date_match.group(2).zfill(2)}-{date_match.group(1).zfill(2)}" if date_match else "0000-00-00"

            # 2️⃣ Phân loại nội dung (Giữ nguyên logic của bạn)
            target_folder = 'SUC_KHOE'
            if any(word in content for word in ['vợ', 'massage', 'ngâm chân', 'ông bà', 'gia đình']):
                target_folder = 'CHAM_SOC_GIA_DINH'
            elif any(word in content for word in ['github', 'nes', 'python', 'robot', 'code']):
                target_folder = 'LAP_TRINH_ROBOT'

            # 3️⃣ Đổi tên + di chuyển (thêm hậu tố để biết đã xử lý)
            new_filename = f"{date_prefix}-{filename.replace('.html', '_DA_XEM.html')}"
            target_path = os.path.join(target_folder, new_filename)

            # Chống ghi đè
            counter = 1
            while os.path.exists(target_path):
                name, ext = os.path.splitext(new_filename)
                target_path = os.path.join(target_folder, f"{name}_{counter}{ext}")
                counter += 1

            shutil.move(filename, target_path)
            print(f"✅ Đã dọn dẹp: {filename} → {target_path}")

        except Exception as e:
            print(f"❌ Lỗi xử lý {filename}: {e}")
            
    if not da_thong_bao:
        print(f"📅 Hôm nay ({hom_nay}) chưa có tệp thông báo mới nào được xử lý.")

if __name__ == "__main__":
    organize_smart()
