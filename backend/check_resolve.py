from datetime import datetime, timedelta
from src.db.models.enums import AttendanceStatus
from src.services.attendance_service import AIDemoService

def test():
    start_time = datetime.now() - timedelta(minutes=20)
    print("Start time:", start_time)
    print("Result when no late_time (expected 3 LATE):", AIDemoService._resolve_attendance_status(None, start_time))
    
    start_time2 = datetime.now() - timedelta(minutes=10)
    print("Start time2:", start_time2)
    print("Result when no late_time < 15m (expected 1 PRESENT):", AIDemoService._resolve_attendance_status(None, start_time2))

test()
