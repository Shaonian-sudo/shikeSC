# -*- coding: utf-8 -*-
"""
试客商城 · 数据初始化脚本
用法：python seed.py
生成：管理员 admin/Admin@123、测试用户 buyer/Test@123、演示商品 16 件
"""
import os

from werkzeug.security import generate_password_hash

import models


def seed():
    from app import app
    os.makedirs("instance", exist_ok=True)
    with app.app_context():
        _seed_core()


def _seed_core():
    models.init_db()

    if not models.get_user_by_name("admin"):
        models.create_user("admin", generate_password_hash("Admin@123"),
                           "admin@testbuy.local", is_admin=1)
        print("[ok] 管理员已创建：admin / Admin@123")
    if not models.get_user_by_name("buyer"):
        models.create_user("buyer", generate_password_hash("Test@123"),
                           "buyer@testbuy.local")
        print("[ok] 测试用户已创建：buyer / Test@123")

    if not models.list_all_products():
        demo = [
            ("智能手表 Pro", "数码", 899.00, 50, "AMOLED 屏，心率血氧监测，续航 14 天"),
            ("无线降噪耳机", "数码", 499.00, 80, "40dB 主动降噪，蓝牙 5.3"),
            ("机械键盘 87 键", "数码", 329.00, 60, "RGB 背光，热插拔轴体"),
            ("便携蓝牙音箱", "数码", 199.00, 40, "IPX7 防水，12 小时续航"),
            ("纯棉基础T恤", "服饰", 79.00, 200, "100% 精梳棉，宽松版型"),
            ("修身牛仔裤", "服饰", 159.00, 120, "弹力面料，直筒剪裁"),
            ("轻量运动跑鞋", "服饰", 399.00, 90, "透气网面，缓震中底"),
            ("休闲帆布包", "服饰", 129.00, 100, "大容量，加厚帆布"),
            ("玻尿酸保湿面膜", "美妆", 99.00, 300, "30ml*10 片，深层补水"),
            ("氨基酸洁面乳", "美妆", 59.00, 250, "温和不刺激，敏感肌适用"),
            ("防晒霜 SPF50+", "美妆", 89.00, 180, "清爽不油腻，防水防汗"),
            ("淡香水 50ml", "美妆", 259.00, 70, "木质花香调，持香 8 小时"),
            ("不锈钢保温杯", "家居", 69.00, 150, "316 不锈钢，24 小时保温"),
            ("记忆棉护颈枕", "家居", 119.00, 110, "慢回弹，人体工学设计"),
            ("香薰加湿器", "家居", 149.00, 95, "静音运行，大雾量"),
            ("北欧风台灯", "家居", 109.00, 88, "三档调光，护眼无频闪"),
        ]
        for name, category, price, stock, desc in demo:
            models.add_product(name, category, price, stock, desc)
        print(f"[ok] 演示商品已创建：{len(demo)} 件")

    print("完成。启动服务：python app.py")


if __name__ == "__main__":
    seed()
