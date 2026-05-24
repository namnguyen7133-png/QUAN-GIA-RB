import os
import sqlite3
import datetime
import traceback
import requests
import gspread

from google.oauth2.service_account import Credentials


# =========================================================
# CONFIG (ĐÃ CHUYỂN SANG ĐƯỜNG DẪN ĐÁM MÂY)
# =========================================================

# Đọc trực tiếp file dữ liệu nằm cùng thư mục trên GitHub
DB_PATH = "THOITIET.db"

GOOGLE_SHEET_ID = "1cKQe0vUcSVjDebBPVhvJYc17pGG9pAYaDeMzhB0bl34"

TAB_NAME = "thoi_tiet_mac_do"

# File này sẽ được hệ thống tự động sinh ra từ Secrets khi chạy
CREDENTIALS_FILE = "credentials.json"

LOG_FILE = "thoitiet_log.txt"


# =========================================================
# LOG
# =========================================================

def ghi_log(msg):

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    line = f"[{now}] {msg}"

    try:

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    except:
        pass


# =========================================================
# ĐỌC TOKEN TỪ ENVIRONMENT VARIABLES (GITHUB SECRETS)
# =========================================================

def doc_token_env(env_name):
    """Lấy trực tiếp giá trị cấu hình bảo mật từ GitHub Actions"""
    return os.environ.get(env_name, "").strip()


# =========================================================
# PUSHBULLET
# =========================================================

def gui_pushbullet(title, body):

    token = doc_token_env("PUSHBULLET_TOKEN")

    if not token:
        return

    headers = {
        "Access-Token": token,
        "Content-Type": "application/json"
    }

    data = {
        "type": "note",
        "title": title,
        "body": body
    }

    requests.post(
        "https://api.pushbullet.com/v2/pushes",
        json=data,
        headers=headers,
        timeout=20
    )


# =========================================================
# SLACK
# =========================================================

def gui_slack(msg):

    webhook = doc_token_env("SLACK_WEBHOOK_URL")

    if not webhook:
        return

    requests.post(
        webhook,
        json={"text": msg},
        timeout=20
    )


# =========================================================
# GUI THONG BAO
# =========================================================

def gui_thong_bao(title, body):

    try:
        # Kiểm tra tổng độ dài ký tự của tin nhắn để phân phối kênh
        tong_do_dai = len(title) + len(body)

        if tong_do_dai <= 110:
            gui_pushbullet(title, body)

        else:
            # Nếu tin nhắn dài, gộp lại có xuống dòng để gửi qua Slack
            noi_dung_slack = f"{title}\n{body}"
            gui_slack(noi_dung_slack)

    except:
        pass


# =========================================================
# GOOGLE SHEET
# =========================================================

def mo_google_sheet():
    # Tự động tạo file credentials.json từ GitHub Secret nếu chưa tồn tại trên máy ảo
    if not os.path.exists(CREDENTIALS_FILE):
        creds_json = doc_token_env("GOOGLE_CREDENTIALS")
        if creds_json:
            with open(CREDENTIALS_FILE, "w", encoding="utf-8") as f:
                f.write(creds_json)

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    credentials = Credentials.from_service_account_file(
        CREDENTIALS_FILE,
        scopes=scopes
    )

    gc = gspread.authorize(credentials)

    workbook = gc.open_by_key(GOOGLE_SHEET_ID)

    return workbook.worksheet(TAB_NAME)


# =========================================================
# CHECK NGAY
# =========================================================

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
            temperature_min,
            temperature_max,
            rain_sum
        FROM THOITIET_DINH_DUONG
        WHERE time = ?
    """

    cursor.execute(query, (ngay_2007,))

    row = cursor.fetchone()

    conn.close()

    if not row:

        raise Exception(
            f"Khong tim thay du lieu {ngay_2007}"
        )

    t_min, t_max, rain = row

    return {
        "ngay_xem": hom_nay.strftime("%d/%m/%Y"),
        "ngay_2007": ngay_2007,
        "t_min": t_min,
        "t_max": t_max,
        "rain": rain
    }


# =========================================================
# GOI Y
# =========================================================

def tao_goi_y(data):

    ds = []

    ds.append(
        "Gợi ý 1: ChatGPT viết lại báo cáo chuyên nghiệp."
    )

    ds.append(
        "Gợi ý 2: Link app thường ngắn gọn."
    )

    if data["rain"] > 5:

        ds.append(
            "⚠️ Có mưa, nên mang ô."
        )

    return " | ".join(ds)


# =========================================================
# NOI DUNG GUI
# =========================================================

def tao_noi_dung(data, goi_y):
    
    # Tiêu đề ngắn gọn hiển thị ngay trên banner thông báo để tránh mất chữ
    tieu_de = f"☀️ Dự báo {data['ngay_xem']}: {data['t_min']}°C - {data['t_max']}°C"

    than_bai = f"""
♉ Kim Ngưu | Lập Hạ

👕 {goi_y}

🥗 Ăn thanh nhiệt, tăng rau xanh.

🩺 Điều hòa khí huyết.
""".strip()

    return tieu_de, than_bai


# =========================================================
# MAIN
# =========================================================

def main():

    print("🚀 DANG CHAY TREN GITHUB ACTIONS...")

    data = lay_du_lieu()

    goi_y = tao_goi_y(data)

    tieu_de, than_bai = tao_noi_dung(data, goi_y)

    sheet = mo_google_sheet()

    ngay = data["ngay_xem"]

    if da_co_ngay(sheet, ngay):

        print("⚠️ DA TON TAI NGAY")

        gui_pushbullet(
            "⚠️ CẢNH BÁO",
            f"Sheet đã có ngày {ngay}"
        )

        return

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

    gui_thong_bao(tieu_de, than_bai)

    print("✅ THANH CONG")


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    try:

        main()

    except Exception as e:

        loi_ngan = f"❌ {str(e)}"

        print(loi_ngan)

        ghi_log(traceback.format_exc())

        gui_slack(
            traceback.format_exc()
        )
