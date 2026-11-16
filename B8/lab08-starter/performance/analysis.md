# Lab 4 — Phân tích kết quả

| Kịch bản | Users | Spawn rate | Duration | p95 (ms) | Failure rate | RPS |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 2 | 30s | 92 | 0,000% | 5,06 |
| B | 50 | 5 | 60s | 62 | 0,216% | 23,34 |
| C | 200 | 50 | 30s | 210 | 0,071% | 95,15 |

Số liệu lấy từ dòng **Aggregated** trong [A.html](../reports/A.html), [B.html](../reports/B.html) và [C.html](../reports/C.html). RPS là trung bình cả lần đo (`total_rps`); failure rate = số request lỗi / tổng request × 100%. Duration là thời gian cấu hình bằng `-t`.

1. Kịch bản có p95 cao nhất là gì? Dùng số liệu quan sát để giải thích.

    **C có p95 tổng cao nhất: 210 ms**, so với 92 ms ở A và 62 ms ở B.
    C tăng lên 200 user với tốc độ 50 user/giây, tương đương khoảng 4 giây
    để sinh đủ user. B có 50 user và A có 10 user.

    POST là endpoint chậm nhất ở C: p95 570 ms, p99 1.500 ms và thời gian
    lớn nhất 2.977 ms. POST có thao tác ghi và commit SQLite. Tranh chấp
    ghi, chờ tài nguyên hoặc chi phí xử lý khi nhiều request đồng thời là
    các giả thuyết phù hợp với code; chưa có log khóa, query hay CPU để
    khẳng định nguyên nhân cụ thể. Các GET ở C cũng tăng p95 lên 150–160 ms.

    B có p95 thấp hơn A dù nhiều user hơn, nên số đo không cho thấy quan hệ
    tăng đều theo tải. A chỉ có 148 request, trong đó 18 POST, còn B chạy
    lâu hơn và có 1.390 request. Khởi động, cache, trạng thái dữ liệu và
    nhiễu trên máy là các yếu tố cần kiểm chứng bằng những lần đo lặp lại.
    RPS tăng từ 5,06 lên 23,34 rồi 95,15; ba lần đo chưa xác định được ngưỡng
    bão hòa hoặc công suất tối đa của hệ thống.

2. Endpoint nào tăng failure rate? Phân biệt lỗi HTTP thực và lỗi đánh dấu trong Locust.

    Chỉ `GET /books?year={year}` có lỗi được Locust ghi nhận:

    | Kịch bản | Số lần tìm theo năm | Lỗi giả lập | Failure rate riêng task |
    |---|---:|---:|---:|
    | A | 23 | 0 | 0,000% |
    | B | 197 | 3 | 1,523% |
    | C | 374 | 2 | 0,535% |

    Thông báo lỗi ở B và C đều là
    `SIMULATED_500 (client-side only; actual HTTP 200)`. Các endpoint khác có
    0 lỗi và bảng exceptions của cả ba báo cáo đều rỗng. Trong các báo cáo
    này không ghi nhận HTTP 500 thật, timeout hoặc lỗi kết nối.

    Tỷ lệ lỗi không tăng đều theo số user: B có 3 lỗi, C có 2 lỗi. Đây là
    kết quả lấy mẫu ngẫu nhiên, không phải bằng chứng server lỗi nhiều hơn
    khi tăng tải. GET sách theo ID chấp nhận 404 mong đợi là thành công,
    vì task chọn ID ngẫu nhiên và một số sách có thể không tồn tại.

3. Với SLO giả định p95 < 300 ms, kịch bản nào đạt? Nêu giới hạn của phép đo.

    Nếu SLO áp dụng cho **p95 tổng**, cả A (92 ms), B (62 ms) và C (210 ms)
    đều đạt. Nếu yêu cầu **mọi endpoint** có p95 < 300 ms, B đạt theo báo
    cáo; A có POST được báo là 300 ms nên chưa chứng minh được điều kiện
    nhỏ hơn 300 ms, còn C không đạt vì POST có p95 570 ms. Percentile của
    Locust là giá trị xấp xỉ, cần lưu ý khi kết quả ở sát ngưỡng.

    Đề xuất dùng B (50 user, spawn rate 5, 60 giây) làm baseline CI ban đầu:
    p95 tổng và p95 từng endpoint quan trọng < 300 ms, đồng thời không có
    lỗi HTTP hoặc kết nối ngoài kỳ vọng. B đo được 23,34 RPS; lưu giá trị
    này để so sánh hồi quy trong cùng điều kiện thay vì coi là năng lực
    production được bảo đảm. A có thể dùng làm bước smoke test nhẹ, C dùng
    kiểm tra tăng tải nhanh khi cần.

    CI cần tách lỗi `SIMULATED_500` khỏi lỗi thật, hoặc chạy một cấu hình
    riêng tắt giả lập. Không chỉ dùng exit code mặc định để kết luận server
    lỗi vì lỗi giả lập cũng có thể làm Locust trả mã khác 0. Trước khi đặt
    gate ổn định, nên đo lặp lại với dữ liệu khởi tạo, phiên bản, máy chạy
    và khoảng warm-up được kiểm soát.

    Các số liệu này chỉ là phép đo ngắn trên Flask development server và
    SQLite ở localhost. Client và server cùng máy, user có thời gian nghỉ
    1–3 giây, các kịch bản có thời lượng khác nhau và task tạo sách làm
    trạng thái DB thay đổi. Chưa có bằng chứng DB được đưa về cùng trạng
    thái trước mỗi lần chạy. Không dùng ba báo cáo này để khẳng định SLO
    production hoặc kết luận hệ thống chịu được tải dài hạn.

4. Nếu connection pool bị giới hạn ở 5, bạn sẽ kiểm chứng ảnh hưởng như thế nào?

    Đây là **thiết kế thí nghiệm đề xuất**, chưa chạy trong ba báo cáo trên.
    Nếu có nhiều hơn 5 request đồng thời cần giữ connection, các request
    khác có thể phải chờ; khi hết thời gian chờ có thể phát sinh timeout.
    200 user ảo không đồng nghĩa 200 connection đang bị giữ, vì còn thời
    gian nghỉ và mỗi task chỉ mượn connection trong một phần thời gian.

    So sánh cấu hình hiện tại với một cấu hình dùng pool hỗ trợ giới hạn,
    đặt `pool_size=5` và `max_overflow=0` để không mở connection vượt mức 5;
    giữ `pool_timeout` cố định và kiểm tra `db.engine.pool` để xác nhận
    cấu hình thực sự được áp dụng. Chạy lại C với cùng dữ liệu khởi tạo,
    thời lượng và task, đồng thời ghi thời gian chờ lấy connection, số
    connection đang được mượn và log timeout.

    Đối chiếu p95/p99, RPS và lỗi thật với baseline. Phân biệt timeout của
    pool với lỗi SQLite bị khóa và lỗi giả lập phía Locust. Chỉ khi số đo
    chờ connection và log tương ứng cùng thay đổi mới có cơ sở quy kết ảnh
    hưởng cho giới hạn pool; không mặc định mọi lỗi ở 200 user là do pool.

> Không điền số liệu giả định vào bảng. Không khẳng định hiệu năng production
> từ SQLite + Flask development server trên máy cá nhân.
