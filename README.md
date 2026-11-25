# Forensic trong ảnh

Dự án thực hành giám định ảnh số bằng Python, tập trung vào ba nhóm nội dung:

1. Phân tích và thay đổi metadata EXIF của ảnh JPEG.
2. Phát hiện chỉnh sửa ảnh bằng Copy-move và Error Level Analysis (ELA).
3. Mô phỏng giấu tin LSB, trích xuất và phát hiện dữ liệu thực thi ẩn trong ảnh.

## Phạm vi và mục tiêu

- Tìm hiểu cấu trúc ảnh số, JPEG, metadata và dữ liệu EXIF.
- Kiểm tra độ tin cậy của EXIF như bằng chứng giám định.
- Phát hiện Copy-move bằng so khớp khối pixel.
- Phát hiện Splicing bằng phân tích sai lệch mức nén ELA.
- Mô phỏng Steganography bằng Least Significant Bit (LSB).
- Xây dựng bộ phát hiện steganography đa lớp cho dữ liệu thực thi.

Các phương pháp dùng trong dự án là minh họa truyền thống. Metadata có thể bị chỉnh sửa dễ dàng, còn Copy-move và ELA có thể sai sót khi ảnh bị xoay, làm mờ, tái nén hoặc xử lý nâng cao. Kết luận giám định nên dựa trên nhiều phương pháp thay vì một tín hiệu duy nhất.

## Cấu trúc dự án

```text
Forensic_in_image/
├── JPEG/
│   ├── exp1_analyze_exif.py
│   ├── exp1_modify_exif.py
│   ├── exp2_ela.py
│   └── output/
│
├── PNG\
    │   ├── exp2_copy_move.py
│   ├── exp3_hide_exe.py
│   ├── exp3_extractor.py
│   ├── exp3_forensic_detector.py
│   ├── exp3_payload.py
│   ├── exp3_c2_server.py
│   └── output/
├── input/
├── requirements.txt
└── README.md
```

## Dữ liệu mẫu

- `_BNB8179.jpg`: ảnh gốc cho thực nghiệm EXIF.
- `_BNB8179_MODIFIED.jpg`: ảnh sau chỉnh sửa metadata.
- `482142463_1153091206495882_5020505596692321905_n.jpg`: ảnh JPEG mẫu.
- `received_2550792785102777.jpeg` và `received_768112981488116.jpeg`: ảnh JPEG dùng cho phân tích ELA.
- `forged2.png`: ảnh Copy-move mẫu.
- `forged2_mask.png`: mặt nạ vùng giả mạo tham chiếu.
- `JPEG/output/`: ảnh ELA đã sinh ra ở mức nén chất lượng 75.

## Cài đặt

Yêu cầu Python 3 và pip.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Các thư viện chính được sử dụng:

- `exifread`: đọc metadata EXIF.
- `piexif`: đọc và ghi metadata EXIF.
- `Pillow`, `NumPy`: xử lý ảnh và bit dữ liệu.
- `OpenCV`: đọc ảnh, nén JPEG và phát hiện Copy-move.
- `Matplotlib`: hiển thị bản đồ ELA.
- `SciPy`: kiểm định chi-square trong steganalysis.

## Hướng dẫn chạy

Chạy từng script từ thư mục gốc hoặc thư mục `JPEG`. Các chương trình tương tác sẽ yêu cầu nhập đường dẫn ảnh.

### 1. Phân tích EXIF

```bash
python JPEG\exp1_analyze_exif.py
```

Chương trình mở ảnh ở chế độ nhị phân, phân nhóm các tag thành `Image`, `EXIF`, `GPS`, `Thumbnail` và `Other`, sau đó lọc các trường camera, thời gian, kích thước, ISO, khẩu độ, màn trập, tiêu cự, flash và phần mềm.

### 2. Chỉnh sửa EXIF

```bash
python JPEG\exp1_modify_exif.py
```

Có thể thay đổi:

- `DateTimeOriginal`, `DateTimeDigitized` và `DateTime`.
- Tọa độ GPS, gồm vĩ độ, kinh độ và hướng N/S/E/W.
- Hãng máy ảnh (`Make`) và model máy ảnh (`Model`).

Nếu ảnh chưa có EXIF, chương trình khởi tạo cấu trúc IFD mới rồi ghi ngược vào ảnh.

### 3. Phát hiện Copy-move

```bash
python PNG\exp2_copy_move.py
```

Thuật toán dùng khối xám 8×8, dịch cửa sổ với bước 1 pixel, sắp xếp các khối từ điển và đánh dấu hai vị trí có khối nội dung giống hệt nhau. Ảnh gốc dạng xám và mask nhị phân được lưu dưới dạng PNG trong `PNG/output/`, đồng thời hiển thị trên màn hình.

Hạn chế: có thể tăng số kết quả trùng do vùng đồng nhất và không ổn định với các phép xoay, scale hoặc làm mờ.

### 4. Phân tích ELA

```bash
python JPEG\exp2_ela.py
```

Chương trình nén lại ảnh JPEG ở chất lượng 75, lấy sai khác tuyệt đối theo từng kênh màu và chuẩn hóa toàn dải `[0, 255]`. Ảnh ELA được lưu trong `JPEG/output/` với tên dạng `<tên_gốc>_ela.png_Q75.png` và hiển thị bằng Matplotlib.

ELA phụ thuộc vào định dạng và lịch sử nén JPEG; vùng ghép có sai lệch nén nổi bật thường dễ quan sát hơn.

### 5. Nhúng dữ liệu bằng LSB

```bash
python PNG\exp3_hide_exe.py
```

Chương trình yêu cầu ảnh PNG gốc, file thực thi và đường dẫn ảnh đầu ra. Nó chuyển từng byte payload thành bit, thêm marker `<<EXE_START>>`, kích thước và marker `<<DATA_START>>`, sau đó ghi các bit vào bit thấp nhất của kênh R/G/B.

### 6. Trích xuất dữ liệu LSB

```bash
python PNG\exp3_extractor.py
```

Chương trình đọc lại bit thấp nhất của các pixel, tìm header marker, đọc kích thước payload, trích xuất byte thực thi và thực thi file tạm đã đổi tên `svchost.exe` trên Windows.

### 7. Phân tích steganography

```bash
python PNG\exp3_forensic_detector.py
```

Bộ phát hiện chấm điểm nguy cơ theo tối đa 100 điểm:

- Phát hiện chuỗi `MZ` và header PE: 100 điểm.
- Giảm entropy đột ngột giữa các chunk: 40 điểm.
- Cân bằng bit LSB trong từng chunk: 20 điểm.
- Adaptive Chi-square cân bằng cặp mức màu: 20 điểm.

Ngưỡng kết luận:

- `>= 100`: phát hiện mã thực thi `.exe` ẩn.
- `>= 60`: cảnh báo dữ liệu ẩn có cấu trúc bất thường.
- `>= 40`: nghi ngờ công cụ giấu tin.
- Dưới `40`: chưa phát hiện bất thường.

Điểm số là kết quả hỗ trợ phân tích, không thay thế xác minh bằng công cụ chuyên dụng và phân tích mẫu thực địa.

### 8. Mô phỏng payload và C2

```bash
python PNG\exp3_c2_server.py
```

Chạy server C2 trên `0.0.0.0:4444`, sau đó chạy payload ở máy thử nghiệm:

```bash
python PNG\exp3_payload.py
```

Payload thực thi lệnh shell và gửi kết quả TCP về server. Đây là nội dung mô phỏng reverse shell trong báo cáo. Chỉ chạy trong môi trường cô lập mà bạn được phép kiểm thử.

## Đánh giá kết quả thực nghiệm

### Metadata EXIF

EXIF cung cấp thông tin thiết bị, thời gian, thông số chụp và GPS. Tuy nhiên, dữ liệu này có thể bị thay đổi bằng `piexif` hoặc các công cụ chuyên dụng. Vì vậy, EXIF chỉ có giá trị tham khảo và không bảo đảm tính toàn vẹn.

### Copy-move và Splicing

- Block-based Copy-move phù hợp khi vùng sao chép giữ nguyên cấu trúc pixel theo Lossless của PNG.
- ELA hỗ trợ phát hiện vùng ghép do sai khác mức nén JPEG.
- Các kết quả nên được đối chiếu với metadata, vùng nhiễu, mặt nạ và lịch sử nén.

### Steganography và Steganalysis

LSB có khả năng che giấu dữ liệu với ít thay đổi quan sát trực quan. Bộ phát hiện đa lớp có thể nhận diện dữ liệu nhúng dựa trên sự cân bằng bit, thay đổi entropy, chi-square và chữ ký PE. Hệ thống hiện chủ yếu hữu hiệu với payload có cấu trúc PE và dữ liệu nhúng tuần tự.

## Hạn chế

- Chưa tích hợp mô hình học máy hoặc học sâu.
- Bộ dữ liệu thực nghiệm còn nhỏ và chủ yếu ở điều kiện kiểm soát.
- Copy-move chưa xử lý đầy đủ xoay, scale và biến đổi hình học.
- ELA phụ thuộc lịch sử nén và định dạng JPEG.
- Steganalysis chủ yếu hướng tới LSB cơ bản, chưa bao quát các kỹ thuật nhúng nâng cao.

Hướng phát triển phù hợp: xây dựng bộ dữ liệu chuẩn hóa, tích hợp CNN/Transformer, áp dụng phân tích noise residual trong miền tần số, và nghiên cứu steganalysis thống kê cho nhiều phương pháp nhúng.

## Cảnh báo an toàn

Các file `exp3_payload.py`, `exp3_extractor.py`, `exp3_hide_exe.py` và `exp3_c2_server.py` mô phỏng hành vi điều khiển từ xa và thực thi mã. Chỉ sử dụng trên máy thử nghiệm do bạn sở hữu hoặc có quyền kiểm thử rõ ràng. Không nhúng, phân phối hoặc kích hoạt payload trên hệ thống người khác.
