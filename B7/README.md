# BT Buổi 7

## Kết quả test bằng curl

![Tạo sản phẩm và lấy danh sách có phân trang](images/result1.png)

**1. Tạo sản phẩm và lấy danh sách:**

- `POST /api/v1/products` trả về `201 CREATED`, tạo sản phẩm `TEST-B7` có id `6`, giá `15000` và tồn kho `10`.
- `GET /api/v1/products?page=1&size=2` trả về `200 OK`, lấy 2 sản phẩm của trang đầu.
- Response có `items`, `page: 1`, `size: 2` và `total: 6` tại thời điểm test.

![Chi tiết sản phẩm, cập nhật và reserve](images/result2.png)

**2. Lấy chi tiết, cập nhật và đặt trước sản phẩm:**

- `GET /api/v1/products/4` trả về `200 OK`, hiển thị thông tin sản phẩm id `4`.
- `PATCH /api/v1/products/4` đổi tên thành `Ban phim moi`; giá và tồn kho giữ nguyên.
- `POST /api/v1/products/4/reserve` với `qty: 2` trả về `200 OK`, tồn kho giảm từ `10` xuống `8`.
- Reserve với `qty: 999` trả về `409 CONFLICT`, lỗi `out_of_stock` do không đủ hàng.

![Kiểm tra giá không hợp lệ và tạo đơn hàng](images/result3.png)

**3. Validate dữ liệu và tạo đơn hàng:**

- Tạo sản phẩm với `price_cents: -1` trả về `422 UNPROCESSABLE ENTITY`, lỗi `validation_error` chỉ rõ giá phải lớn hơn hoặc bằng 0.
- `POST /api/v1/orders` trả về `201 CREATED`, tạo đơn id `1` cho khách hàng `Tran Long`.
- Đơn có 2 dòng sản phẩm: `Ban phim` giá `15000` và `Chuot` giá `8000`, mỗi loại 1 sản phẩm; tổng tiền `23000`.

![Danh sách và chi tiết đơn hàng](images/result4.png)

**4. Lấy danh sách và chi tiết đơn hàng:**

- `GET /api/v1/orders` và `GET /api/v1/orders/1` đều trả về `200 OK`.
- Kết quả có thông tin khách hàng, các dòng sản phẩm, số lượng, đơn giá và tổng tiền `23000`.
- Một Order liên kết nhiều Product thông qua OrderItem.

![Kiểm tra healthz và ready](images/result5.png)

**5. Kiểm tra trạng thái service:**

- `GET /healthz` trả về `200 OK` với `status: "ok"`, xác nhận ứng dụng đang chạy.
- `GET /ready` trả về `200 OK` với `checks.db: "ok"`, xác nhận database sẵn sàng.
- Hai chức năng sử dụng hai endpoint riêng biệt.

![Xóa mềm sản phẩm và kiểm tra lại](images/result6.png)

**6. Xóa mềm sản phẩm:**

- `DELETE /api/v1/products/4` trả về `204 NO CONTENT`, không có response body.
- `GET /api/v1/products/4` sau khi xóa trả về `404 NOT FOUND`.
- Sản phẩm được đánh dấu `archived=true` và không còn được trả về qua API sản phẩm.

## Kết quả test bằng pytest

![Kết quả chạy 20 bài kiểm thử](images/result7.png)

**7. Kiểm thử tự động:**

- Chạy `python.exe -m pytest -v`, kết quả **20 passed**, không có test thất bại.
- Kiểm tra tạo sản phẩm, trùng SKU, validation, phân trang, cập nhật, xóa mềm và reserve không âm tồn kho.
- Kiểm tra đơn nhiều sản phẩm, lưu giá tại thời điểm đặt hàng và rollback khi tạo đơn thất bại.
- Test GET orders có eager loading đạt: tạo 5 đơn, mỗi đơn 3 sản phẩm và kiểm tra chỉ có 2 truy vấn SELECT để tránh N+1.
- Các test health check, JSON sai cú pháp và lệnh tạo dữ liệu mẫu cũng đạt.

