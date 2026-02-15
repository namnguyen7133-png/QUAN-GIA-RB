# Hệ thống Robot Ăn Uống GitHub

## Mục tiêu
Robot tự chạy chế độ ăn uống theo:
- ngày thường 366
- âm lịch
- lễ dương
- quân hàm
- quân cờ
- dữ liệu NotebookLM

---

## Cấu trúc repo

index.html → robot điều phối chính  
038 Che do an it benh tat.html → 366 ngày  
am-lich.html → ngày âm lịch  
le-duong.html → ngày lễ  
docs/ → tài liệu NotebookLM  
data/ → dữ liệu món ăn  

---

## Logic robot chạy

1. nếu hôm nay có âm lịch → chạy am-lich  
2. nếu hôm nay có lễ → chạy le-duong  
3. nếu có quân hàm → chạy file quân hàm  
4. nếu có quân cờ → chạy file quân cờ  
5. nếu không → chạy 366  

---

## Thêm dữ liệu NotebookLM

B1: copy nội dung NotebookLM  
B2: tạo file docs/ten.md  
B3: dán nội dung  

Robot HTML đọc:
fetch("docs/ten.md")

---

## Robot phân tích video

NotebookLM → xuất text  
→ script lọc:
- món ăn
- bệnh
- thời điểm
- chi phí  

→ lưu data JSON  

---

## Affiliate

Từ dữ liệu:
món → nguyên liệu → sản phẩm → link  

---

## Khi robot không chạy

Kiểm tra:
- index.html có không  
- tên file đúng không  
- path đúng không  

---

## Mở robot

https://namnguyen7133-png.github.io/HTML-i-n-tho-i-/
