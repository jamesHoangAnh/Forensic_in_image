import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path

class ELADetector:
    def __init__(self, quality=75):
        self.quality = quality
        self.original_image = None
        self.recompressed_image = None
        self.ela_map = None

    def load_image(self, image_path: str):
        if not os.path.exists(image_path):
            raise FileNotFoundError("Không tìm thấy ảnh")
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError("Không đọc được ảnh")
        self.original_image = image
        return image

    def recompress_jpeg(self, image):
        param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
        _, buffer = cv2.imencode(".jpg", image, param)
        self.recompressed_image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)

    def compute_ela_color(self):
        diff = cv2.absdiff(self.original_image, self.recompressed_image)
        max_val = np.max(diff)
        scale = 255.0 / max_val if max_val != 0 else 1
        ela_color = np.clip(diff * scale, 0, 255).astype(np.uint8)
        self.ela_map = ela_color
        return ela_color

    #output the ELA image to a file
    def save_ela(self, original_path: str):
        if self.ela_map is None:
            raise ValueError("ELA map chưa được tính toán")
        ela_filename = Path(original_path).stem + "_ela.png" + f"_Q{self.quality}.png"
        ela_path = Path("F:/Project/LapTrinhKichBan/Forensic_in_image/JPEG/output") / ela_filename
        ela_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(ela_path), self.ela_map)
        print(f"Đã lưu ảnh ELA tại: {ela_path}")

    def show(self):
        ela_rgb = cv2.cvtColor(self.ela_map, cv2.COLOR_BGR2RGB)
        plt.imshow(ela_rgb)
        plt.title(f"ELA Result (Q={self.quality})")
        plt.axis("off")
        plt.show()

if __name__ == "__main__":
    path = input("Nhập đường dẫn ảnh nghi vấn splicing: ").strip()
    detector = ELADetector(quality=75)
    detector.load_image(path)
    detector.recompress_jpeg(detector.original_image)
    detector.compute_ela_color()
    detector.save_ela(path)
    detector.show()