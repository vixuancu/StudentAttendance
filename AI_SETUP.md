# Hướng Dẫn Cài Đặt AI & Anti-Spoofing Cho Project Điểm Danh AI (Dành Cho Windows)

Khi pull dự án `StudentAttendance` về một máy Windows mới, module Nhận Diện Khuôn Mặt (InsightFace) và Chống Gian Lận (Anti-Spoofing MiniFASNet) có thể không hoạt động do các yêu cầu kỹ thuật khắt khe. Dưới đây là hướng dẫn các bước để đảm bảo máy của bạn chạy được 100%.

## 1. Yêu Cầu Bắt Buộc (QUAN TRỌNG)

Bạn **bắt buộc** phải sử dụng đúng **Python 3.11.**
Nếu bạn dùng Python 3.10 hoặc 3.12, việc cài đặt file InsightFace `.whl` đính kèm trong repo sẽ CHẮC CHẮN gặp lỗi "is not a supported wheel on this platform".

- **Cách tải Python 3.11:** [https://www.python.org/downloads/release/python-3119/](https://www.python.org/downloads/release/python-3119/) (Cuộn xuống dưới chọn *Windows installer (64-bit)*).
- **Lưu ý trong lúc cài đặt Python:** Phải nhớ tích chọn dòng "Add python.exe to PATH".

## 2. Windows C++ Build Tools

Mô hình chống giả mạo (`onnxruntime`) và OpenCV backend được chia sẻ có chứa code C++. Trên Windows, bạn cần bộ Visual C++ Redistributable.

- Truy cập [Download Visual Studio Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).
- Tải bộ *Build Tools for Visual Studio 2022*. Khi cài, nhớ tích chọn **"Desktop development with C++"**.

## 3. Quy Trình Cài Đặt Các Thư Viện Backend Python

Khởi chạy Terminal / PowerShell, đi vào thư mục **StudentAttendance** (nơi chứa file `README.md`):

```bash
# 1. Tạo môi trường ảo với Python 3.11
python -m venv .venv

# 2. Kích hoạt môi trường (Windows PowerShell)
.\.venv\Scripts\activate
# (Nếu bạn dùng Git Bash thì gõ: source .venv/Scripts/activate)

# 3. Nâng cấp pip để tránh lỗi
python -m pip install --upgrade pip
```

Bây giờ bạn sẽ cài đặt thư viện AI đặc thù là `insightface` thông qua file wheel đính kèm sẵn để bỏ qua lỗi build do dính C++ phức tạp:

```bash
# Cài đặt file wheel InsightFace
pip install insightface-0.7.3-cp311-cp311-win_amd64.whl
```

Sau đó cài đặt tất cả các thư viện thông thường khác (fastapi, onnxruntime, opencv...):

```bash
pip install -r backend/requirements.txt
```

> **Lưu ý về Torch:** Server backend hoàn toàn KHÔNG sử dụng thư viện Pytorch (`torch`). Chức năng Onnxruntime + Numpy đã tự gánh toàn bộ để giúp cho máy bạn không phải tải Pytorch nặng vài GB về máy ảo. Nên nếu bạn thấy AI lỗi đòi `torch` hay `torchvision`, hãy pull lại git do nó đã được dọn sạch rồi!

## 4. Cấu Hình .env

Bật Server FastAPI mà quên tạo file `.env` sẽ khiến server tắt ngang lập tức:

1. Trỏ vào thư mục `backend/`.
2. Tạo/Copy file `.env.example` thành file `.env`.
3. Đảm bảo cấu hình cổng DB đúng trong biến `DATABASE_URL`.

## 5. Chạy Server Điểm Danh AI

Ở màn hình PowerShell vừa đứng (Vẫn nhớ đang trong trạng thái Activate môi trường `.venv`):

```bash
# Lệnh chạy môi trường Develop Backend
make dev
```

Nếu Console in ra log `[AntiSpoof] ONNX Model loaded successfully.`, chúc mừng! Máy của bạn đã kéo được Models chống gian lận và module điểm danh đang hoạt động hoàn hảo ở cổng API `8000`. Cùng lúc đó bạn có thể start code Frontend bình thường.

## Troubleshooting FAQ

**Hỏi: Khi gõ `pip install insightface-0.7.3...` tôi bị báo lỗi Error in requirement?**
Trả lời: Hãy chắc chắn bạn đang đứng ở thư mục ngoài cùng (cùng cấp với thư mục `backend/` và file `.whl` đó chứ không phải đang đứng thụt vào trong `backend/`). Hoặc đơn giản là phiên bản Python của bạn không phải bản 3.11 64-bit. `Python -V` để kiểm tra.

**Hỏi: Import onnxruntime lib bị lỗi DLL Load Failed?**
Trả lời: Đảm bảo máy tính Windows 11 của bạn đã cài đặt xong Visual C++ Build Tools như ở bước 2, hãy thử Restart máy lại là xử lý xong.