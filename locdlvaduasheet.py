def lay_du_lieu():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    hom_nay = datetime.date.today()
    ngay_2007 = f"2007-{hom_nay.strftime('%m-%d')}"

    # Lấy danh sách toàn bộ các cột thực tế đang có trong bảng để đối chiếu
    cursor.execute("PRAGMA table_info(THOITIET_DINH_DUONG);")
    cac_cot_co_san = [row[1] for row in cursor.fetchall()]
    
    # In ra terminal để debug xem database đang có những cột gì
    print("🔍 DANH SÁCH CÁC CỘT THỰC TẾ TRONG DATABASE:", cac_cot_co_san)

    if not cac_cot_co_san:
        raise Exception("Bang THOITIET_DINH_DUONG khong ton tai hoac khong co du lieu.")

    # 1. Tự động tìm tên cột Nhiệt độ thấp nhất
    cot_min = None
    for c in ["temperature_2m_min", "nhiet_do_min", "min_temp", "temperature_min", "t_min"]:
        if c in cac_cot_co_san:
            cot_min = c
            break

    # 2. Tự động tìm tên cột Nhiệt độ cao nhất
    cot_max = None
    for c in ["temperature_2m_max", "nhiet_do_max", "max_temp", "temperature_max", "t_max"]:
        if c in cac_cot_co_san:
            cot_max = c
            break

    # 3. Tự động tìm tên cột Lượng mưa
    cot_rain = None
    for c in ["rain_sum", "luong_mua", "rain", "mua_sum", "rain_fall"]:
        if c in cac_cot_co_san:
            cot_rain = c
            break

    # Nếu vẫn không tìm thấy, báo lỗi tường minh để dễ sửa
    if not cot_min or not cot_max:
        raise Exception(f"Không tìm thấy cột nhiệt độ phù hợp trong database! Các cột hiện có là: {cac_cot_co_san}")

    if not cot_rain:
        # Nếu không có cột mưa thì mặc định lấy cột đầu tiên hoặc xử lý an toàn
        cot_rain = cac_cot_co_san[0] 

    # Tạo câu lệnh SQL động gọi chính xác tên các cột tìm được
    query = f"""
        SELECT
            {cot_min},
            {cot_max},
            {cot_rain}
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
        "t_min": float(t_min) if t_min is not None else 0.0,
        "t_max": float(t_max) if t_max is not None else 0.0,
        "rain": float(rain) if rain is not None else 0.0
    }
