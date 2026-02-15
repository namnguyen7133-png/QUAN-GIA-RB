# ========= LOG JSON =========
with open(DUP_LOG, "w", encoding="utf-8") as f:
    json.dump(duplicates, f, indent=2, ensure_ascii=False)

event = {
    "time": datetime.utcnow().isoformat(),
    "duplicates": len(duplicates),
    "moved": moved
}

# đảm bảo EVENT_LOG luôn là list
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
