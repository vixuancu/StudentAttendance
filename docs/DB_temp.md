users – người dùng hệ thống
users (
  id PK,
  username,
  password_hash,
  role ENUM('ADMIN','GIAO_VU','GIANG_VIEN'),
  is_active,
  created_at
)
Chỉ người có nghiệp vụ quản lý / giảng dạy mới có tài khoản
Sinh viên là dữ liệu, không phải actor

lecturers – thông tin giảng viên

lecturers (
  id PK,
  user_id FK -> users.id,
  lecturer_code,
  full_name,
  department
)

Tách users và lecturers để:
dễ mở rộng
dễ tích hợp hệ thống khác

students – sinh viên (đối tượng điểm danh)

students (
  id PK,
  student_code,
  full_name,
  class_code,
  status
)
Sinh viên có thể học nhiều môn tín chỉ
Không cần thông tin đăng nhập

III. THỰC THỂ ĐÀO TẠO THEO TÍN CHỈ

courses – môn tín chỉ (lớp học phần)
courses (
  id PK,
  course_code,
  course_name,
  semester,
  lecturer_id FK -> lecturers.id
)

Một môn tín chỉ gắn với một giảng viên phụ trách
Sinh viên đăng ký môn qua bảng trung gian

course_students – sinh viên đăng ký môn
course_students (
  course_id FK,
  student_id FK,
  PRIMARY KEY (course_id, student_id)
)
Quan hệ N–N giữa sinh viên và môn tín chỉ
Phù hợp đào tạo tín chỉ

class_sessions – BUỔI HỌC (cốt lõi)
class_sessions (
  id PK,
  course_id FK,
  session_date DATE,
  session_slot ENUM('SANG','CHIEU','TOI'),
  start_time,
  end_time,
  status ENUM('PENDING','ACTIVE','CLOSED')
)
Điểm danh luôn gắn với buổi học cụ thể
Phân ca học đúng thực tế khoa CNTT

IV. NHÓM BẢNG PHỤC VỤ NGHIỆP VỤ 6–7–8

attendance_records – KẾT QUẢ CUỐI
attendance_records (
  id PK,
  session_id FK,
  student_id FK,
  status ENUM('PRESENT','ABSENT','LATE','UNCONFIRMED'),
  detected_by ENUM('AI','MANUAL'),
  detected_at
)

Một sinh viên chỉ có 1 bản ghi / 1 buổi học
Trạng thái có thể thay đổi → cần lưu trạng thái cuối

attendance_events – log AI detect (rất đẹp)
attendance_events (
  id PK,
  session_id FK,
  student_id FK,
  confidence,
  image_path,
  detected_at
)

AI có thể detect nhiều lần
Bảng này:
phục vụ dashboard realtime
phục vụ xác nhận thủ công

V. NHÓM BẢNG SINH TRẮC HỌC

face_embeddings – dữ liệu khuôn mặt
face_embeddings (
  id PK,
  student_id FK,
  embedding_vector BLOB,
  is_active,
  created_at
)
Không ghi đè dữ liệu cũ
Đảm bảo truy vết & bảo mật
