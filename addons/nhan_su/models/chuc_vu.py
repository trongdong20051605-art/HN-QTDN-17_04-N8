from odoo import models, fields


class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Quản lý chức vụ'
    _rec_name = 'ten_chuc_vu'

    ma_chuc_vu = fields.Char(string='Mã chức vụ', required=True)
    ten_chuc_vu = fields.Char(string='Tên chức vụ', required=True)
    mo_ta_cong_viec = fields.Text(string='Mô tả công việc')
    muc_luong_de_xuat = fields.Float(string='Mức lương theo chức vụ')
    phu_cap_chuc_vu = fields.Float(string='Phụ cấp chức vụ')
    cap_bac = fields.Selection([
        ('nhan_vien', 'Nhân viên'),
        ('to_truong', 'Tổ trưởng'),
        ('pho_phong', 'Phó phòng'),
        ('truong_phong', 'Trưởng phòng'),
        ('giam_doc', 'Giám đốc'),
    ], string='Cấp bậc', default='nhan_vien')

    trang_thai = fields.Selection([
        ('dang_su_dung', 'Đang sử dụng'),
        ('ngung_su_dung', 'Ngừng sử dụng'),
    ], string='Trạng thái', default='dang_su_dung')
    nhan_vien_ids = fields.One2many(
        'nhan_vien',
        'chuc_vu_id',
        string='Danh sách nhân viên'
    )
    _sql_constraints = [
        ('unique_ma_chuc_vu', 'unique(ma_chuc_vu)', 'Mã chức vụ không được trùng!')
    ]
