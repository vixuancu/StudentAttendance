I. BỐI CẢNH NGHIỆP VỤ TỔNG THỂ CỦA HỆ THỐNG
Hệ thống được xây dựng cho Khoa Công nghệ Thông tin – Đại học Mở Hà Nội, phục vụ:
Đào tạo theo hình thức tín chỉ
Sinh viên đăng ký nhiều môn tín chỉ khác nhau
Một môn tín chỉ:
Có nhiều sinh viên thuộc nhiều lớp hành chính khác nhau
Hoạt động giảng dạy trong ngày chia thành:
Buổi sáng
Buổi chiều
Buổi tối
👉 Vì vậy:
Điểm danh không gắn với sinh viên cố định
Mà gắn với:
 môn tín chỉ – buổi học – thời điểm cụ thể
Hệ thống hỗ trợ giảng viên thực hiện điểm danh tự động bằng nhận diện khuôn mặt, đồng thời đảm bảo khả năng kiểm soát, xác nhận và xuất dữ liệu phục vụ quản lý.
II. CÁC ĐỐI TƯỢNG NGHIỆP VỤ (Business Actors)
1. Giảng viên (Actor chính)
Người trực tiếp sử dụng hệ thống
Thực hiện điểm danh cho các môn tín chỉ mình phụ trách
2. Giáo vụ
Quản lý dữ liệu đào tạo
Hỗ trợ cập nhật thông tin sinh viên, lớp học phần
3. IT Admin
Quản trị hệ thống
Quản lý tài khoản, thiết bị, phân quyền
4. Sinh viên
Không thao tác trực tiếp
Là đối tượng được ghi nhận điểm danh
5. Hệ thống quản lý sinh viên (external)
Cung cấp dữ liệu:
Sinh viên
Môn tín chỉ
Danh sách đăng ký môn
III. CÁC NGHIỆP VỤ CHÍNH CỦA HỆ THỐNG (MÔ TẢ CHI TIẾT)
🔹 Nghiệp vụ 1: Quản lý người dùng & phân quyền
Mục đích
Đảm bảo chỉ đúng người – đúng vai trò mới được sử dụng chức năng điểm danh.
Nội dung nghiệp vụ
Cấp tài khoản cho:
Giảng viên
Giáo vụ
IT Admin
Xác thực đăng nhập
Phân quyền chức năng theo vai trò
Chỉ giảng viên:
Được kích hoạt lớp
Được điểm danh
Sinh viên không có tài khoản hệ thống
Nghiệp vụ 2: Quản lý sinh viên (dữ liệu nền - lưu ý đọc hết phần nv2)
Mục đích
Làm dữ liệu đầu vào cho điểm danh.
Nội dung nghiệp vụ
Lưu thông tin sinh viên:
Mã sinh viên
Họ tên
Trạng thái học tập


Đồng bộ danh sách sinh viên từ hệ thống quản lý sinh viên (có thể là dự định trong tương lai , hiện tại chắc chắn ko làm được ) - phần này có thể thay bằng import excel hay csv

Quản lý dữ liệu khuôn mặt:
Lưu vector đặc trưng
Cập nhật khi sinh viên thay đổi ngoại hình
Lưu lịch sử vector cũ


Nghiệp vụ 3: Quản lý môn học tín chỉ
Mục đích
Phản ánh đúng mô hình đào tạo tín chỉ.
Nội dung nghiệp vụ
Quản lý danh sách môn tín chỉ:
Mã môn
Tên môn
Học kỳ
Gán giảng viên phụ trách môn
Quản lý danh sách sinh viên đăng ký môn - xoay quanh môn học -buổi học
Một sinh viên có thể đăng ký nhiều môn
Một môn có nhiều sinh viên khác nhau

Nghiệp vụ 4: Quản lý buổi học theo ngày & ca học
Mục đích
Điểm danh phải gắn với một buổi học cụ thể, không phải cả môn.
Nội dung nghiệp vụ
Trong một ngày, mỗi môn tín chỉ có thể có:
Buổi sáng
Buổi chiều
Buổi tối
Mỗi buổi học có:
Thời gian bắt đầu
Thời gian kết thúc
Trạng thái buổi học
Hệ thống phải: - bên dưới để tham khảo nhưng kiểu kiểu thế
Tạo buổi học
Kích hoạt buổi học
Kết thúc buổi học

Nghiệp vụ 5: Kích hoạt điểm danh cho buổi học
Mục đích
Chuẩn bị dữ liệu & môi trường cho điểm danh.
Nội dung nghiệp vụ
Giảng viên đăng nhập
Xem danh sách các môn tín chỉ trong ngày
Chọn:
Môn học
Buổi (sáng / chiều / tối)
Kích hoạt buổi học
Hệ thống: - kiểu kiểu như dưới - đọc tham khảo 
Load danh sách sinh viên đăng ký môn
Kết nối camera
Chuyển trạng thái buổi học sang “Đang hoạt động”


Nghiệp vụ 6: Điểm danh tự động bằng nhận diện khuôn mặt
Mục đích
Ghi nhận sự hiện diện của sinh viên trong buổi học.
Nội dung nghiệp vụ
Camera ghi hình realtime
Hệ thống:
Phát hiện khuôn mặt
Trích xuất đặc trưng khuôn mặt
So khớp với dữ liệu sinh viên trong môn tín chỉ
Khi nhận diện thành công:
Ghi nhận sinh viên có mặt
Lưu thời điểm điểm danh
Khi không chắc chắn: - tham khảo 
Gắn trạng thái “chưa xác nhận”
AI hỗ trợ, không tự quyết định hoàn toàn.

Nghiệp vụ 7: Xác nhận & chỉnh sửa điểm danh
Mục đích
Đảm bảo độ tin cậy của kết quả điểm danh.
Nội dung nghiệp vụ
Giảng viên theo dõi dashboard realtime
Kiểm tra các trường hợp:
Nhận diện sai
Không nhận diện được
Giảng viên:
Xác nhận thủ công
Chỉnh sửa trạng thái (có mặt / vắng / muộn)

Nghiệp vụ 8: Theo dõi & hiển thị kết quả điểm danh
Mục đích
Hỗ trợ giảng viên kiểm soát buổi học.
Nội dung nghiệp vụ
Hiển thị:
Danh sách sinh viên
Trạng thái điểm danh theo thời gian thực

Thống kê nhanh:
Số sinh viên có mặt
Số sinh viên vắng
Đây là báo cáo realtime, không phải báo cáo tổng hợp.

Nghiệp vụ 9: Xuất dữ liệu điểm danh
Mục đích
Phục vụ lưu trữ và quản lý đào tạo.
Nội dung nghiệp vụ
Xuất danh sách điểm danh theo: tùy case muốn chọn làm chức năng
Buổi học
Môn tín chỉ
Khoảng thời gian
Định dạng:
Excel
Dữ liệu này có thể dùng cho:
Giáo vụ
Lưu trữ khoa

có thể mô tả chi tiết cho coder hiểu để code ví dụ  tham khảo (mang tính chất phục vụ code): 

I. MÔ HÌNH LẠI NGHIỆP VỤ 6 – ĐIỂM DANH TỰ ĐỘNG
1️⃣ Thời điểm nghiệp vụ 6 bắt đầu
Chỉ khi buổi học ở trạng thái “ĐANG HOẠT ĐỘNG”

Giảng viên không cần bấm “điểm danh” từng sinh viên

2️⃣ Vai trò AI trong nghiệp vụ 6 (cực kỳ quan trọng)
AI KHÔNG quyết định cuối cùng, mà chỉ:
Phát hiện khuôn mặt

Đề xuất kết quả nhận diện

Mỗi lần detect thành công → sinh ra một bản ghi tạm:
Thuộc tính
Ý nghĩa
student_id
SV được AI cho là khớp
confidence
Độ tin cậy
detected_at
Thời điểm
status
PENDING

👉 PENDING = chưa xác nhận

3️⃣ Các tình huống nghiệp vụ 6
TH1: Nhận diện rõ ràng
confidence cao

Hệ thống:

Đánh dấu SV = PRESENT

detected_by = AI

TH2: Nhận diện không chắc chắn
confidence thấp

Hệ thống:

Gắn trạng thái UNCONFIRMED

Đẩy lên dashboard cho giảng viên xem

TH3: Không nhận diện được
Không tạo bản ghi

SV vẫn là ABSENT cho tới khi xác nhận thủ công

👉 Đây là chỗ nghiệp vụ 6 kết thúc, chuyển sang 7 & 8.

III. MÔ HÌNH LẠI NGHIỆP VỤ 7 – XÁC NHẬN & CHỈNH SỬA
1️⃣ Nghiệp vụ này diễn ra KHI NÀO?
Trong lúc buổi học đang diễn ra

Hoặc sau khi kết thúc buổi học

2️⃣ Giảng viên nhìn thấy gì?
Dashboard hiển thị:
Danh sách sinh viên môn học

Với từng sinh viên:

Có mặt (AI)

Chưa xác nhận

Vắng

3️⃣ Giảng viên có thể làm gì?
Với sinh viên UNCONFIRMED
Xem ảnh chụp tại thời điểm AI detect

Xác nhận:

Có mặt

Vắng

Với sinh viên không có bản ghi
Điểm danh thủ công

Ghi chú (tuỳ chọn)

👉 Khi giảng viên thao tác:
status đổi sang CONFIRMED

detected_by = MANUAL

4️⃣ Tại sao nghiệp vụ này BẮT BUỘC?
Nếu không có nghiệp vụ 7:
Hội đồng phản biện sẽ hỏi:

“AI nhận diện sai thì sao?”
Bạn trả lời:
“Hệ thống hỗ trợ, quyết định cuối cùng thuộc về giảng viên.”
💯 Điểm cộng rất lớn.

IV. MÔ HÌNH LẠI NGHIỆP VỤ 8 – DASHBOARD REALTIME
1️⃣ Dashboard realtime KHÔNG phải báo cáo
👉 Nó là màn hình hỗ trợ giảng viên trong buổi học

2️⃣ Dashboard realtime hiển thị cái gì?
A. Thông tin tổng quan buổi học
Tên môn

Buổi: sáng / chiều / tối

Trạng thái: đang hoạt động

Thời gian bắt đầu

B. Danh sách sinh viên (core)
SV
Tên
Trạng thái
Nguồn
2020xxx
Nguyễn A
✅ Có mặt
AI
2020yyy
Trần B
⚠️ Chưa xác nhận
AI
2020zzz
Lê C
❌ Vắng
—

C. Thống kê realtime
Tổng số sinh viên

Số SV đã có mặt

Số SV chưa xác nhận

Số SV vắng

👉 Các con số thay đổi theo thời gian thực

3️⃣ Về mặt backend, realtime là gì?
Khi AI detect → backend:

Ghi DB

Push event (WebSocket / SSE)

Frontend:

Tự cập nhật bảng danh sách

Không cần reload trang

👉 Bạn không cần nói công nghệ realtime trong luận văn, chỉ mô tả nghiệp vụ là đủ.

V. NGHIỆP VỤ 9 – BÁO CÁO & XUẤT EXCEL (BẠN LO CHO ĐÚNG)
1️⃣ Báo cáo tối thiểu cần có (KHÔNG PHỨC TẠP)
Báo cáo theo buổi học
Môn tín chỉ

Ngày học

Buổi học

Danh sách sinh viên:

Có mặt

Vắng

Muộn
Thời điểm điểm danh

👉 Đây là báo cáo gốc, mọi thứ khác đều sinh ra từ đây.

2️⃣ Xuất Excel là gì về mặt nghiệp vụ?
Sau khi buổi học kết thúc

Giảng viên hoặc giáo vụ:

Chọn buổi học

Bấm “Xuất Excel”

Hệ thống:

Tổng hợp dữ liệu

Xuất file Excel

IV. DANH SÁCH CHỨC NĂNG HỆ THỐNG 
Bạn có thể trình bày thành bảng hoặc danh sách:
Quản lý tài khoản và phân quyền

Quản lý dữ liệu sinh viên

Quản lý dữ liệu khuôn mặt sinh viên

Quản lý môn học tín chỉ

Quản lý danh sách sinh viên đăng ký môn

Quản lý buổi học theo ngày và ca học

Kích hoạt buổi học

Điểm danh tự động bằng nhận diện khuôn mặt

Xác nhận và chỉnh sửa kết quả điểm danh

Hiển thị kết quả điểm danh realtime

Xuất dữ liệu điểm danh dạng Excel

Quản lý camera và thiết bị

Ghi log hoạt động hệ thống








