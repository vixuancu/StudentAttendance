"""
Enums / Constants cho hệ thống.
Dùng integer mapping để đồng bộ với SmallInteger trong DB.
"""


class Gender:
    """Giới tính: False=Nữ, True=Nam"""

    FEMALE = False
    MALE = True


class CameraStatus:
    """Trạng thái camera: 0=Offline, 1=Online"""

    OFFLINE = 0
    ONLINE = 1


class DayOfWeek:
    """Thứ trong tuần: 2=Thứ 2, ..., 8=Chủ nhật"""

    MON = 2
    TUE = 3
    WED = 4
    THU = 5
    FRI = 6
    SAT = 7
    SUN = 8


class SessionStatus:
    """Trạng thái buổi học: 0=Chưa bắt đầu, 1=Đang diễn ra, 2=Kết thúc, 3=Nghỉ, 4=Bù"""

    PENDING = 0
    ACTIVE = 1
    CLOSED = 2
    CANCELLED = 3
    MAKEUP = 4


class AttendanceStatus:
    """Trạng thái điểm danh: 1=Có mặt, 2=Vắng, 3=Trễ, 4=Có phép"""

    PRESENT = 1
    ABSENT = 2
    LATE = 3
    EXCUSED = 4


class CancelStatus:
    """Soft delete: False=Active, True=Cancelled"""

    ACTIVE = False
    CANCELLED = True
