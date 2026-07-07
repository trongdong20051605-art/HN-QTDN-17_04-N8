from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ChamCong(models.Model):
    _name = 'cham_cong'
    _description = 'Bảng chấm công nhân viên'
    _rec_name = 'nhan_vien_id'
    _order = 'ngay_cham_cong desc'

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        required=True
    )

    ma_dinh_danh = fields.Char(
        string='Mã định danh',
        related='nhan_vien_id.ma_dinh_danh',
        store=True,
        readonly=True
    )

    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban',
        related='nhan_vien_id.phong_ban_id',
        store=True,
        readonly=True
    )

    chuc_vu_id = fields.Many2one(
        'chuc_vu',
        string='Chức vụ',
        related='nhan_vien_id.chuc_vu_id',
        store=True,
        readonly=True
    )

    ngay_cham_cong = fields.Date(
        string='Ngày chấm công',
        required=True,
        default=fields.Date.today
    )

    gio_vao = fields.Float(
        string='Giờ vào',
        default=8.0
    )

    gio_ra = fields.Float(
        string='Giờ ra',
        default=17.0
    )

    so_gio_lam = fields.Float(
        string='Số giờ làm',
        compute='_compute_so_gio_lam',
        store=True
    )

    gio_lam_them = fields.Float(
        string='Giờ làm thêm',
        default=0
    )

    trang_thai = fields.Selection([
        ('co_mat', 'Có mặt'),
        ('di_muon', 'Đi muộn'),
        ('vang', 'Vắng'),
        ('nghi_phep', 'Nghỉ phép'),
    ], string='Trạng thái', default='co_mat', required=True)

    ghi_chu = fields.Text(
        string='Ghi chú'
    )

    @api.depends('gio_vao', 'gio_ra', 'trang_thai')
    def _compute_so_gio_lam(self):
        for record in self:
            if record.trang_thai in ['vang', 'nghi_phep']:
                record.so_gio_lam = 0
            elif record.gio_vao and record.gio_ra and record.gio_ra >= record.gio_vao:
                record.so_gio_lam = record.gio_ra - record.gio_vao
            else:
                record.so_gio_lam = 0

    @api.constrains('gio_vao', 'gio_ra')
    def _check_gio_lam(self):
        for record in self:
            if record.gio_vao < 0 or record.gio_vao > 24:
                raise ValidationError('Giờ vào phải nằm trong khoảng 0 đến 24.')
            if record.gio_ra < 0 or record.gio_ra > 24:
                raise ValidationError('Giờ ra phải nằm trong khoảng 0 đến 24.')
            if record.gio_ra < record.gio_vao and record.trang_thai not in ['vang', 'nghi_phep']:
                raise ValidationError('Giờ ra không được nhỏ hơn giờ vào.')

    @api.constrains('gio_lam_them')
    def _check_gio_lam_them(self):
        for record in self:
            if record.gio_lam_them < 0:
                raise ValidationError('Giờ làm thêm không được nhỏ hơn 0.')
