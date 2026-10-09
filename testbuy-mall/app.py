# -*- coding: utf-8 -*-
"""
试客商城 TestBuy Mall · Flask 应用入口
被测电商系统：登录/注册、商品浏览与搜索、购物车、下单结算、订单管理、后台商品管理。
设计说明：所有关键交互元素均带 data-testid 属性，为 UI 自动化测试提供稳定定位标识。
"""
import os
import math

from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
from werkzeug.security import generate_password_hash, check_password_hash

import models

PER_PAGE = 12


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("TESTBUY_SECRET", "testbuy-mall-dev-secret")
    os.makedirs(app.instance_path, exist_ok=True)

    app.teardown_appcontext(models.close_db)

    # ---------------- 公共 ----------------
    @app.context_processor
    def inject_globals():
        return {"current_user": g.get("user")}

    @app.before_request
    def load_user():
        uid = session.get("user_id")
        g.user = models.get_user_by_id(uid) if uid else None

    def login_required(view):
        from functools import wraps

        @wraps(view)
        def wrapped(*args, **kwargs):
            if not g.get("user"):
                flash("请先登录", "warning")
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped

    def admin_required(view):
        from functools import wraps

        @wraps(view)
        def wrapped(*args, **kwargs):
            if not g.get("user") or not g.user["is_admin"]:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    # ---------------- 首页 / 商品 ----------------
    @app.route("/")
    def index():
        keyword = request.args.get("keyword", "").strip()
        category = request.args.get("category", "").strip()
        page = max(1, request.args.get("page", 1, type=int))
        products, total = models.list_products(keyword, category, page, PER_PAGE)
        pages = max(1, math.ceil(total / PER_PAGE))
        return render_template(
            "index.html", products=products, total=total, page=page, pages=pages,
            keyword=keyword, category=category,
            categories=models.list_categories())

    @app.route("/product/<int:pid>")
    def product_detail(pid):
        product = models.get_product(pid)
        if not product or not product["is_on_sale"]:
            abort(404)
        return render_template("product.html", product=product)

    # ---------------- 认证 ----------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            email = request.form.get("email", "").strip()
            if len(username) < 3 or len(password) < 6:
                flash("用户名至少 3 位，密码至少 6 位", "danger")
            elif models.get_user_by_name(username):
                flash("用户名已存在", "danger")
            else:
                models.create_user(username, generate_password_hash(password), email)
                flash("注册成功，请登录", "success")
                return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = models.get_user_by_name(username)
            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                flash(f"欢迎回来，{user['username']}", "success")
                nxt = request.args.get("next")
                return redirect(nxt if nxt and nxt.startswith("/") else url_for("index"))
            flash("用户名或密码错误", "danger")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        flash("已退出登录", "info")
        return redirect(url_for("index"))

    # ---------------- 购物车 ----------------
    @app.route("/cart")
    @login_required
    def cart():
        items, total = models.list_cart(g.user["id"])
        return render_template("cart.html", items=items, total=total)

    @app.route("/cart/add", methods=["POST"])
    @login_required
    def cart_add():
        pid = request.form.get("product_id", type=int)
        qty = request.form.get("quantity", 1, type=int)
        product = models.get_product(pid) if pid else None
        if not product or not product["is_on_sale"]:
            flash("商品不存在或已下架", "danger")
        else:
            models.add_to_cart(g.user["id"], pid, max(qty, 1))
            flash("已加入购物车", "success")
        return redirect(request.referrer or url_for("index"))

    @app.route("/cart/update", methods=["POST"])
    @login_required
    def cart_update():
        cid = request.form.get("cid", type=int)
        qty = request.form.get("quantity", 1, type=int)
        if cid:
            models.update_cart_qty(cid, qty)
        return redirect(url_for("cart"))

    @app.route("/cart/remove/<int:cid>", methods=["POST"])
    @login_required
    def cart_remove(cid):
        models.remove_cart_item(cid)
        return redirect(url_for("cart"))

    # ---------------- 结算 / 订单 ----------------
    @app.route("/checkout", methods=["GET", "POST"])
    @login_required
    def checkout():
        items, total = models.list_cart(g.user["id"])
        if not items:
            flash("购物车为空", "warning")
            return redirect(url_for("cart"))
        if request.method == "POST":
            receiver = request.form.get("receiver", "").strip()
            phone = request.form.get("phone", "").strip()
            address = request.form.get("address", "").strip()
            if not (receiver and phone and address):
                flash("请完整填写收货信息", "danger")
                return render_template("checkout.html", items=items, total=total)
            order_items = [(it["product_id"], it["name"], it["price"], it["quantity"])
                           for it in items]
            try:
                order_id, order_no = models.create_order(
                    g.user["id"], receiver, phone, address, order_items)
            except Exception:
                flash("库存不足或下单失败", "danger")
                return render_template("checkout.html", items=items, total=total)
            models.clear_cart(g.user["id"])
            return redirect(url_for("order_success", order_id=order_id))
        return render_template("checkout.html", items=items, total=total)

    @app.route("/order/success/<int:order_id>")
    @login_required
    def order_success(order_id):
        order = models.get_order(order_id, g.user["id"])
        if not order:
            abort(404)
        return render_template("order_success.html", order=order)

    @app.route("/orders")
    @login_required
    def orders():
        return render_template("orders.html", orders=models.list_orders(g.user["id"]))

    @app.route("/order/<int:order_id>")
    @login_required
    def order_detail(order_id):
        order = models.get_order(order_id, g.user["id"])
        if not order:
            abort(404)
        return render_template("order_detail.html", order=order,
                               items=models.get_order_items(order_id))

    @app.route("/order/<int:order_id>/cancel", methods=["POST"])
    @login_required
    def order_cancel(order_id):
        order = models.get_order(order_id, g.user["id"])
        if order and order["status"] in ("待付款", "待发货"):
            models.update_order_status(order_id, "已取消")
            flash("订单已取消", "success")
        return redirect(url_for("order_detail", order_id=order_id))

    # ---------------- 后台管理 ----------------
    @app.route("/admin/products")
    @admin_required
    def admin_products():
        return render_template("admin/products.html",
                               products=models.list_all_products())

    @app.route("/admin/products/add", methods=["POST"])
    @admin_required
    def admin_product_add():
        models.add_product(
            request.form.get("name", "").strip(),
            request.form.get("category", "默认").strip(),
            request.form.get("price", 0),
            request.form.get("stock", 0),
            request.form.get("description", "").strip(),
            request.form.get("image_url", "").strip())
        flash("商品已添加", "success")
        return redirect(url_for("admin_products"))

    @app.route("/admin/products/<int:pid>/update", methods=["POST"])
    @admin_required
    def admin_product_update(pid):
        models.update_product(
            pid,
            request.form.get("name", "").strip(),
            request.form.get("category", "默认").strip(),
            request.form.get("price", 0),
            request.form.get("stock", 0),
            request.form.get("description", "").strip(),
            request.form.get("image_url", "").strip(),
            request.form.get("is_on_sale", "1"))
        flash("商品已更新", "success")
        return redirect(url_for("admin_products"))

    @app.route("/admin/products/<int:pid>/delete", methods=["POST"])
    @admin_required
    def admin_product_delete(pid):
        models.delete_product(pid)
        flash("商品已删除", "info")
        return redirect(url_for("admin_products"))

    @app.route("/admin/orders")
    @admin_required
    def admin_orders():
        return render_template("admin/orders.html", orders=models.list_all_orders())

    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="页面不存在"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("error.html", code=403, message="无权限访问"), 403

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
