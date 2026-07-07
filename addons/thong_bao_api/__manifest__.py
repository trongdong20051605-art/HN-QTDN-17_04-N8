{
    'name': 'Thông báo Telegram API',
    'version': '1.0',
    'summary': 'Gửi thông báo chấm công và tính lương qua Telegram API',
    'category': 'Tools',
    'author': 'Student',
    'depends': ['base', 'web', 'nhan_su', 'cham_cong', 'tinh_luong'],
    'data': [
        'security/ir.model.access.csv',
        'views/thong_bao_api.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'thong_bao_api/static/src/css/custom_theme.css',
        ],
    },
    'installable': True,
    'application': True,
}