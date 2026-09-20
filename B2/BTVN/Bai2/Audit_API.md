# Audit RESTful API: GitHub REST API

## 1. Get User Profile
* **URL:** GET /users/{username}
* **Status Code:** 
  * 200 OK: Thành công, trả về JSON chứa thông tin chi tiết của user
  * 404 Not Found: Không tìm thấy user
* **Key Headers:**
  * Content-Type: application/json; charset=utf-8
  * ETag: Mã hash dùng cho Cache Validation.
  * X-RateLimit-Limit: Giới hạn số request tối đa/giờ.
* **Đánh giá RESTful:** **Đạt**. URL dùng đúng danh từ số nhiều /users, dùng phương thức GET để truy vấn dữ liệu an toàn.

---

## 2. Create Repository
* **URL:** POST /user/repos
* **Status Code:** 
  * 201 Created: Tạo repo thành công.
  * 400 Bad Request: Cú pháp JSON gửi lên bị lỗi.
  * 422 Unprocessable Entity: Trùng tên repo hoặc thiếu thông tin bắt buộc.
* **Key Headers:**
  * Location: URL chỉ định địa chỉ của repo vừa khởi tạo.
  * Content-Type: application/json
* **Đánh giá RESTful:** **Đạt**. Sử dụng đúng POST để tạo mới, trả về 201 Created kèm Header Location theo đúng chuẩn REST.

---

## 3. Update Repository
* **URL:** PATCH /repos/{owner}/{repo}
* **Status Code:** 
  * 200 OK: Cập nhật thành công các trường dữ liệu được gửi lên.
  * 403 Forbidden: Không có quyền chỉnh sửa repo này.
  * 404 Not Found: Repo không tồn tại.
* **Key Headers:**
  * Content-Type: application/json
* **Đánh giá RESTful:** **Đạt**. Sử dụng đúng phương thức PATCH cho thao tác cập nhật một phần dữ liệu (Partial Update).

---

## 4. Delete Repository
* **URL:** DELETE /repos/{owner}/{repo}
* **Status Code:** 
  * 204 No Content: Xóa thành công, không trả về dữ liệu trong Response Body.
  * 403 Forbidden: Không có quyền xóa repo.
  * 404 Not Found: Repo không tồn tại hoặc đã bị xóa.
* **Key Headers:**
  * X-RateLimit-Remaining: Số lượt gọi request còn lại.
* **Đánh giá RESTful:** **Đạt**. Sử dụng đúng HTTP Method DELETE và trả về status code 204 No Content với Body rỗng chuẩn mực.

---

## 5. List Repositories
* **URL:** GET /users/{username}/repos?page=1&per_page=5
* **Status Code:** 
  * 200 OK: Trả về mảng danh sách các repos.
* **Key Headers:**
  * Link: Cung cấp liên kết trang tiếp theo và trang cuối (rel="next", rel="last").
  * Cache-Control: Quản lý bộ nhớ đệm (Cache).
* **Đánh giá RESTful:** **Đạt (Cấp độ 3 - HATEOAS)**. GitHub không hardcode thông tin phân trang vào body mà sử dụng Header Link giúp Client tự điều hướng các trang dễ dàng.

---

## Kết Luận
GitHub REST API tuân thủ rất tốt các nguyên tắc RESTful. API định danh tài nguyên bằng danh từ rõ ràng, sử dụng chính xác các HTTP Method (GET, POST, PATCH, DELETE) và mã HTTP Status Code tương ứng với từng trường hợp.