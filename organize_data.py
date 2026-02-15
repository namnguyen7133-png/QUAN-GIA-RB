import os
import shutil
import hashlib
import json
import csv
from datetime import datetime

# ========= CẤU HÌNH =========
ROOT_DIR = "."
SCAN_EXT = (".html", ".md", ".txt", ".pdf")

TARGET_DIRS = {
    "SUC_KHOE": ["suc_khoe", "benh", "thuoc", "health", "medical"],
    "CHAM_SOC_GIA_DINH": ["gia_dinh", "tre_em", "me_be", "family", "baby"],
    "LAP_TRINH_ROBOT": ["robot", "code", "python", "ai", "automation"]
}

IGNORE_DIRS = [".git", "node_modules", "__pycache__"]
IGNORE_FILES = ["duplicate_log.json", "calendar_event_log.json"]

DUP_LOG = "duplicate_log.json"
EVENT_LOG = "calendar_event_log.json"
CSV_LOG = "robot_report.csv"

# ========= HASH FILE (BLOCK) =========
def file_hash(path, block_size=65536):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            data = f.read(block_size)
            if not data:
                break
            h.update(data)
    return h.hexdigest()

# ========= ĐỌC NỘI DUNG NHẸ =========
def read_sample(path, size=2000):
    try:
        with open(path, "rb") as f:
            return f.read(size).decode("utf-8", "ignore").lower()
    except:
        return ""

# ========= PHÂN LOẠI =========
def classify(path):
    name = os.path.basename(path).lower()
    text = read_sample(path)

    for folder, keys in TARGET_DIRS.items():
        for k in keys:
            if k in name or k in text:
                return folder
    return None

# ========= THU THẬP FILE =========
files = []

for root, dirs, fs in os.walk(ROOT_DIR):
    if any(ig in root for ig in IGNORE_DIRS):
        continue

    for f in fs:
        if f in IGNORE_FILES:
            continue
        if f.lower().endswith(SCAN_EXT):
            files.append(os.path.join(root, f))

# ========= PHÁT HIỆN TRÙNG =========
hash_map = {}
duplicates = []

for f in files:
    try:
        h = file_hash(f)
        if h in hash_map:
            duplicates.append({
                "duplicate": f,
                "original": hash_map[h]
            })
            os.remove(f)
        else:
            hash_map[h] = f
    except:
        pass

# ========= PHÂN LOẠI & MOVE =========
moved = []

for f in list(hash_map.values()):
    target = classify(f)
    if not target:
        continue

    name = os.path.basename(f)
    dest_dir = os.path.join(ROOT_DIR, target)
    os.makedirs(dest_dir, exist_ok=True)
    dest = os.path.join(dest_dir, name)

    if os.path.abspath(f) == os.path.abspath(dest):
        continue

    if not os.path.exists(dest):
        shutil.move(f, dest)
        moved.append({
            "file": name,
            "to": target
        })

# ========= LOG JSON =========
with open(DUP_LOG, "w", encoding="utf-8") as f:
    json.dump(duplicates, f, indent=2, ensure_ascii=False)

event = {
    "time": datetime.utcnow().isoformat(),
    "duplicates": len(duplicates),
    "moved": moved
}

if os.path.exists(EVENT_LOG):
    try:
        data = json.load(open(EVENT_LOG, encoding="utf-8"))
    except:
        data = []
else:
    data = []

data.append(event)

with open(EVENT_LOG, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# ========= CSV REPORT =========
with open(CSV_LOG, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["time", "duplicates", "moved_files"])
    writer.writerow([
        event["time"],
        event["duplicates"],
        len(event["moved"])
    ])

# ========= STATS =========
print("Robot v3 done")
print("Files scanned:", len(files))
print("Duplicates removed:", len(duplicates))
print("Moved:", len(moved))
