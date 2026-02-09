"""
Entry point để chạy app: python run.py
Hoặc dùng: uvicorn backend.src.main:app --reload
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # auto-reload khi dev
        log_level="info",
    )
