from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BangLuongThang(models.Model):
    _name = 'bang_luong_thang'
    _description = 'Bảng lương tháng'
    _rec_name = 'ten_bang_luong'
    _order = 'nam desc, thang desc'

    ten_bang_luong = fields.Char(
        string='Tên bảng lương',
        compute='_compute_ten_bang_luong',
        store=True
    )

    thang = fields.Selection([
        ('1', 'Tháng 1'),
        ('2', 'Tháng 2'),
        ('3', 'Tháng 3'),
        ('4', 'Tháng 4'),
        ('5', 'Tháng 5'),
        ('6', 'Tháng 6'),
        ('7', 'Tháng 7'),
        ('8', 'Tháng 8'),
        ('9', 'Tháng 9'),
        ('10', 'Tháng 10'),
        ('11', 'Tháng 11'),
        ('12', 'Tháng 12'),
    ], string='Tháng', required=True)

    nam = fields.Integer(
        string='Năm',
        required=True,
        default=2026
    )

    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban'
    )

    line_ids = fields.One2many(
        'bang_luong_thang_line',
        'bang_luong_id',
        string='Chi tiết bảng lương'
    )

    tong_nhan_vien = fields.Integer(
        string='Tổng nhân viên',
        compute='_compute_tong_hop',
        store=True
    )

    tong_luong_co_ban = fields.Float(
        string='Tổng lương cơ bản',
        compute='_compute_tong_hop',
        store=True
    )

    tong_tien_lam_them = fields.Float(
        string='Tổng tiền làm thêm',
        compute='_compute_tong_hop',
        store=True
    )

    tong_bao_hiem = fields.Float(
        string='Tổng bảo hiểm',
        compute='_compute_tong_hop',
        store=True
    )

    tong_thuong = fields.Float(
        string='Tổng thưởng',
        compute='_compute_tong_hop',
        store=True
    )

    tong_khau_tru = fields.Float(
        string='Tổng khấu trừ',
        compute='_compute_tong_hop',
        store=True
    )

    tong_thuc_linh = fields.Float(
        string='Tổng thực lĩnh',
        compute='_compute_tong_hop',
        store=True
    )

    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_tong_hop', 'Đã tổng hợp'),
        ('da_chot', 'Đã chốt bảng lương'),
    ], string='Trạng thái', default='nhap')

    ghi_chu = fields.Text(string='Ghi chú')

    @api.depends('thang', 'nam', 'phong_ban_id')
    def _compute_ten_bang_luong(self):
        for record in self:
            if record.thang and record.nam:
                if record.phong_ban_id:
                    record.ten_bang_luong = (
                        f'Bảng lương tháng {record.thang}/{record.nam} - {record.phong_ban_id.ten_phong_ban}'
                    )
                else:
                    record.ten_bang_luong = f'Bảng lương tháng {record.thang}/{record.nam}'
            else:
                record.ten_bang_luong = 'Bảng lương'

    def _compute_tong_hop(self):
        for record in self:
            record.tong_nhan_vien = len(record.line_ids)
            record.tong_luong_co_ban = sum(record.line_ids.mapped('luong_co_ban'))
            record.tong_tien_lam_them = sum(record.line_ids.mapped('tien_lam_them'))
            record.tong_bao_hiem = sum(record.line_ids.mapped('tien_bao_hiem'))
            record.tong_thuong = sum(record.line_ids.mapped('thuong'))
            record.tong_khau_tru = sum(record.line_ids.mapped('khau_tru'))
            record.tong_thuc_linh = sum(record.line_ids.mapped('thuc_linh'))

    def action_tong_hop_bang_luong(self):
        for record in self:
            if not record.thang or not record.nam:
                raise ValidationError('Vui lòng chọn tháng và năm.')

            domain = [
                ('thang', '=', record.thang),
                ('nam', '=', record.nam),
                ('trang_thai', 'in', ['da_duyet', 'da_tra']),
            ]

            if record.phong_ban_id:
                domain.append(('phong_ban_id', '=', record.phong_ban_id.id))

            phieu_luongs = self.env['tinh_luong'].search(domain)

            if not phieu_luongs:
                raise ValidationError(
                    'Không tìm thấy phiếu lương đã duyệt hoặc đã trả lương trong tháng/năm này.'
                )

            record.line_ids.unlink()

            for phieu in phieu_luongs:
                self.env['bang_luong_thang_line'].create({
                    'bang_luong_id': record.id,
                    'tinh_luong_id': phieu.id,
                    'nhan_vien_id': phieu.nhan_vien_id.id,
                    'ma_dinh_danh': phieu.ma_dinh_danh,
                    'phong_ban_id': phieu.phong_ban_id.id if phieu.phong_ban_id else False,
                    'chuc_vu_id': phieu.chuc_vu_id.id if phieu.chuc_vu_id else False,
                    'luong_co_ban': phieu.luong_co_ban,
                    'tong_ngay_cong': phieu.tong_ngay_cong,
                    'tong_gio_lam_them': phieu.tong_gio_lam_them,
                    'tien_lam_them': phieu.tien_lam_them,
                    'tien_bao_hiem': phieu.tien_bao_hiem,
                    'thuong': phieu.thuong,
                    'khau_tru': phieu.khau_tru,
                    'thuc_linh': phieu.thuc_linh,
                    'trang_thai_luong': phieu.trang_thai,
                })

            record.trang_thai = 'da_tong_hop'

    def action_chot_bang_luong(self):
        for record in self:
            if not record.line_ids:
                raise ValidationError('Chưa có dữ liệu bảng lương để chốt.')

            record.trang_thai = 'da_chot'

    def action_dat_ve_nhap(self):
        for record in self:
            record.trang_thai = 'nhap'

    _sql_constraints = [
        (
            'unique_bang_luong_thang',
            'unique(thang, nam, phong_ban_id)',
            'Bảng lương tháng này đã tồn tại!'
        )
    ]


class BangLuongThangLine(models.Model):
    _name = 'bang_luong_thang_line'
    _description = 'Chi tiết bảng lương tháng'

    bang_luong_id = fields.Many2one(
        'bang_luong_thang',
        string='Bảng lương tháng',
        required=True,
        ondelete='cascade'
    )

    tinh_luong_id = fields.Many2one(
        'tinh_luong',
        string='Phiếu lương gốc',
        readonly=True
    )

    nhan_vien_id = fields.Many2one(
        'nhan_vien',
        string='Nhân viên',
        readonly=True
    )

    ma_dinh_danh = fields.Char(
        string='Mã định danh',
        readonly=True
    )

    phong_ban_id = fields.Many2one(
        'phong_ban',
        string='Phòng ban',
        readonly=True
    )

    chuc_vu_id = fields.Many2one(
        'chuc_vu',
        string='Chức vụ',
        readonly=True
    )

    luong_co_ban = fields.Float(
        string='Lương cơ bản',
        readonly=True
    )

    tong_ngay_cong = fields.Float(
        string='Tổng ngày công',
        readonly=True
    )

    tong_gio_lam_them = fields.Float(
        string='Tổng giờ làm thêm',
        readonly=True
    )

    tien_lam_them = fields.Float(
        string='Tiền làm thêm',
        readonly=True
    )

    tien_bao_hiem = fields.Float(
        string='Tiền bảo hiểm',
        readonly=True
    )

    thuong = fields.Float(
        string='Thưởng',
        readonly=True
    )

    khau_tru = fields.Float(
        string='Khấu trừ',
        readonly=True
    )

    thuc_linh = fields.Float(
        string='Thực lĩnh',
        readonly=True
    )

    trang_thai_luong = fields.Selection([
        ('nhap', 'Nháp'),
        ('cho_duyet', 'Chờ phê duyệt'),
        ('da_duyet', 'Đã phê duyệt'),
        ('tu_choi', 'Từ chối'),
        ('da_tra', 'Đã trả lương'),
    ], string='Trạng thái phiếu lương', readonly=True)