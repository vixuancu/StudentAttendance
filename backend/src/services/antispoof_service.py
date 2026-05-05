import os
import threading
import cv2
import numpy as np
from pathlib import Path

import onnxruntime as ort

class AntiSpoofPredictor:
    def __init__(self, model_path=None):
        self._lock = threading.Lock()
        self.session = None
        self.model_loaded = False
        
        if model_path is None:
            # Resolve default path from current file
            base_dir = Path(__file__).resolve().parents[3]
            model_path = base_dir / "ai_core" / "models" / "antispoof" / "minifasnet.onnx"
            
        self.model_path = str(model_path)
            
    def _load_model(self):
        with self._lock:
            if self.model_loaded:
                return True
                
            if not os.path.exists(self.model_path):
                print(f"[AntiSpoof] Model ONNX not found at {self.model_path}")
                return False
                
            try:
                # Cấu hình onnxruntime chạy trên CPU
                options = ort.SessionOptions()
                options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                self.session = ort.InferenceSession(self.model_path, options, providers=['CPUExecutionProvider'])
                self.input_name = self.session.get_inputs()[0].name
                self.model_loaded = True
                print(f"[AntiSpoof] ONNX Model loaded successfully.")
                return True
            except Exception as e:
                print(f"[AntiSpoof] Failed to load ONNX model: {e}")
                return False
                
    def check_liveness(self, image: np.ndarray, face_box=None) -> tuple[bool, float]:
        """
        Dự đoán ảnh mặt thật hay giả với mô hình MiniFASNet qua ONNX.
        Returns:
            is_real (bool): True if real, False if spoof
            score (float): Confidence score của liveness (>= 0.7 được coi là thật)
        """
        if not self.model_loaded:
            if not self._load_model():
                # Failsafe
                return True, 1.0
                
        if image is None or image.size == 0:
            return False, 0.0

        try:
            # Theo chuẩn Silent-Face-Anti-Spoofing, input đầu vào:
            # - Tỉ lệ 80x80
            # - Không cần chuyển RGB -> Model dùng BGR format (do cv2.imread_color lúc train)
            # - Chuẩn hóa (Normalization) để hạn chế noise/mờ của camera
            # 
            # Tuy nhiên do thuật toán nhận crop từ module insightface cắt sẵn quá hẹp, 
            # nó thiếu background. Sẽ bị dự báo lầm là giả nếu như crop quá chật.
            # Tạm thời bổ sung Padding nếu đc, hoặc resize chuẩn nhất.
            img = cv2.resize(image, (80, 80))
            
            # Chuẩn hóa tensor float
            img_tensor = np.zeros((1, 3, 80, 80), dtype=np.float32)
            
            # Repos sử dụng BGR. Tác giả đã bỏ chia 255 ở custom ToTensor() nên ta giữ nguyên pixel 0-255
            for i in range(3):
                img_tensor[0, i, :, :] = img[:, :, i]

            # ONNX Inference
            output = self.session.run(None, {self.input_name: img_tensor})[0]
            
            # Model MiniFASNet trả về 3 values cho 3 class: [fake_score, real_score, fake_score]
            # Ta áp dụng Softmax.
            preds = output[0]
            
            exp_preds = np.exp(preds - np.max(preds))
            probs = exp_preds / np.sum(exp_preds)
            
            # Index 1 là class REAL. 
            real_score = probs[1]

            # Nâng Threshold lên cao (0.85) để hệ thống nhận diện gắt gao hơn đối với màn hình điện thoại
            # Vì ta đã cấu hình Frontend lúc nãy (ở react-component) padding mở rộng box x2.2 lần
            # Hình ảnh lúc này đã bao quát cả quang cảnh viền điện thoại -> Mô hình sẽ thấy rất rõ
            threshold = 0.92

            return (real_score >= threshold), float(real_score)

        except Exception as e:
            print(f"[AntiSpoof] Error tracking: {e}")
            return True, 1.0

# Global instance
_predictor = None

def get_antispoof_predictor():
    global _predictor
    if _predictor is None:
        _predictor = AntiSpoofPredictor()
    return _predictor

def check_liveness(image: np.ndarray) -> tuple[bool, float]:
    """Helper function to call global predictor"""
    predictor = get_antispoof_predictor()
    return predictor.check_liveness(image)