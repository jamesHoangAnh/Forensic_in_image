from PIL import Image
import numpy as np

class LSBHider:
    def __init__(self):
        self.HEADER_MARKER = "<<EXE_START>>"
        self.DATA_MARKER = "<<DATA_START>>"

    def file_to_binary(self, file_path):
        with open(file_path, 'rb') as f:
            file_bytes = f.read()
        binary = ''.join(format(byte, '08b') for byte in file_bytes)
        return binary, len(file_bytes)

    def create_header(self, file_size):
        header = f"{self.HEADER_MARKER}{file_size:010d}{self.DATA_MARKER}"
        return ''.join(format(ord(c), '08b') for c in header)

    def hide_exe(self, image_path, exe_path, output_path):
        exe_binary, exe_size = self.file_to_binary(exe_path)
        header_binary = self.create_header(exe_size)
        full_binary = header_binary + exe_binary

        img = Image.open(image_path)
        if img.mode != 'RGB': img = img.convert('RGB')
        img_array = np.array(img)

        if img_array.size * 3 < len(full_binary):
            raise ValueError("Ảnh quá nhỏ để chứa file thực thi!")

        bit_index = 0
        for i in range(img_array.shape[0]):
            for j in range(img_array.shape[1]):
                for k in range(3): # R, G, B
                    if bit_index < len(full_binary):
                        img_array[i, j, k] = (img_array[i, j, k] & 0xFE) | int(full_binary[bit_index])
                        bit_index += 1
                    else: break
                if bit_index >= len(full_binary): break
            if bit_index >= len(full_binary): break

        result = Image.fromarray(img_array)
        result.save(output_path, 'PNG')
        print(f"[+] Đã nhúng thành công vào {output_path}")

if __name__ == "__main__":
    img_in = input("Đường dẫn ảnh gốc (PNG): ").strip()
    exe_in = input("Đường dẫn file payload.exe: ").strip()
    img_out = input("Đường dẫn ảnh xuất ra (stego.png): ").strip()
    LSBHider().hide_exe(img_in, exe_in, img_out)
    P