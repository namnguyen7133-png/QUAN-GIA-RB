import os
import sqlite3
import datetime
import traceback
import requests
import gspread
from google.oauth2.service_account import Credentials

# Gọi trực tiếp hàm thông báo sạch lỗi của anh Nam
try:
    from thong_bao import send_system_alert
except Exception:
    # Nếu chưa có file thong_bao.py, tạo hàm giả lập để không bị sập code
    def send_system_alert(*args, **kwargs): pass

# =========================================================
# CONFIG (TỰ ĐỘNG CHUYỂN ĐỔI LINH HOẠT MÁY TÍNH & GITHUB)
# =========================================================
GOOGLE_SHEET_ID = "1cKQe0vUcSVjDebBPVhvJYc17pGG9pAYaDeMzhB0bl34"
TAB_NAME = "thoi_tiet_mac_do"
CREDENTIALS_FILE = "credentials.json"
LOG_FILE = "thoitiet_log.txt"

# Tự động nhận diện đường dẫn Database (Ổ D hoặc Máy ảo GitHub)
if os.path.exists(r"D:\LICH\THOITIET\THOITIET.db"):
    DB_PATH = r"D:\LICH\THOITIET\THOITIET.db"
else:
    DB_PATH = "THOITIET.db"

def ghi_log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] {msg}\n")
    except:
        pass

def doc_token_env(env_name):
    """Lấy cấu hình bảo mật từ GitHub Secrets"""
    return os.environ.get(env_name, "").strip()

# =========================================================
# GOOGLE SHEET
# =========================================================
def mo_google_sheet():
    # Chạy trên GitHub: Tự tạo file credentials.json từ Secret nếu chưa có
    if not os.path.exists(CREDENTIALS_FILE):
        creds_json = doc_token_env("GOOGLE_CREDENTIALS")
        if creds_json:
            with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
                f.write(creds_json)
                
    # Chạy dưới máy tính Offline: Nếu không có file local thì tìm đường dẫn mặc định
    if not os.path.exists(CREDENTIALS_FILE) and os.path.exists(r"D:\LICH\THOITIET\credentials.json"):
        credentials_file_path = r"D:\LICH\THOITIET\credentials.json"
    else:
        credentials_file_path = CREDENTIALS_FILE

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credentials = Credentials.from_service_account_file(credentials_file_path, scopes=scopes)
    gc = gspread.authorize(credentials)
    workbook = gc.open_by_key(GOOGLE_SHEET_ID)
    return workbook.worksheet(TAB_NAME)

def da_co_ngay(sheet, ngay):
    try:
        cot_a = sheet.col_values(1)
        return ngay in cot_a
    except:
        return False

# =========================================================
# LAY DU LIEU SQLITE
# =========================================================
def lay_du_lieu():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hom_nay = datetime.date.today()
    ngay_2007 = f"2007-{hom_nay.strftime('%m-%d')}"

    query = """
        SELECT
            *
           rain_sum
        FROM THOITIET_DINH_DUONG
        WHERE time = ?
    """
    cursor.execute(query, (ngay_2007,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise Exception(f"Khong tim thay du lieu cua ngay {ngay_2007} trong bang THOITIET_DINH_DUONG")

    t_min, t_max, rain = row
    return {
        "ngay_xem": hom_nay.strftime("%d/%m/%Y"),
        "ngay_2007": ngay_2007,
        "t_min": t_min,
        "t_max": t_max,
        "rain": rain
    }

def tao_goi_y(data):
    ds = ["Gợi ý 1: ChatGPT viết lại báo cáo chuyên nghiệp.", "Gợi ý 2: Link app thường ngắn gọn."]
    if data["rain"] > 5:
        ds.append("⚠️ Có mưa, nên mang ô.")
    return " | ".join(ds)

# =========================================================
# MAIN FUNCTION
# =========================================================
def main():
    print("🚀 ROBOT QUÂN GIA ĐANG KHỞI CHẠY HỆ THỐNG...")
    
    # 1. Lấy dữ liệu thời tiết
    data = lay_du_lieu()
    goi_y = tao_goi_y(data)
    
    # 2. Kết nối Google Sheet
    sheet = mo_google_sheet()
    ngay = data["ngay_xem"]

    # 3. Kiểm tra trùng lặp ngày
    if da_co_ngay(sheet, ngay):
        print("⚠️ DỮ LIỆU NGÀY NÀY ĐÃ TỒN TẠI TRÊN SHEET!")
        send_system_alert(
            title="⚠️ CẢNH BÁO TRÙNG NGÀY",
            message=f"Hệ thống dừng lại vì Google Sheet đã có sẵn dữ liệu ngày {ngay}.",
            task_name="Đẩy dữ liệu Sheet",
            data_in=DB_PATH,
            data_out="Google Sheet"
        )
        return

    # 4. Ghi dữ liệu vào Sheet
    row = [
        data["ngay_xem"],
        data["ngay_2007"],
        f"{data['t_min']}°C - {data['t_max']}°C",
        "Lập Hạ",
        "Kim Ngưu",
        goi_y,
        "- Món ăn thanh nhiệt.",
        "Điều hòa khí huyết."
    ]
    sheet.insert_row(row, 2)
    print("✅ ĐÃ GHI DỮ LIỆU LÊN SHEET THÀNH CÔNG!")

    # 5. Bắn thông báo nghiệm thu về điện thoại/Slack thông qua file thong_bao.py
    send_system_alert(
        title="☀️ ROBOT QUẢN GIA: THÀNH CÔNG",
        message=f"Dự báo {data['ngay_xem']}: {data['t_min']}°C - {data['t_max']}°C\n\n👕 {goi_y}\n🥗 Ăn thanh nhiệt, tăng rau xanh.\n🩺 Điều hòa khí huyết.",
        task_name="Đẩy dữ liệu Sheet",
        data_in=DB_PATH,
        data_out="Google Sheet"
    )

# =========================================================
# KHỐI KÍCH HOẠT CHẠY VÀ BẮT LỖI TỰ ĐỘNG
# =========================================================
if __name__ == "__main__":
    try:
        main()
        print("✅ HỆ THỐNG HOÀN THÀNH NHIỆM VỤ!")
    except Exception as e:
        chi_tiet_loi = traceback.format_exc()
        print("❌ LỖI HỆ THỐNG:\n", chi_tiet_loi)
        ghi_log(chi_tiet_loi)
        
        # Gọi file thong_bao.py tự động gửi chi tiết lỗi bốc được về Slack/Pushbullet
        send_system_alert(
            title="🚨 ROBOT QUẢN GIA: THẤT BẠI",
            message=f"Hệ thống gặp sự cố nghiêm trọng: {str(e)}",
            task_name="Đẩy dữ liệu Sheet",
            data_in=DB_PATH,
            data_out="Google Sheet",
            error_detail=chi_tiet_loi
        )
