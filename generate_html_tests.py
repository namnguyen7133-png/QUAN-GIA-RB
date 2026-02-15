import os
from pathlib import Path
from datetime import datetime
import html

# ======================================================
# HTML TEST GENERATOR — Đúng • Đủ • Đẹp • Sáng tạo • Tiết kiệm
# Tạo tối đa 300 file HTML preview cho toàn bộ repo
# Dùng: python generate_html_tests.py
# ======================================================

# Root repo (tự nhận thư mục hiện tại)
ROOT = Path(".").resolve()

# Output folder
OUT_DIR = ROOT / "_html_tests"
OUT_DIR.mkdir(exist_ok=True)

# Bỏ qua các thư mục không cần thiết
EXCLUDE = {".git", ".github", "_html_tests", "__pycache__"}

# Thu thập tối đa 300 file
all_files = []
for p in ROOT.rglob("*"):
    if not p.is_file():
        continue
    if any(part in EXCLUDE for part in p.parts):
        continue
    all_files.append(p)

all_files = sorted(all_files)[:300]

# Template HTML đẹp + meta
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Test: {name}</title>
  <style>
    body {{ font-family: system-ui, Arial, sans-serif; margin: 40px; background:#f3f4f6; }}
    .card {{ background:white; padding:28px; border-radius:14px; box-shadow:0 4px 14px rgba(0,0,0,0.08); }}
    h1 {{ margin-top:0; font-size:28px }}
    .meta {{ color:#6b7280; font-size:14px; margin-bottom:16px }}
    pre {{ background:#0f172a; color:#22c55e; padding:18px; border-radius:10px; overflow:auto }}
    .footer {{ margin-top:20px; font-size:12px; color:#999 }}
  </style>
</head>
<body>
  <div class="card">
    <h1>{name}</h1>
    <div class="meta">📁 {path}</div>
    <pre>{content}</pre>
    <div class="footer">Generated: {time}</div>
  </div>
</body>
</html>
"""


def safe_read(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return html.escape(text[:2000])
    except Exception:
        return "(binary or unreadable file)"


count = 0
for i, file_path in enumerate(all_files, start=1):
    rel = file_path.relative_to(ROOT)
    name = rel.stem
    content = safe_read(file_path)

    html_text = HTML_TEMPLATE.format(
        name=name,
        path=str(rel),
        content=content,
        time=datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    out_file = OUT_DIR / f"test_{i:03d}_{name}.html"
    out_file.write_text(html_text, encoding="utf-8")
    count += 1

# ===== TẠO DASHBOARD INDEX =====
index_items = []
for f in sorted(OUT_DIR.glob("test_*.html")):
    index_items.append(f'<li><a href="{f.name}" target="_blank">{f.name}</a></li>')

index_html = f"""<!DOCTYPE html>
<html lang=\"vi\">
<head>
<meta charset=\"UTF-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
<title>HTML Test Dashboard</title>
<style>
body {{ font-family: system-ui, Arial; margin:40px; background:#f3f4f6 }}
.card {{ background:white; padding:28px; border-radius:14px; box-shadow:0 4px 14px rgba(0,0,0,0.08) }}
h1 {{ margin-top:0 }}
ul {{ columns:3; -webkit-columns:3; -moz-columns:3 }}
a {{ text-decoration:none; color:#2563eb }}
a:hover {{ text-decoration:underline }}
</style>
</head>
<body>
<div class=\"card\">
<h1>📊 HTML Test Dashboard</h1>
<p>Tổng file: {count}</p>
<ul>
{''.join(index_items)}
</ul>
</div>
</body>
</html>
"""

(OUT_DIR / "index.html").write_text(index_html, encoding="utf-8")

print(f"✅ Generated {count} HTML test files + dashboard in {OUT_DIR}")
