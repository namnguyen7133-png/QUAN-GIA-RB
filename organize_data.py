import os
import re
import shutil
from datetime import datetime

def robot_quan_gia_phuc_vu():
    # --- PHẦN MỚI: KẾT NỐI VỚI NÃO BỘ CALENDAR ---
    # Lấy chìa khóa ID lịch từ hệ thống GitHub Secrets mà bạn đã tạo
    CALENDAR_ID = os.getenv('MY_CALENDAR_ID')
    
    # Lấy ngày hôm nay theo định dạng trong tên file của bạn (ví dụ: 08-02)
    ngay_thang = datetime.now().strftime("%d-%m")
    nam = datetime.now().strftime("%Y")
    hom_nay_day_du = datetime.now().strftime("%d-%m-%Y")

    print(f"🤖 Robot khởi động... Hôm nay là ngày: {hom_nay_day_du}")
    
    # Kiểm tra xem Robot có thấy lịch của bạn không
    if CALENDAR_ID:
        print(f"📅 NÃO BỘ ĐÃ KẾT NỐI: {CALENDAR_ID}")
    else:
        print("⚠️ CẢNH BÁO: Robot chưa thấy chìa khóa MY_CALENDAR_ID!")

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

    # 2️⃣ TIẾN HÀNH DỌN DẸP VÀ PHÂN LOẠI
    for folder in ['SUC_KHOE', 'CHAM_SOC_GIA_DINH', 'LAP_TRINH_ROBOT']:
        os.makedirs(folder, exist_ok=True)

    for filename in files:
        if filename in ['index.html', 'friends.csv']: continue 
        
        # Logic phân loại đơn giản vào SUC_KHOE
        target_folder = 'SUC_KHOE'
        new_name = f"{hom_nay_day_du}-DA_DOC-{filename}"
        
        try:
            shutil.move(filename, os.path.join(target_folder, new_name))
            print(f"✅ Đã dọn dẹp: {filename} -> {target_folder}")
        except Exception as e:
            print(f"❌ Lỗi khi dọn dẹp {filename}: {e}")

    # --- PHẦN MỚI: XÁC NHẬN HOÀN THÀNH LÊN LỊCH ---
    if CALENDAR_ID and found_today_file:
        print(f"\n🚀 LỆNH CHO BOT: Đã sẵn sàng dữ liệu để ĐĂNG BÀI theo lịch {CALENDAR_ID}")

if __name__ == "__main__":
    robot_quan_gia_phuc_vu()
