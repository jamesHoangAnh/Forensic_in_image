from PIL import Image
import numpy as np
from scipy.stats import chisquare
import struct

class ForensicLSBDetector:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
        if self.image.mode != 'RGB': self.image = self.image.convert('RGB')
        
        self.flat_pixels = np.array(self.image).flatten()
        total_pixels = len(self.flat_pixels)
        
        if total_pixels < 100000: self.chunk_size = 5000
        elif total_pixels < 1000000: self.chunk_size = 10000
        else: self.chunk_size = 20000
        
        self.chunks = [self.flat_pixels[i:i + self.chunk_size] for i in range(0, len(self.flat_pixels), self.chunk_size)]

    def detect_sequential_drop(self):
        entropies = []
        for chunk in self.chunks:
            p = np.bincount(chunk & 1, minlength=2) / len(chunk)
            if 0 in p: entropies.append(0)
            else: entropies.append(-np.sum(p * np.log2(p)))
        
        diffs = [abs(entropies[i] - entropies[i+1]) for i in range(len(entropies)-1)]
        max_val = max(diffs) if diffs else 0
        idx = diffs.index(max_val) if diffs else 0
        capacity = (idx / len(self.chunks)) * 100 if self.chunks else 0
        
        return {'suspicious': max_val > 0.1, 'max_val': max_val, 'drop_index': idx, 'capacity': capacity}

    def local_balance_test(self):
        devs = []
        for chunk in self.chunks:
            lsb = chunk & 1
            mean_lsb = np.mean(lsb)
            devs.append(abs(mean_lsb - 0.5))
        
        ultra_rate = (sum(1 for d in devs if d < 0.002) / len(self.chunks)) * 100
        very_rate = (sum(1 for d in devs if d < 0.01) / len(self.chunks)) * 100
        mean_dev = np.mean(devs)
        std_dev = np.std(devs)
        
        criteria1 = ultra_rate > 50
        criteria2 = mean_dev < 0.1 and std_dev < 0.05
        return {'suspicious': criteria1 or criteria2, 'ultra_rate': ultra_rate, 'mean_dev': mean_dev}

    def adaptive_chi_square(self, drop_idx):
        sample_end = min((drop_idx + 1) * self.chunk_size, len(self.flat_pixels))
        sample = self.flat_pixels[:sample_end]
        hist, _ = np.histogram(sample, bins=256, range=(0, 256))
        
        obs, exp = [], []
        pair_diffs = []
        for i in range(0, 256, 2):
            combined = hist[i] + hist[i+1]
            if combined > 10:
                obs.extend([hist[i], hist[i+1]])
                exp.extend([combined/2, combined/2])
                pair_diffs.append(abs(hist[i] - hist[i+1]) / combined if combined > 0 else 0)
        
        chi2_stat, p_val = chisquare(obs, exp)
        total_obs = sum(obs)
        norm_chi2 = chi2_stat / total_obs if total_obs > 0 else 0
        balance_ratio = sum(1 for d in pair_diffs if d < 0.05) / len(pair_diffs) if pair_diffs else 0
        
        return {'suspicious': norm_chi2 < 0.01 and balance_ratio > 0.60, 'norm_chi2': norm_chi2}

    def check_pe_signature(self):
        ext = np.packbits(self.flat_pixels[:200000] & 1).tobytes()
        idx = ext.find(b'MZ')
        if idx != -1:
            try:
                pe_ptr = struct.unpack('<I', ext[idx+0x3C:idx+0x40])[0]
                if ext[idx+pe_ptr:idx+pe_ptr+4] == b'PE\0\0':
                    return {'suspicious': True, 'found_at': idx}
            except: pass
        return {'suspicious': False, 'found_at': None}

    def detect_all(self):
        drop_res = self.detect_sequential_drop()
        bal_res = self.local_balance_test()
        pe_res = self.check_pe_signature()
        chi_res = self.adaptive_chi_square(drop_res['drop_index'])
        
        score = 0
        if pe_res['suspicious']: score += 100
        if drop_res['suspicious']: score += 40
        if bal_res['suspicious']: score += 20
        if chi_res['suspicious']: score += 20
        
        print(f"\n--- KẾT QUẢ PHÂN TÍCH FORENSIC ---")
        print(f"TỔNG ĐIỂM NGUY CƠ: {score}/100")
        
        if score >= 100: verdict = "NGUY HIỂM: PHÁT HIỆN MÃ ĐỘC THỰC THI (.EXE) ẨN TRONG ẢNH"
        elif score >= 60: verdict = "CẢNH BÁO: PHÁT HIỆN DỮ LIỆU ẨN CÓ CẤU TRÚC BẤT THƯỜNG"
        elif score >= 40: verdict = "NGHI VẤN: CÓ DẤU HIỆU SỬ DỤNG CÔNG CỤ GIẤU TIN"
        else: verdict = "AN TOÀN: KHÔNG PHÁT HIỆN DỮ LIỆU BẤT THƯỜNG"
        
        print(f"KẾT LUẬN: {verdict}")
        return score

if __name__ == "__main__":
    path = input("Nhập đường dẫn ảnh cần kiểm tra steganography: ").strip()
    detector = ForensicLSBDetector(path)
    detector.detect_all()