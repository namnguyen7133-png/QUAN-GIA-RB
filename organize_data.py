import os
import json
import hashlib
import shutil
from datetime import datetime, UTC

# ========= CONFIG =========
ROOT_DIR = "."
DUP_DIR = "duplicates"
LOG_DIR = "logs"

os.makedirs(DUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

DUP_LOG = os.path.join(LOG_DIR, "duplicate_log.json")
EVENT_LOG = os.path.join(LOG_DIR, "event_log.json")

# ========= HASH =========
def file_hash(path, chunk_size=8192):
    h = hashlib.md5()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

# ========= SCAN =========
hash_map = {}
name_map = {}
duplicates = []
moved = 0

for root, _, files in os.walk(ROOT_DIR):
    if DUP_DIR in root or LOG_DIR in root or ".git" in root:
        continue

    for file in files:
        path = os.path.join(root, file)

        try:
            size = os.path.getsize(path)
            if size == 0:
                continue
        except:
            continue

        # hash
        try:
            h = file_hash(path)
        except:
            continue

        # duplicate by hash
        if h in hash_map:
            dst = os.path.join(DUP_DIR, file)
            shutil.move(path, dst)
            duplicates.append({
                "type": "hash",
                "file": path,
                "duplicate_of": hash_map[h]
            })
            moved += 1
            continue
        else:
            hash_map[h] = path

        # duplicate by name
        if file in name_map:
            dst = os.path.join(DUP_DIR, file)
            shutil.move(path, dst)
            duplicates.append({
                "type": "name",
                "file": path,
                "duplicate_of": name_map[file]
            })
            moved += 1
        else:
            name_map[file] = path

# ========= SAVE LOG =========
with open(DUP_LOG, "w", encoding="utf-8") as f:
    json.dump(duplicates, f, indent=2, ensure_ascii=False)

event = {
    "time": datetime.now(UTC).isoformat(),
    "duplicates": len(duplicates),
    "moved": moved
}

data = []

if os.path.exists(EVENT_LOG):
    try:
        with open(EVENT_LOG, encoding="utf-8") as f:
            loaded = json.load(f)
            if isinstance(loaded, list):
                data = loaded
    except:
        pass

data.append(event)

with open(EVENT_LOG, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Duplicates found: {len(duplicates)}")
print(f"Files moved: {moved}")
