# GAP ANALYSIS - Đề tài Chấm công liên hệ Tính lương liên hệ Nhân sự

## 1. Mục tiêu
Xác định phần đã kế thừa và phần cần phát triển mới để hệ thống đáp ứng nghiệp vụ tích hợp giữa Nhân sự, Chấm công và Tính lương.

## 2. Phần kế thừa
Các chức năng đã có:
- Quản lý nhân viên
- Quản lý phòng ban
- Quản lý chức vụ
- Quản lý hợp đồng lao động
- Quản lý chấm công hằng ngày
- Tạo phiếu lương
- Tính thực lĩnh
- Phê duyệt lương
- Bảng lương, sao kê cá nhân, báo cáo lương

## 3. Khoảng trống nghiệp vụ
Các chức năng còn thiếu:
- Bảng công tháng để tổng hợp dữ liệu chấm công.
- Quy trình duyệt bảng công trước khi tính lương.
- Phiếu lương chưa lấy lương từ hợp đồng lao động.
- Phiếu lương chưa lấy ngày công từ bảng công đã duyệt.
- Chưa có cảnh báo nhân viên đi muộn, vắng nhiều hoặc làm thêm bất thường.
- Chưa có AI trợ lý hỗ trợ người dùng tra cứu dữ liệu.

## 4. Phần phát triển mới
Nhóm bổ sung:
- Model Bảng công tháng.
- Quy trình Tổng hợp công và Duyệt bảng công.
- Cập nhật phiếu lương lấy dữ liệu từ hợp đồng và bảng công đã duyệt.
- Module Trợ lý AI.
- Cảnh báo chấm công bất thường.
- Sơ đồ business flow end-to-end.

## 5. Kết luận
Sau khi bổ sung các chức năng trên, hệ thống thể hiện rõ luồng nghiệp vụ tích hợp giữa HRM, Chấm công và Tính lương. Dữ liệu nhân viên được dùng làm dữ liệu gốc, tránh hardcoding và tránh nhập liệu trùng lặp.