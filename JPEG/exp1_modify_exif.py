import piexif
from datetime import datetime

def parse_datetime_input(date_input):
    try:
        # Hỗ trợ nhiều định dạng nhập vào
        for fmt in ('%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S'):
            try:
                dt = datetime.strptime(date_input, fmt)
                return dt.strftime('%Y:%m:%d %H:%M:%S')
            except ValueError:
                continue
        return None
    except:
        return None

def change_to_rational(value):
    # Chuyển đổi số thực thập phân sang phân số (tử, mẫu) cho chuẩn EXIF GPS
    f = float(value)
    denominator = 1000000
    numerator = int(f * denominator)
    return (numerator, denominator)

def change_datetime_original(exif_dict):
    date_input = input("\nNhập ngày giờ chụp (VD: 2026:11:20 10:30:00): ").strip()
    parsed_date = parse_datetime_input(date_input)
    if parsed_date:
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = parsed_date.encode()
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = parsed_date.encode()
        exif_dict["0th"][piexif.ImageIFD.DateTime] = parsed_date.encode()
        print(f"Đã cập nhật DateTimeOriginal: {parsed_date}")
    else:
        print("Định dạng ngày giờ không hợp lệ!")

def change_location(exif_dict):
    try:
        latitude = float(input("\nNhập vĩ độ (Latitude): ").strip())
        longitude = float(input("Nhập kinh độ (Longitude): ").strip())
        
        lat_ref = b"N" if latitude >= 0 else b"S"
        lng_ref = b"E" if longitude >= 0 else b"W"
        
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = lat_ref
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = [change_to_rational(abs(latitude)), (0, 1), (0, 1)]
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = lng_ref
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = [change_to_rational(abs(longitude)), (0, 1), (0, 1)]
        return True
    except ValueError:
        print("Tọa độ không hợp lệ!")
        return False

def change_camera_info(exif_dict):
    make = input("Nhập hãng máy ảnh (Make) [Enter để bỏ qua]: ").strip()
    if make: exif_dict["0th"][piexif.ImageIFD.Make] = make.encode()
    
    model = input("Nhập model máy ảnh (Model) [Enter để bỏ qua]: ").strip()
    if model: exif_dict["0th"][piexif.ImageIFD.Model] = model.encode()

def save_changes(filename, exif_dict):
    try:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, filename)
        print(f"\nĐã lưu thành công vào file: {filename}")
    except Exception as e:
        print(f"\nLỗi khi lưu file: {e}")

if __name__ == "__main__":
    filename = input("Nhập đường dẫn file ảnh cần chỉnh sửa: ").strip()
    try:
        exif_dict = piexif.load(filename)
    except:
        exif_dict = {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}
        
    change_datetime_original(exif_dict)
    change_location(exif_dict)
    change_camera_info(exif_dict)
    save_changes(filename, exif_dict)