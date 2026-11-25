from pathlib import Path

import cv2
import numpy as np

BLOCK_SIZE = 8
STEP = 1

def detect_copy_move_basic(image_path):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print("Không đọc được ảnh!")
        return None, None
    
    h, w = img.shape
    blocks = []
    positions = []

    print(f"Đang xử lý ảnh {w}x{h}...")
    print(f"Số lượng block cần xử lý: {((w - BLOCK_SIZE + 1) // STEP) * ((h - BLOCK_SIZE + 1) // STEP)}")

    # 1. Chia block
    for y in range(0, h - BLOCK_SIZE + 1, STEP):
        for x in range(0, w - BLOCK_SIZE + 1, STEP):
            block = img[y:y+BLOCK_SIZE, x:x+BLOCK_SIZE]
            blocks.append(block.flatten())
            positions.append((y, x))
    
    blocks = np.array(blocks)
    print(f"Đã trích xuất {len(blocks)} blocks. Đang sắp xếp...")

    # 2. Lexicographic sort
    idx = np.lexsort(blocks.T)
    blocks = blocks[idx]
    positions = [positions[i] for i in idx]
    print("Đang so khớp các block...")

    # 3. So khớp
    mask = np.zeros_like(img)
    match_count = 0
    for i in range(len(blocks) - 1):
        if np.array_equal(blocks[i], blocks[i+1]):
            y1, x1 = positions[i]
            y2, x2 = positions[i+1]
            mask[y1:y1+BLOCK_SIZE, x1:x1+BLOCK_SIZE] = 255
            mask[y2:y2+BLOCK_SIZE, x2:x2+BLOCK_SIZE] = 255
            match_count += 1
    
    print(f"Phát hiện {match_count} cặp block trùng khớp!")
    return img, mask

if __name__ == "__main__":
    path = input("Nhập đường dẫn ảnh nghi vấn copy-move: ").strip()
    img, mask = detect_copy_move_basic(path)
    
    if img is None or mask is None:
        print("Chương trình kết thúc do lỗi.")
    else:
        output_dir = Path(__file__).resolve().parent / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        input_name = Path(path).stem
        original_output = output_dir / f"{input_name}_copy_move_original.png"
        mask_output = output_dir / f"{input_name}_copy_move_mask.png"

        if not cv2.imwrite(str(original_output), img):
            raise OSError(f"Không thể lưu ảnh gốc: {original_output}")
        if not cv2.imwrite(str(mask_output), mask):
            raise OSError(f"Không thể lưu mask: {mask_output}")
        print(f"Đã lưu ảnh gốc: {original_output}")
        print(f"Đã lưu mask: {mask_output}")

        print("\n" + "="*50)
        print("Đang hiển thị kết quả...")
        print("Nhấn phím bất kỳ để đóng cửa sổ và thoát.")
        print("="*50)
        
        # Hiển thị kết quả
        cv2.imshow("Original (Gray) - Nhan phim de thoat", img)
        cv2.imshow("Detected Mask - Nhan phim de thoat", mask)
        
        # Chờ nhấn phím với timeout 30 giây (30000ms)
        # Nếu không nhấn phím, chương trình vẫn tự thoát sau 30s
        key = cv2.waitKey(0)
        print(f"Bạn đã nhấn phím: {key}")
        
        cv2.destroyAllWindows()
        print("Chương trình đã kết thúc.")