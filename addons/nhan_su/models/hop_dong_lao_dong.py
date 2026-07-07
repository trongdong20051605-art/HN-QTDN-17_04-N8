from odoo import models, fields, api
from odoo.exceptions import ValidationError


class HopDongLaoDong(models.Model):
    _name = 'hop_dong_lao_dong'
    _description = 'Quản lý hợp đồng lao động'
    _rec_name = 'so_hop_dong'
    _order = 'ngay_ky desc'

    so_hop_dong = fields.Char(string='Số hợp đồng', required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên', required=True)

    loai_hop_dong = fields.Selection([
        ('thu_viec', 'Hợp đồng thử việc'),
        ('xac_dinh_thoi_han', 'Hợp đồng xác định thời hạn'),
        ('khong_xac_dinh_thoi_han', 'Hợp đồng không xác định thời hạn'),
    ], string='Loại hợp đồng', required=True)

    ngay_ky = fields.Date(string='Ngày ký', required=True)
    ngay_bat_dau = fields.Date(string='Ngày bắt đầu', required=True)
    ngay_ket_thuc = fields.Date(string='Ngày kết thúc')

    muc_luong = fields.Float(string='Mức lương trong hợp đồng')
    phu_cap = fields.Float(string='Phụ cấp')
    noi_dung_cong_viec = fields.Text(string='Nội dung công việc')
    ghi_chu = fields.Text(string='Ghi chú')

    trang_thai = fields.Selection([
        ('hieu_luc', 'Đang hiệu lực'),
        ('sap_het_han', 'Sắp hết hạn'),
        ('het_han', 'Hết hạn'),
        ('da_cham_dut', 'Đã chấm dứt'),
    ], string='Trạng thái', default='hieu_luc')
   
    ty_le_bao_hiem = fields.Float(
    string='Tỷ lệ bảo hiểm (%)',
    default=10.5
    )

    @api.constrains('ngay_bat_dau', 'ngay_ket_thuc')
    def _check_ngay_hop_dong(self):
        for record in self:
            if record.ngay_ket_thuc and record.ngay_ket_thuc < record.ngay_bat_dau:
                raise ValidationError('Ngày kết thúc không được nhỏ hơn ngày bắt đầu.')

    _sql_constraints = [
        ('unique_so_hop_dong', 'unique(so_hop_dong)', 'Số hợp đồng không được trùng!')
    ]

