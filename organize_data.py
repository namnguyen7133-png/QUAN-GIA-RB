import os
import shutil
import hashlib
import json
from datetime import datetime

# ===== CẤU HÌNH =====
ROOT_DIR = "."
TARGET_DIRS = {
    "SUC_KHOE": ["suc_khoe", "benh", "thuoc"],
    "CHAM_SOC_GIA_DINH": ["gia_dinh", "tre_em", "me_be"],
    "LAP_TRINH_ROBOT": ["robot", "code", "python", "ai"]
}

DUP_LOG = "duplicate_log.json"
EVENT_LOG = "calendar_event_log.json"

# ===== HÀM TIỆN ÍCH =====
def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def classify(name):
    n = name.lower()
    for folder, keys in TARGET_DIRS.items():
        for k in keys:
            if k in n:
                return folder
    return None

# ===== THU THẬP FILE =====
files = []
for root, _, fs in os.walk(ROOT_DIR):
    if ".git" in root:
        continue
    for f in fs:
        if f.endswith(".html"):
            files.append(os.path.join(root, f))

# ===== PHÁT HIỆN TRÙNG =====
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

# ===== PHÂN LOẠI =====
moved = []

for f in list(hash_map.values()):
    name = os.path.basename(f)
    target = classify(name)
    if target:
        dest_dir = os.path.join(ROOT_DIR, target)
        os.makedirs(dest_dir, exist_ok=True)
        dest = os.path.join(dest_dir, name)

        if not os.path.exists(dest):
            shutil.move(f, dest)
            moved.append({
                "file": name,
                "to": target
            })

# ===== LOG =====
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

print("Robot v2 done")
