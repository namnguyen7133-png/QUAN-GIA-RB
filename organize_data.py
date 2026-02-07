import os
import re
import shutil
from datetime import datetime

def robot_quan_gia_phuc_vu():
    # Lấy ngày hôm nay theo định dạng trong tên file của bạn (ví dụ: 08-02)
    ngay_thang = datetime.now().strftime("%d-%m")
    nam = datetime.now().strftime("%Y")
    hom_nay_day_du = datetime.now().strftime("%d-%m-%Y")

    print(f"🤖 Robot khởi động... Hôm nay là ngày: {hom_nay_day_du}")

    # 1️⃣ TÌM VÀ MỞ TỆP CỦA NGÀY HÔM NAY
    files = [f for f in os.listdir('.') if f.endswith('.html') and os.path.isfile(f)]
    
    found_today_file = False
    for filename in files:
        # Nếu tên file chứa ngày hôm nay (ví dụ: plan_08_02.html hoặc 08-02.html)
        if ngay_thang in filename.replace('_', '-'):
            print(f"✨ ĐÃ TÌM THẤY TỆP NHIỆM VỤ: {filename}")
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Trích xuất phần thông báo/cách dùng trong tệp HTML
                print("--- NỘI DUNG HƯỚNG DẪN HÔM NAY ---")
                print(content[:500]) # Hiển thị 500 ký tự đầu tiên để bạn đọc
                
                if "đau lưng" in content.lower() or "thức đêm" in content.lower():
                    print("\n🚨 CẢNH BÁO SỨC KHỎE: Tệp hôm nay nhắc bạn phải nghỉ ngơi vì ĐAU LƯNG!")
            found_today_file = True
            break
    
    if not found_today_file:
        print(f"❓ Không tìm thấy tệp riêng cho ngày {ngay_thang}. Robot sẽ dọn dẹp chung.")

    # 2️⃣ TIẾN HÀNH DỌN DẸP VÀ PHÂN LOẠI (Như cũ nhưng an toàn hơn)
    for folder in ['SUC_KHOE', 'CHAM_SOC_GIA_DINH', 'LAP_TRINH_ROBOT']:
        os.makedirs(folder, exist_ok=True)

    for filename in files:
        if filename in ['index.html', 'friends.csv']: continue # Tuyệt đối không đụng vào
        
        target_folder = 'SUC_KHOE'
        # Di chuyển vào thư mục dựa trên nội dung (như bạn đã viết)
        # ... (giữ nguyên logic phân loại của bạn)
        
        new_name = f"{hom_nay_day_du}-DA_DOC-{filename}"
        shutil.move(filename, os.path.join(target_folder, new_name))

if __name__ == "__main__":
    robot_quan_gia_phuc_vu()
