import os
import re

def organize_files():
    files = [f for f in os.listdir('.') if f.endswith('.html') and f != 'index.html']
    for filename in files:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            # Tìm ngày tháng dạng dd/mm/yyyy hoặc dd-mm-yyyy
            match = re.search(r'(\d{1,2})[/|-](\d{1,2})[/|-](\d{4})', content)
            if match:
                new_name = f"{match.group(3)}-{match.group(2).zfill(2)}-{match.group(1).zfill(2)}-Health.html"
                if filename != new_name:
                    os.rename(filename, new_name)
                    print(f"Doi ten: {filename} -> {new_name}")

if __name__ == "__main__":
    organize_files()
