# -*- coding: utf-8 -*-
"""
试客商城 · 数据访问层
基于 SQLite 的轻量 DAO 封装，无第三方 ORM 依赖。
"""
import os
import sqlite3
from datetime import datetime

from flask import current_app, g

DB_NAME = "testbuy.db"


def get_db():
    """按请求获取数据库连接（Flask g 对象缓存）。"""
    if "db" not in g:
        db_path = os.path.join(current_app.instance_path, DB_NAME)
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """建表：用户 / 商品 / 购物车 / 订单 / 订单明细。"""
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email         TEXT,
            is_admin      INTEGER DEFAULT 0,
            created_at    TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS products (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            category    TEXT NOT NULL DEFAULT '默认',
            price       REAL NOT NULL,
            stock       INTEGER NOT NULL DEFAULT 0,
            description TEXT DEFAULT '',
            image_url   TEXT DEFAULT '',
            is_on_sale  INTEGER DEFAULT 1,
            created_at  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS cart_items (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity   INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id, product_id),
            FOREIGN KEY (user_id)    REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_no     TEXT UNIQUE NOT NULL,
            user_id      INTEGER NOT NULL,
            receiver     TEXT NOT NULL,
            phone        TEXT NOT NULL,
            address      TEXT NOT NULL,
            total_amount REAL NOT NULL,
            status       TEXT NOT NULL DEFAULT '待付款',
            created_at   TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id     INTEGER NOT NULL,
            product_id   INTEGER,
            product_name TEXT NOT NULL,
            price        REAL NOT NULL,
            quantity     INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
        """
    )
    db.commit()


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------- 用户 ----------------
def create_user(username, password_hash, email=None, is_admin=0):
    db = get_db()
    cur = db.execute(
        "INSERT INTO users (username, password_hash, email, is_admin, created_at)"
        " VALUES (?, ?, ?, ?, ?)",
        (username, password_hash, email, is_admin, now_str()),
    )
    db.commit()
    return cur.lastrowid


def get_user_by_name(username):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def get_user_by_id(uid):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


# ---------------- 商品 ----------------
def list_products(keyword="", category="", page=1, per_page=12):
    db = get_db()
    sql = "SELECT * FROM products WHERE is_on_sale = 1"
    args = []
    if keyword:
        sql += " AND name LIKE ?"
        args.append(f"%{keyword}%")
    if category:
        sql += " AND category = ?"
        args.append(category)
    total = db.execute(f"SELECT COUNT(*) AS c FROM ({sql})", args).fetchone()["c"]
    sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
    args += [per_page, (page - 1) * per_page]
    rows = db.execute(sql, args).fetchall()
    return rows, total


def list_all_products():
    db = get_db()
    return db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()


def get_product(pid):
    db = get_db()
    return db.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()


def list_categories():
    db = get_db()
    return [r["category"] for r in db.execute(
        "SELECT DISTINCT category FROM products WHERE is_on_sale = 1").fetchall()]


def add_product(name, category, price, stock, description="", image_url=""):
    db = get_db()
    cur = db.execute(
        "INSERT INTO products (name, category, price, stock, description, image_url, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, category, float(price), int(stock), description, image_url, now_str()),
    )
    db.commit()
    return cur.lastrowid


def update_product(pid, name, category, price, stock, description="", image_url="", is_on_sale=1):
    db = get_db()
    db.execute(
        "UPDATE products SET name=?, category=?, price=?, stock=?, description=?, image_url=?, is_on_sale=?"
        " WHERE id=?",
        (name, category, float(price), int(stock), description, image_url, int(is_on_sale), pid),
    )
    db.commit()


def delete_product(pid):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (pid,))
    db.commit()


# ---------------- 购物车 ----------------
def add_to_cart(user_id, product_id, quantity=1):
    db = get_db()
    row = db.execute(
        "SELECT * FROM cart_items WHERE user_id=? AND product_id=?",
        (user_id, product_id)).fetchone()
    if row:
        db.execute(
            "UPDATE cart_items SET quantity = quantity + ? WHERE id = ?",
            (quantity, row["id"]))
    else:
        db.execute(
            "INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)",
            (user_id, product_id, quantity))
    db.commit()


def list_cart(user_id):
    db = get_db()
    rows = db.execute(
        """SELECT c.id AS cid, c.product_id, c.quantity, p.name, p.price, p.stock, p.image_url
           FROM cart_items c JOIN products p ON c.product_id = p.id
           WHERE c.user_id = ? ORDER BY c.id""",
        (user_id,)).fetchall()
    return rows, sum(r["price"] * r["quantity"] for r in rows)


def update_cart_qty(cid, quantity):
    db = get_db()
    db.execute("UPDATE cart_items SET quantity = ? WHERE id = ?", (max(int(quantity), 1), cid))
    db.commit()


def remove_cart_item(cid):
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE id = ?", (cid,))
    db.commit()


def clear_cart(user_id):
    db = get_db()
    db.execute("DELETE FROM cart_items WHERE user_id = ?", (user_id,))
    db.commit()


# ---------------- 订单 ----------------
def create_order(user_id, receiver, phone, address, items):
    """items: [(product_id, name, price, qty), ...] 创建订单并扣减库存。"""
    db = get_db()
    total = round(sum(p * q for _, _, p, q in items), 2)
    order_no = f"TB{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}"
    cur = db.execute(
        "INSERT INTO orders (order_no, user_id, receiver, phone, address, total_amount, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?)",
        (order_no, user_id, receiver, phone, address, total, now_str()))
    order_id = cur.lastrowid
    for pid, name, price, qty in items:
        db.execute(
            "INSERT INTO order_items (order_id, product_id, product_name, price, quantity)"
            " VALUES (?, ?, ?, ?, ?)",
            (order_id, pid, name, price, qty))
        db.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))
    db.commit()
    return order_id, order_no


def list_orders(user_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()


def list_all_orders():
    db = get_db()
    return db.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()


def get_order(order_id, user_id=None):
    db = get_db()
    if user_id:
        return db.execute(
            "SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id)).fetchone()
    return db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()


def get_order_items(order_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()


def update_order_status(order_id, status):
    db = get_db()
    db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    db.commit()
