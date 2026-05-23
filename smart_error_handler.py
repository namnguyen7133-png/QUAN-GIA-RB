import os
import json
import sqlite3
import requests
import hashlib
import re
from datetime import datetime

# ============================================================
# CAU HINH - DOC CAC FILE API
# ============================================================

def doc_file(duong_dan):
    try:
        with open(duong_dan, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return None

# Doc cac token
SLACK_URL = doc_file("D:/APP SCRIPT/SLACK_WEBHOOK_URL.txt")
PUSHBULLET_TOKEN = doc_file("D:/APP SCRIPT/PUSHBULLET_TOKEN.txt")
DEEPSEEK_API = doc_file("D:/VIDEO/yotube/van_hoa_viet/DEEPSEEK_TIM_DAU/THOITIETLAMVIEC/API Deepseek.txt")

print("=== Kiem tra cau hinh ===")
print(f"Slack URL: {'Co' if SLACK_URL else 'Khong'}")
print(f"Pushbullet: {'Co' if PUSHBULLET_TOKEN else 'Khong'}")
print(f"Deepseek: {'Co' if DEEPSEEK_API else 'Khong'}")

# ============================================================
# HANG DOI TRANH TRUNG
# ============================================================

QUEUE_FILE = "notifier_central.json"

def tai_queue():
    if os.path.exists(QUEUE_FILE):
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"da_xu_ly": [], "dang_cho": []}

def luu_queue(data):
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def tao_hash(file_path, dong, loi):
    chuoi = f"{file_path}_{dong}_{loi}"
    return hashlib.md5(chuoi.encode()).hexdigest()

# ============================================================
# GUI THONG BAO
# ============================================================

def gui_slack(noi_dung):
    if not SLACK_URL:
        return
    try:
        requests.post(SLACK_URL, json={"text": noi_dung}, timeout=10)
        print("[Slack] Da gui")
    except Exception as e:
        print(f"[Slack] Loi: {e}")

def gui_pushbullet(tieu_de, noi_dung):
    if not PUSHBULLET_TOKEN:
        return
    try:
        requests.post(
            "https://api.pushbullet.com/v2/pushes",
            json={"type": "note", "title": tieu_de, "body": noi_dung},
            headers={"Access-Token": PUSHBULLET_TOKEN},
            timeout=10
        )
        print("[Pushbullet] Da gui")
    except Exception as e:
        print(f"[Pushbullet] Loi: {e}")

def gui_thong_minh(tieu_de, noi_dung):
    """Tin ngan (<200 ky tu) gui Pushbullet, tin dai gui Slack"""
    gio = datetime.now().hour
    if not (22 <= gio or gio < 7):
        print(f"[{gio}h] Khong trong khung gio cho phep (22h-7h)")
        return
    
    if len(noi_dung) < 200 and PUSHBULLET_TOKEN:
        gui_pushbullet(tieu_de, noi_dung)
    elif SLACK_URL:
        gui_slack(f"*{tieu_de}*\n{noi_dung}")
    else:
        print(f"Khong co kenh gui: {noi_dung[:100]}")

# ============================================================
# SUA LOI DATABASE
# ============================================================

def sua_db_thieu_cot(db_path, bang, cot_thieu):
    if not os.path.exists(db_path):
        return False, f"Khong tim thay {db_path}"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Kiem tra bang
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (bang,))
        if not cursor.fetchone():
            conn.close()
            return False, f"Khong tim thay bang {bang}"
        
        # Them cot
        cursor.execute(f"ALTER TABLE {bang} ADD COLUMN {cot_thieu} REAL")
        conn.commit()
        conn.close()
        return True, f"Da them cot {cot_thieu}"
    except Exception as e:
        return False, str(e)

def sua_toan_bo_db():
    """Sua tat ca cac loi database cua ban"""
    print("\n=== Dang sua database ===")
    
    cac_db = [
        "D:/CASHFLOW/data/weather.db",
        "weather.db",
        "D:/SUA LOI GITHUB SHEET PYTHON/deepseek/weather.db"
    ]
    
    cac_bang = ["weather_data", "thoitiet", "data"]
    cac_cot = ["temperature_2m_min", "temperature_2m_max", "humidity"]
    
    da_sua = False
    for db_path in cac_db:
        if os.path.exists(db_path):
            print(f"Tim thay: {db_path}")
            for bang in cac_bang:
                for cot in cac_cot:
                    ok, msg = sua_db_thieu_cot(db_path, bang, cot)
                    if ok:
                        print(f"  {msg}")
                        da_sua = True
            break
    
    if not da_sua:
        print("Khong tim thay database, tao moi...")
        conn = sqlite3.connect("weather.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                date TEXT,
                temperature_2m_min REAL,
                temperature_2m_max REAL,
                humidity REAL
            )
        """)
        conn.commit()
        conn.close()
        print("Da tao database moi: weather.db")
    
    return da_sua

# ============================================================
# XU LY LOI CHINH
# ============================================================

def xu_ly_loi(file_path, dong, loai_loi, chi_tiet, code_mau=""):
    print(f"\n=== Xu ly loi ===")
    print(f"File: {file_path}")
    print(f"Dong: {dong}")
    print(f"Loi: {loai_loi}")
    print(f"Chi tiet: {chi_tiet[:100]}")
    
    # Kiem tra trung
    hash_loi = tao_hash(file_path, dong, loai_loi)
    queue = tai_queue()
    
    if hash_loi in queue["da_xu_ly"]:
        print("Loi da xu ly roi, bo qua")
        return True
    
    # Thu tu dong sua
    da_sua = False
    
    # Truong hop loi thieu cot SQLite
    if "no such column" in chi_tiet.lower():
        tim = re.search(r"no such column:\s*(\w+)", chi_tiet)
        if tim:
            cot = tim.group(1)
            # Thu sua database
            cac_db = [
                "D:/CASHFLOW/data/weather.db",
                "weather.db"
            ]
            for db_path in cac_db:
                ok, msg = sua_db_thieu_cot(db_path, "weather_data", cot)
                if ok:
                    da_sua = True
                    print(f"Da sua: {msg}")
                    break
    
    # Truong hop loi import
    elif "ModuleNotFoundError" in loai_loi:
        tim = re.search(r"'([^']+)'", chi_tiet)
        if tim:
            module = tim.group(1)
            msg = f"Can chay: pip install {module}"
            print(msg)
            gui_thong_minh("Thieu module Python", msg)
    
    # Ghi log
    queue["dang_cho"] = [l for l in queue["dang_cho"] if l.get("hash") != hash_loi]
    
    if da_sua:
        queue["da_xu_ly"].append(hash_loi)
        gui_thong_minh("Da tu dong sua loi", f"{file_path}\n{chi_tiet[:200]}")
    else:
        queue["dang_cho"].append({
            "hash": hash_loi,
            "file": file_path,
            "dong": dong,
            "loai": loai_loi,
            "chi_tiet": chi_tiet,
            "thoi_gian": datetime.now().isoformat()
        })
        gui_thong_minh("Can xu ly thu cong", f"{file_path}\n{chi_tiet[:200]}")
    
    luu_queue(queue)
    return da_sua

# ============================================================
# HAM CHINH
# ============================================================

def main():
    print("\n" + "="*50)
    print("HE THONG SUA LOI THONG MINH")
    print("="*50)
    
    # B1: Sua database
    sua_toan_bo_db()
    
    # B2: Xu ly loi tu file locdlvaduasheet.py
    xu_ly_loi(
        file_path="/home/runner/work/QUAN-GIA-RB/QUAN-GIA-RB/locdlvaduasheet.py",
        dong=194,
        loai_loi="sqlite3.OperationalError",
        chi_tiet="no such column: temperature_2m_min",
        code_mau="cursor.execute('SELECT temperature_2m_min FROM weather_data')"
    )
    
    # B3: In ket qua
    print("\n" + "="*50)
    print("KET QUA")
    print("="*50)
    
    queue = tai_queue()
    print(f"Da xu ly: {len(queue['da_xu_ly'])} loi")
    print(f"Dang cho: {len(queue['dang_cho'])} loi")
    
    if queue["dang_cho"]:
        print("\nCac loi dang cho:")
        for l in queue["dang_cho"]:
            print(f"  - {l['file']} (dong {l['dong']}): {l['chi_tiet'][:50]}")
    
    print("\nFile log: notifier_central.json")
    print("HOAN TAT!")

if __name__ == "__main__":
    main()