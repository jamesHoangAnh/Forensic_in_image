import exifread

def phan_tich_exif_voi_exifread(duong_dan_anh):
    try:
        with open(duong_dan_anh, 'rb') as f:
            tags = exifread.process_file(f, details=True)
            if not tags:
                print("Không tìm thấy dữ liệu EXIF!")
                return None
            
            # Nhóm các tag
            nhom_tags = {'Image':[],
                        'EXIF':[], 
                        'GPS':[], 
                        'Thumbnail':[], 
                        'Other':[]
            }
            
            for tag, value in tags.items():
                if tag.startswith('Image'): nhom_tags['Image'].append((tag, value))
                elif tag.startswith('EXIF'): nhom_tags['EXIF'].append((tag, value))
                elif tag.startswith('GPS'): nhom_tags['GPS'].append((tag, value))
                elif tag.startswith('Thumbnail'): nhom_tags['Thumbnail'].append((tag, value))
                else: nhom_tags['Other'].append((tag, value))
            
            for nhom, items in nhom_tags.items():
                if items:
                    print(f"\n--- {nhom} Tags ---")
                    for tag, value in items:
                        print(f"{tag:40s}: {value}")
            return tags
    except Exception as e:
        print(f"Lỗi đọc file: {e}")
        return None

def lay_thong_tin_chi_tiet(duong_dan_anh):
    try:
        with open(duong_dan_anh, 'rb') as f:
            tags = exifread.process_file(f)
            thong_tin = {
                'Camera': tags.get('Image Model'),
                'Nhà sản xuất': tags.get('Image Make'),
                'Ngày chụp': tags.get('EXIF DateTimeOriginal'),
                'Kích thước ảnh': f"{tags.get('EXIF ExifImageWidth')} x {tags.get('EXIF ExifImageLength')}",
                'Độ phân giải': f"{tags.get('Image XResolution')} x {tags.get('Image YResolution')}",
                'ISO': tags.get('EXIF ISOSpeedRatings'),
                'Khẩu độ': tags.get('EXIF FNumber'),
                'Tốc độ màn trập': tags.get('EXIF ExposureTime'),
                'Tiêu cự': tags.get('EXIF FocalLength'),
                'Flash': tags.get('EXIF Flash'),
                'Phần mềm': tags.get('Image Software'),
            }
            print("\nThông tin camera và cài đặt:")
            print("-" * 80)
            for key, value in thong_tin.items():
                if value:
                    print(f"{key:25s}: {value}")
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    file_path = input("Nhập đường dẫn ảnh JPEG cần phân tích: ").strip()
    phan_tich_exif_voi_exifread(file_path)
    lay_thong_tin_chi_tiet(file_path)