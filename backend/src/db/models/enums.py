import enum

class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    GIAO_VU = "GIAO_VU"
    GIANG_VIEN  = "GIANG_VIEN"

class StudentStatus(str, enum.Enum):
    ACTIVE = "ACTIVE" # Đang học
    INACTIVE = "INACTIVE" # Nghỉ học
    GRADUATED = "GRADUATED" # Tốt nghiệp
    SUSPENDED = "SUSPENDED" # Đình chỉ

class SessionSlot(str, enum.Enum):
    SANG = "SANG" # Buổi sáng
    CHIEU = "CHIEU" # Buổi chiều
    TOI = "TOI" # Buổi tối

class SessionStatus(str,enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"

class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT" # Có mặt
    ABSENT = "ABSENT" # Vắng mặt
    LATE = "LATE" # Trễ
    UNCONFIRMED = "UNCONFIRMED" # Chưa xác nhận

class DetectedByType(str, enum.Enum):
    AI = "AI" # Trí tuệ nhân tạo
    MANUAL = "MANUAL" # Thủ công