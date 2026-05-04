import sys
import os
from pathlib import Path
import asyncio

# Thêm đường dẫn project vào sys.path để import
sys.path.append(str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from src.db.session import async_session_factory
from src.repository.ai_demo_repo import AIDemoRepository
from datetime import datetime, timedelta, time

async def test_time_logic(class_session_id=134): # Mặc định test với class_session_id 134 như log bạn bị lỗi
    print(f"=== Bắt đầu kiểm tra dữ liệu thời gian cho Class Session ID: {class_session_id} ===")
    
    async with async_session_factory() as db_session:
        repo = AIDemoRepository(db_session)
        session = await repo.get_class_session_detail(class_session_id)
        
        if not session:
            print("Lỗi: Không tìm thấy session này trong DB.")
            return
            
        print(f"1. Dữ liệu từ Database:")
        print(f"   - session_date: {session.session_date}")
        print(f"   - start_time  : {session.start_time}")
        print(f"   - end_time    : {session.end_time}")
        print(f"   - late_time   : {session.late_time}")
        
        if session.session_date and session.start_time:
            now = datetime.now()
            print(f"\n2. Thông tin giờ hiện tại của Backend Server:")
            print(f"   - datetime.now() = {now}")
            
            # --- KIỂM TRA MÔ PHỎNG THEO LOGIC MỚI TRONG ATTENDANCE_SERVICE ---
            
            # 2.1 Kiểm tra xem có đúng ngày hôm nay không
            # Có thể lệch ngày do múi giờ
            print(f"\n3. Kiểm tra logic ngày/giờ:")
            db_date = session.session_date.date()
            server_date = now.date()
            print(f"   - DB Date     = {db_date}")
            print(f"   - Server Date = {server_date}")
            
            if db_date != server_date:
                print("   => CẢNH BÁO LỖI (1): Khác ngày (Chỉ có thể điểm danh ca học trong ngày hôm nay). Có thể do lỗi lệch timezone hoặc đang test khác ngày.")
                
            # 2.2 Kiểm tra giờ kết thúc (Lỗi bạn gặp)
            if session.end_time:
                session_end_datetime = datetime.combine(session.session_date.date(), session.end_time.time())
                print(f"\n   - Thời gian kết thúc ca học (DB) = {session_end_datetime}")
                print(f"   - Thời gian Server hiện tại      = {now}")
                
                # So sánh thử
                if now > session_end_datetime:
                    print("   => CẢNH BÁO LỖI (2): Ca học đã kết thúc. Thời gian Server lớn hơn (trễ hơn) giờ kết thúc DB.")
                    print(f"      Lệch (số giây): {(now - session_end_datetime).total_seconds()} giây")
                else:
                    print("   => HỢP LỆ: Giờ Server chưa vượt quá kết thúc session_end.")
                    
            # 2.3 Kiểm tra giờ bắt đầu sớm quá 15 phút
            session_start_datetime = datetime.combine(session.session_date.date(), session.start_time.time())
            print(f"\n   - Thời gian bắt đầu ca học (DB)  = {session_start_datetime}")
            
            time_diff_seconds = (session_start_datetime - now).total_seconds()
            print(f"   - Tính lệch thời gian (bắt đầu - now): {time_diff_seconds} giây")
            
            if time_diff_seconds > 15 * 60: # Quá 15p (=> là trước giờ học > 15p)
                 print(f"   => CẢNH BÁO LỖI (3): Mở sớm > 15 phút. Lệch {time_diff_seconds / 60:.1f} phút.")
            elif time_diff_seconds > 0:
                 print(f"   => HỢP LỆ (Mở sớm): Được phép mở trước, sớm: {time_diff_seconds / 60:.1f} phút.")
            else:
                 print(f"   => HỢP LỆ (Đang học): Lớp đã bắt đầu được {-time_diff_seconds / 60:.1f} phút trước.")

    print("\n=================")

            
if __name__ == "__main__":
    import sys
    loop = asyncio.get_event_loop()
    
    sid = 134
    if len(sys.argv) > 1:
        try:
             sid = int(sys.argv[1])
        except ValueError:
             pass
             
    loop.run_until_complete(test_time_logic(sid))