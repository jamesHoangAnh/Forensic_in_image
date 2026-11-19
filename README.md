# Giám định ảnh JPEG và PNG — thực nghiệm

## 1. Mục tiêu và phạm vi

Kho mã này hiện thực các phép kiểm tra pháp chứng cơ bản từ báo cáo gốc, chia riêng theo định dạng JPEG và PNG. Mỗi tệp Python là một chương trình dòng lệnh độc lập, có đầu vào tệp ảnh và ghi kết quả JSON cùng hình minh họa (nếu có).

Các chương trình chỉ đọc ảnh đầu vào; không sửa ảnh gốc, không tạo hoặc nhúng payload, không trích xuất hay chạy nội dung nhúng. Kết quả là dấu hiệu hỗ trợ sàng lọc, không phải kết luận xác thực hay bằng chứng độc lập.

```text
jpeg/
  01_ela.py                 # Nén lại JPEG và tạo bản đồ sai khác ELA
  02_exif_inventory.py      # Đọc một tập trường EXIF, bỏ qua GPS
  03_copy_move_screen.py    # Sàng lọc các khối grayscale trùng khớp chính xác
png/
  01_chunk_audit.py         # Kiểm tra cấu trúc chunk, CRC và dữ liệu sau IEND
  02_lsb_statistics.py      # Thống kê bit thấp RGB và tạo ảnh trực quan hóa
requirements.txt
```

## 2. Cài đặt và chạy

Yêu cầu Python 3.10 trở lên. Tại thư mục gốc dự án, tạo môi trường ảo và cài hai thư viện cần thiết:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Trong VS Code, chọn interpreter `.venv` bằng lệnh **Python: Select Interpreter** để Pylance sử dụng đúng các thư viện vừa cài.

Chạy từng thực nghiệm độc lập:

```powershell
python .\jpeg\01_ela.py .\jpeg\output\ela_7501351.jpg
python .\jpeg\02_exif_inventory.py .\jpeg\output\ela_7501351.jpg
python .\jpeg\03_copy_move_screen.py .\jpeg\output\ela_7501351.jpg

python .\png\01_chunk_audit.py .\input\forged2.png
python .\png\02_lsb_statistics.py .\input\forged2.png
```

Có thể đổi thư mục kết quả bằng `--output-dir`. ELA nhận thêm `--quality` (mặc định 90) và `--scale` (mặc định 10); bộ dò copy-move nhận `--block-size`, `--stride`, `--min-distance`, `--max-blocks` và `--min-texture-stddev`. Mỗi chương trình in JSON ra màn hình và lưu báo cáo JSON trong thư mục kết quả mặc định cạnh script (`jpeg/output` hoặc `png/output`).

## 3. Thực nghiệm JPEG

### 3.1. ELA — `jpeg/01_ela.py`

**Mục tiêu:** quan sát mức sai khác giữa ảnh JPEG đầu vào và chính ảnh đó sau khi nén JPEG lại ở chất lượng đã chọn.

**Quy trình:** mở và chuyển ảnh sang RGB; lưu một bản JPEG nén lại; tính sai khác tuyệt đối từng kênh; nhân sai khác với hệ số hiển thị (mặc định 10) và giới hạn về `[0, 255]`. Kết quả gồm ảnh ELA PNG, bản JPEG nén lại và JSON có kích thước, chất lượng nén, sai khác trung bình/cực đại.

**Diễn giải:** vùng sáng là nơi sai khác sau lần nén lại lớn hơn, không đồng nghĩa chắc chắn với vùng bị ghép/chỉnh sửa. Kết quả phụ thuộc chất lượng nén ban đầu, các lần lưu trước, nội dung, chất lượng được chọn và hệ số hiển thị. ELA không phải phép kiểm tra PNG; chuyển PNG sang JPEG để làm ELA sẽ tạo sai khác do chuyển định dạng và không thể diễn giải như lịch sử JPEG của PNG.

**Kết quả cần ghi nhận:** xem ảnh ELA cùng ảnh gốc; so sánh nhiều thiết lập chất lượng một cách có kiểm soát nếu cần. Không dùng một ngưỡng độ sáng đơn lẻ để kết luận thật/giả.

**Kết quả chạy trên mẫu có sẵn:** `ela_7501351.jpg` (3840×2160), chất lượng nén lại 90, hệ số hiển thị 10: sai khác tuyệt đối trung bình mỗi kênh là `0.0016516`, cực đại `37`. Đây chỉ là số đo cho mẫu này, không phải ngưỡng phân loại.

### 3.2. EXIF — `jpeg/02_exif_inventory.py`

**Mục tiêu:** ghi nhận một số trường EXIF thường gặp (nhà sản xuất/model, thời gian, thông số chụp và hướng ảnh) để đối chiếu với các nguồn khác.

**Quy trình:** đọc EXIF bằng Pillow ở chế độ chỉ đọc; lưu các trường có trong ảnh vào JSON. GPS cố ý không được đưa vào báo cáo nhằm hạn chế lộ dữ liệu vị trí.

**Diễn giải:** EXIF có thể không tồn tại, bị ứng dụng xóa hoặc bị chỉnh sửa. Thời gian/thiết bị ghi trong EXIF không tự chứng minh nguồn gốc ảnh. Chương trình này không ghi hay sửa metadata.

**Kết quả mẫu:** ảnh JPEG thử nghiệm không có EXIF (`exif_present: false`); điều này chỉ nói về tệp mẫu được chạy, không đại diện cho mọi ảnh.

### 3.3. Sàng lọc copy-move — `jpeg/03_copy_move_screen.py`

**Mục tiêu:** tìm các khối grayscale 8×8 trùng khớp chính xác và cách nhau ít nhất một khoảng quy định; xuất mask để kiểm tra thủ công.

**Quy trình:** chuyển ảnh sang grayscale; bỏ qua khối có độ lệch chuẩn cường độ dưới 2 (lọc vùng gần như đồng nhất); quét khối chồng lấn với bước mặc định 4 pixel; nhóm các khối có byte pixel giống hệt nhau; loại các khớp gần nhau theo khoảng cách tối thiểu 16 pixel. Giới hạn mặc định một triệu khối tránh dùng bộ nhớ quá mức. Đổi stride, giới hạn hoặc ngưỡng lọc qua tham số dòng lệnh.

**Giới hạn:** đây là phép sàng lọc đơn giản, không phải thuật toán phát hiện copy-move hoàn chỉnh. Họa tiết lặp tự nhiên có thể tạo cảnh báo giả; xoay, co giãn, làm mờ hoặc tái lấy mẫu có thể khiến vùng sao chép bị bỏ sót. Tham số stride 4 cũng khác cách quét từng pixel (stride 1) trong phần mô tả lý thuyết của báo cáo.

**Kết quả mẫu:** trên cùng JPEG, đã quét 516,901 khối; 516,576 khối gần đồng nhất bị loại do ngưỡng độ lệch chuẩn 2; không có khối trùng được đánh dấu. Ảnh này không phải bộ kiểm thử copy-move có nhãn, nên kết quả không đo được độ chính xác của thuật toán.

## 4. Thực nghiệm PNG

### 4.1. Kiểm tra cấu trúc — `png/01_chunk_audit.py`

**Mục tiêu:** kiểm tra chữ ký PNG, ranh giới chunk, CRC, vị trí/kích thước cơ bản của IHDR, sự hiện diện của IDAT/IEND và byte còn lại sau IEND.

**Quy trình:** đọc cấu trúc chunk theo độ dài khai báo; tính CRC-32 trên loại chunk và dữ liệu; ghi danh sách chunk và các bất thường vào JSON. CRC sai, chunk bị cắt cụt, thiếu chunk thiết yếu hoặc có byte sau IEND được báo riêng.

**Diễn giải:** CRC đúng chỉ cho thấy dữ liệu chunk khớp với CRC đang có trong tệp, không chứng minh tệp nguyên bản hay chưa chỉnh sửa. Người sửa ảnh có thể tạo lại CRC hợp lệ. Một số cảnh báo cấu trúc cũng cần được đánh giá theo chuẩn PNG đầy đủ và nguồn ảnh; báo cáo này là bộ kiểm tra tối thiểu, không thay thế trình phân tích PNG đã được kiểm định.

**Kết quả mẫu:** `input/forged2.png` (256×256, 104,387 byte) có IHDR/IDAT/IEND, mọi CRC được kiểm tra đều hợp lệ, không phát hiện bất thường cấu trúc và không có byte sau IEND.

### 4.2. Thống kê LSB — `png/02_lsb_statistics.py`

**Mục tiêu:** thống kê tỷ lệ bit 1 và tỷ lệ chuyển tiếp ngang/dọc ở bit thấp nhất của từng kênh R/G/B; tạo ảnh RGB mà mỗi kênh trực quan hóa bit thấp tương ứng. Kênh alpha không được phân tích.

**Diễn giải:** số liệu gần 0,5 hoặc ảnh trực quan có nhiễu không đủ để kết luận có dữ liệu ẩn. Nội dung tự nhiên, bộ mã hóa và các thao tác xử lý ảnh cũng ảnh hưởng các thống kê này. Chương trình không trích xuất nội dung, không nhận diện/chạy tệp thực thi và không gắn nhãn “an toàn” hoặc “mã độc”.

**Kết quả mẫu:** tỷ lệ bit 1 lần lượt là R=`0.500427`, G=`0.500702`, B=`0.498383`; các tỷ lệ chuyển tiếp ngang/dọc đều xấp xỉ 0.5. Các trị số này không xác nhận cũng không loại trừ dữ liệu ẩn.

**Đặc điểm định dạng:** PNG dùng nén không mất dữ liệu nên lưu PNG thông thường bảo toàn giá trị pixel; JPEG là nén mất dữ liệu nên có thể làm thay đổi LSB. Điều này không có nghĩa mọi PNG đều chứa dữ liệu nhúng hoặc mọi thao tác chuyển đổi sang JPEG chắc chắn làm mất hoàn toàn một nội dung cụ thể.

## 5. Đầu ra và cách ghi nhận kết quả

Các file kết quả được tạo trong `jpeg/output` hoặc `png/output`; tên file bắt đầu từ tên ảnh nguồn. Mỗi báo cáo JSON ghi đầu vào và số liệu đo được để có thể kiểm tra lại. Hãy lưu nguyên ảnh đầu vào, ghi rõ phiên bản thư viện, tham số chạy và nguồn dữ liệu khi lập báo cáo thực nghiệm. Không suy diễn độ chính xác, tỷ lệ phát hiện hay kết luận giả mạo từ một ảnh đơn lẻ; các chỉ số đó cần bộ dữ liệu có nhãn, quy trình kiểm soát và đối chứng.

## 6. Hiệu đính so với báo cáo ban đầu

- ELA chỉ áp dụng cho quy trình JPEG; không mô tả ELA như phép kiểm tra trực tiếp trên PNG.
- EXIF chỉ là dữ liệu tham khảo có thể bị thiếu hoặc thay đổi, không phải bằng chứng bảo đảm toàn vẹn.
- Copy-move trong mã là phép tìm khối grayscale trùng chính xác, có giới hạn nêu trên; không khẳng định phát hiện được mọi dạng giả mạo.
- Bổ sung kiểm tra cấu trúc PNG/CRC và thống kê LSB như hai thực nghiệm PNG độc lập; CRC hoặc LSB không đưa ra kết luận xác thực tuyệt đối.
- Các mô tả tạo reverse shell, nhúng/chạy payload thực thi, ngụy trang tiến trình và các kết quả phát hiện mã độc định lượng không thuộc bộ thực nghiệm an toàn này, vì mã nguồn/dữ liệu đối chứng tương ứng không có trong workspace để kiểm chứng.

Bản báo cáo Word đã được cập nhật riêng thành `Bao_cao_forensic_anh_cap_nhat.docx`; tài liệu gốc dạng backup được giữ nguyên. Hãy cập nhật lại mục lục/phân trang trong Word trước khi in vì phần thực nghiệm đã được biên tập lại.