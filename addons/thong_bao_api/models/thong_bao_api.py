from odoo import models, fields, api
from odoo.exceptions import ValidationError
import requests


class CauHinhTelegram(models.Model):
    _name = 'cau_hinh_telegram'
    _description = 'Cấu hình Telegram API'
    _rec_name = 'ten_cau_hinh'

    ten_cau_hinh = fields.Char(
        string='Tên cấu hình',
        default='Cấu hình Telegram'
    )

    bot_token = fields.Char(
        string='Bot Token',
        required=True
    )

    chat_id = fields.Char(
        string='Chat ID',
        required=True
    )

    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_kiem_tra', 'Đã kiểm tra kết nối'),
        ('loi', 'Lỗi kết nối'),
    ], string='Trạng thái', default='nhap')

    ket_qua_kiem_tra = fields.Text(
        string='Kết quả kiểm tra',
        readonly=True
    )

    def action_kiem_tra_ket_noi(self):
        for record in self:
            message = 'Kiểm tra kết nối Telegram API từ hệ thống Odoo thành công.'
            ok, result = record._gui_telegram(message)

            record.ket_qua_kiem_tra = result
            record.trang_thai = 'da_kiem_tra' if ok else 'loi'

    def _gui_telegram(self, message):
        self.ensure_one()

        if not self.bot_token or not self.chat_id:
            return False, 'Thiếu Bot Token hoặc Chat ID.'

        url = f'https://api.telegram.org/bot{self.bot_token}/sendMessage'

        try:
            response = requests.post(
                url,
                data={
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML',
                },
                timeout=30
            )

            if response.status_code == 200:
                return True, response.text

            return False, response.text

        except Exception as e:
            return False, str(e)


class LichSuThongBaoTelegram(models.Model):
    _name = 'lich_su_thong_bao_telegram'
    _description = 'Lịch sử thông báo Telegram'
    _order = 'create_date desc'

    tieu_de = fields.Char(
        string='Tiêu đề',
        required=True
    )

    noi_dung = fields.Text(
        string='Nội dung',
        required=True
    )

    loai_thong_bao = fields.Selection([
        ('canh_bao_cham_cong', 'Cảnh báo chấm công'),
        ('luong_cho_duyet', 'Lương chờ phê duyệt'),
        ('tong_quan', 'Tổng quan hệ thống'),
        ('khac', 'Khác'),
    ], string='Loại thông báo', default='khac')

    trang_thai_gui = fields.Selection([
        ('chua_gui', 'Chưa gửi'),
        ('da_gui', 'Đã gửi'),
        ('loi', 'Lỗi gửi'),
    ], string='Trạng thái gửi', default='chua_gui')

    ket_qua_api = fields.Text(
        string='Kết quả API',
        readonly=True
    )

    ngay_gui = fields.Datetime(
        string='Ngày gửi',
        readonly=True
    )

    def action_gui_telegram(self):
        cau_hinh = self.env['cau_hinh_telegram'].search([], limit=1)

        if not cau_hinh:
            raise ValidationError('Chưa có cấu hình Telegram API.')

        for record in self:
            ok, result = cau_hinh._gui_telegram(record.noi_dung)

            record.ket_qua_api = result
            record.trang_thai_gui = 'da_gui' if ok else 'loi'
            record.ngay_gui = fields.Datetime.now()


class TelegramService(models.Model):
    _name = 'telegram_service'
    _description = 'Dịch vụ gửi Telegram'

    name = fields.Char(default='Telegram Service')

    def _mo_lich_su_thong_bao(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Lịch sử thông báo Telegram',
            'res_model': 'lich_su_thong_bao_telegram',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def action_tao_thong_bao_tong_quan_he_thong(self):
        tong_nhan_vien = self.env['nhan_vien'].search_count([])
        tong_phong_ban = self.env['phong_ban'].search_count([])
        tong_chuc_vu = self.env['chuc_vu'].search_count([])
        tong_cham_cong = self.env['cham_cong'].search_count([])
        tong_bang_cong = self.env['bang_cong_thang'].search_count([])
        tong_canh_bao = self.env['canh_bao_cham_cong'].search_count([
            ('da_xu_ly', '=', False)
        ])
        tong_phieu_luong = self.env['tinh_luong'].search_count([])
        tong_luong_cho_duyet = self.env['tinh_luong'].search_count([
            ('trang_thai', '=', 'cho_duyet')
        ])

        noi_dung = (
            'TỔNG QUAN HỆ THỐNG ODOO\n\n'
            f'- Tổng số nhân viên: {tong_nhan_vien}\n'
            f'- Tổng số phòng ban: {tong_phong_ban}\n'
            f'- Tổng số chức vụ: {tong_chuc_vu}\n'
            f'- Tổng số bản ghi chấm công: {tong_cham_cong}\n'
            f'- Tổng số bảng công tháng: {tong_bang_cong}\n'
            f'- Cảnh báo chấm công chưa xử lý: {tong_canh_bao}\n'
            f'- Tổng số phiếu lương: {tong_phieu_luong}\n'
            f'- Phiếu lương chờ phê duyệt: {tong_luong_cho_duyet}\n'
        )

        thong_bao = self.env['lich_su_thong_bao_telegram'].create({
            'tieu_de': 'Tổng quan hệ thống Odoo',
            'noi_dung': noi_dung,
            'loai_thong_bao': 'tong_quan',
        })

        thong_bao.action_gui_telegram()
        return self._mo_lich_su_thong_bao()

    def action_tao_thong_bao_canh_bao_cham_cong(self):
        canh_baos = self.env['canh_bao_cham_cong'].search([
            ('da_xu_ly', '=', False)
        ])

        if not canh_baos:
            noi_dung = (
                'THÔNG BÁO CHẤM CÔNG\n'
                'Hiện không có cảnh báo chấm công chưa xử lý.'
            )
        else:
            ds = []
            for cb in canh_baos:
                ten_nv = f'{cb.nhan_vien_id.ho_dem or ""} {cb.nhan_vien_id.ten or ""}'.strip()
                ds.append(
                    f'- {ten_nv}: {cb.noi_dung} '
                    f'(Tháng {cb.thang}/{cb.nam})'
                )

            noi_dung = (
                'CẢNH BÁO CHẤM CÔNG CHƯA XỬ LÝ\n\n'
                + '\n'.join(ds)
            )

        thong_bao = self.env['lich_su_thong_bao_telegram'].create({
            'tieu_de': 'Cảnh báo chấm công',
            'noi_dung': noi_dung,
            'loai_thong_bao': 'canh_bao_cham_cong',
        })

        thong_bao.action_gui_telegram()
        return self._mo_lich_su_thong_bao()

    def action_tao_thong_bao_di_muon_vang_mat(self):
        cham_congs = self.env['cham_cong'].search([
            ('trang_thai', 'in', ['di_muon', 'vang'])
        ], order='ngay_cham_cong desc', limit=20)

        if not cham_congs:
            noi_dung = (
                'THÔNG BÁO CHẤM CÔNG\n'
                'Hiện không có bản ghi đi muộn hoặc vắng mặt.'
            )
        else:
            ds = []
            for cc in cham_congs:
                ten_nv = f'{cc.nhan_vien_id.ho_dem or ""} {cc.nhan_vien_id.ten or ""}'.strip()
                trang_thai = dict(cc._fields['trang_thai'].selection).get(cc.trang_thai)
                ds.append(
                    f'- {ten_nv}: {trang_thai}, ngày {cc.ngay_cham_cong}'
                )

            noi_dung = (
                'DANH SÁCH ĐI MUỘN / VẮNG MẶT GẦN NHẤT\n\n'
                + '\n'.join(ds)
            )

        thong_bao = self.env['lich_su_thong_bao_telegram'].create({
            'tieu_de': 'Danh sách đi muộn/vắng mặt',
            'noi_dung': noi_dung,
            'loai_thong_bao': 'canh_bao_cham_cong',
        })

        thong_bao.action_gui_telegram()
        return self._mo_lich_su_thong_bao()

    def action_tao_thong_bao_luong_cho_duyet(self):
        phieu_luongs = self.env['tinh_luong'].search([
            ('trang_thai', '=', 'cho_duyet')
        ])

        if not phieu_luongs:
            noi_dung = (
                'THÔNG BÁO TÍNH LƯƠNG\n'
                'Hiện không có phiếu lương nào đang chờ phê duyệt.'
            )
        else:
            ds = []
            for pl in phieu_luongs:
                ten_nv = f'{pl.nhan_vien_id.ho_dem or ""} {pl.nhan_vien_id.ten or ""}'.strip()
                ds.append(
                    f'- {ten_nv}: Tháng {pl.thang}/{pl.nam}, '
                    f'Thực lĩnh {pl.thuc_linh:,.0f} VNĐ'
                )

            noi_dung = (
                'PHIẾU LƯƠNG CHỜ PHÊ DUYỆT\n\n'
                + '\n'.join(ds)
            )

        thong_bao = self.env['lich_su_thong_bao_telegram'].create({
            'tieu_de': 'Phiếu lương chờ phê duyệt',
            'noi_dung': noi_dung,
            'loai_thong_bao': 'luong_cho_duyet',
        })

        thong_bao.action_gui_telegram()
        return self._mo_lich_su_thong_bao()

    def action_tao_thong_bao_tong_hop_luong(self):
        phieu_luongs = self.env['tinh_luong'].search([
            ('trang_thai', 'in', ['da_duyet', 'da_tra', 'cho_duyet'])
        ], order='nam desc, thang desc', limit=20)

        if not phieu_luongs:
            noi_dung = (
                'THÔNG BÁO TÍNH LƯƠNG\n'
                'Hiện chưa có phiếu lương để tổng hợp.'
            )
        else:
            tong_thuc_linh = sum(phieu_luongs.mapped('thuc_linh'))
            tong_bao_hiem = sum(phieu_luongs.mapped('tien_bao_hiem'))
            tong_lam_them = sum(phieu_luongs.mapped('tien_lam_them'))

            ds = []
            for pl in phieu_luongs[:10]:
                ten_nv = f'{pl.nhan_vien_id.ho_dem or ""} {pl.nhan_vien_id.ten or ""}'.strip()
                ds.append(
                    f'- {ten_nv}: tháng {pl.thang}/{pl.nam}, '
                    f'thực lĩnh {pl.thuc_linh:,.0f} VNĐ'
                )

            noi_dung = (
                'TỔNG HỢP LƯƠNG GẦN NHẤT\n\n'
                f'- Số phiếu lương: {len(phieu_luongs)}\n'
                f'- Tổng thực lĩnh: {tong_thuc_linh:,.0f} VNĐ\n'
                f'- Tổng bảo hiểm: {tong_bao_hiem:,.0f} VNĐ\n'
                f'- Tổng tiền làm thêm: {tong_lam_them:,.0f} VNĐ\n\n'
                'Chi tiết một số phiếu lương:\n'
                + '\n'.join(ds)
            )

        thong_bao = self.env['lich_su_thong_bao_telegram'].create({
            'tieu_de': 'Tổng hợp lương',
            'noi_dung': noi_dung,
            'loai_thong_bao': 'luong_cho_duyet',
        })

        thong_bao.action_gui_telegram()
        return self._mo_lich_su_thong_bao()