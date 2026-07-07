# Business Flow - Chấm công liên hệ Tính lương liên hệ Nhân sự

```mermaid
flowchart TD
    A[HR tạo phòng ban, chức vụ] --> B[HR tạo hồ sơ nhân viên]
    B --> C[HR tạo hợp đồng lao động]
    C --> D[Nhân viên đi làm hằng ngày]
    D --> E[Nhân sự/Quản lý nhập chấm công]
    E --> F[Hệ thống tổng hợp bảng công tháng]
    F --> G[Trưởng phòng duyệt bảng công]
    G --> H[Kế toán tạo phiếu lương]
    H --> I[Hệ thống lấy dữ liệu HRM + hợp đồng + bảng công]
    I --> J[Hệ thống tự tính lương]
    J --> K[Kế toán gửi phê duyệt lương]
    K --> L[Quản lý phê duyệt lương]
    L --> M[Kế toán đánh dấu đã trả lương]
    M --> N[AI trợ lý tóm tắt, tra cứu, cảnh báo]

    B -.Dữ liệu gốc HRM.-> E
    C -.Lương, phụ cấp, bảo hiểm.-> I
    G -.Bảng công đã duyệt.-> I
    N -.Input: câu hỏi người dùng.-> O[AI xử lý dữ liệu trong Odoo]
    O -.Output: câu trả lời/tóm tắt/cảnh báo.-> N