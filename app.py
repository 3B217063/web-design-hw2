"""
1132 Web 程式設計 - 第 2 次作業
簡易會員系統（Flask + JSON 檔案儲存）
"""

import json
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

USERS_FILE = "users.json"


# ── JSON 操作函式 ──────────────────────────────────────────────


def init_json_file(file_path: str) -> None:
    """若 JSON 檔案不存在或格式錯誤，建立含預設管理員的初始檔案。"""
    default_data = {
        "users": [
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin123",
                "phone": "0912345678",
                "birthdate": "1990-01-01",
            }
        ]
    }
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)
        return
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "users" not in data:
            raise ValueError
    except (json.JSONDecodeError, ValueError):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default_data, f, ensure_ascii=False, indent=2)


def read_users(file_path: str) -> dict:
    """從 JSON 檔案讀取所有使用者資料，回傳 dict。"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"users": []}


def save_users(file_path: str, data: dict) -> bool:
    """將使用者資料寫入 JSON 檔案，成功回傳 True，失敗回傳 False。"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except OSError:
        return False


# ── 驗證函式 ──────────────────────────────────────────────────


def validate_register(form_data: dict, users: list) -> dict:
    """
    驗證註冊表單資料。
    回傳 {"success": True, "data": {...}} 或 {"success": False, "error": "訊息"}
    """
    username = form_data.get("username", "").strip()
    email = form_data.get("email", "").strip()
    password = form_data.get("password", "").strip()
    phone = form_data.get("phone", "").strip()
    birthdate = form_data.get("birthdate", "").strip()

    if not username:
        return {"success": False, "error": "帳號為必填欄位"}
    if not email:
        return {"success": False, "error": "Email 為必填欄位"}
    if not password:
        return {"success": False, "error": "密碼為必填欄位"}
    if not birthdate:
        return {"success": False, "error": "出生日期為必填欄位"}

    if "@" not in email or "." not in email:
        return {"success": False, "error": "Email 格式不正確"}

    if len(password) < 6 or len(password) > 16:
        return {"success": False, "error": "密碼須為 6-16 個字元"}

    if phone:
        if len(phone) != 10 or not phone.startswith("09") or not phone.isdigit():
            return {"success": False, "error": "電話格式不正確（須為 09 開頭的 10 位數字）"}

    for user in users:
        if user["username"] == username:
            return {"success": False, "error": "帳號已被使用"}
        if user["email"] == email:
            return {"success": False, "error": "Email 已被使用"}

    return {
        "success": True,
        "data": {
            "username": username,
            "email": email,
            "password": password,
            "phone": phone,
            "birthdate": birthdate,
        },
    }


def verify_login(email: str, password: str, users: list) -> dict:
    """
    驗證登入憑證。
    回傳 {"success": True, "data": {...}} 或 {"success": False, "error": "訊息"}
    """
    for user in users:
        if user["email"] == email and user["password"] == password:
            return {"success": True, "data": user}
    return {"success": False, "error": "Email 或密碼錯誤"}


# ── Jinja2 自訂 Filter ────────────────────────────────────────


@app.template_filter("mask_phone")
def mask_phone(phone: str) -> str:
    """將電話中段遮罩：0912345678 → 0912****78"""
    if not phone:
        return "-"
    return phone[:4] + "****" + phone[-2:]


@app.template_filter("format_tw_date")
def format_tw_date(date_str: str) -> str:
    """將西元日期轉換為民國年：1990-01-01 → 民國79年01月01日"""
    if not date_str:
        return "-"
    try:
        year, month, day = date_str.split("-")
        roc_year = int(year) - 1911
        return f"民國{roc_year}年{int(month):02d}月{int(day):02d}日"
    except (ValueError, AttributeError):
        return date_str


# ── 初始化（module level，相容 flask run） ──────────────────────

init_json_file(USERS_FILE)


# ── 路由 ──────────────────────────────────────────────────────


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = read_users(USERS_FILE)
        users = data.get("users", [])
        result = validate_register(request.form.to_dict(), users)
        if result["success"]:
            users.append(result["data"])
            data["users"] = users
            save_users(USERS_FILE, data)
            return redirect(url_for("login"))
        return redirect(url_for("error", message=result["error"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        data = read_users(USERS_FILE)
        users = data.get("users", [])
        result = verify_login(email, password, users)
        if result["success"]:
            return redirect(url_for("welcome", username=result["data"]["username"]))
        return redirect(url_for("error", message=result["error"]))
    return render_template("login.html")


@app.route("/welcome/<username>")
def welcome(username):
    data = read_users(USERS_FILE)
    users = data.get("users", [])
    user = next((u for u in users if u["username"] == username), None)
    if user is None:
        return redirect(url_for("error", message="使用者不存在"))
    return render_template("welcome.html", user=user)


@app.route("/users")
def users():
    data = read_users(USERS_FILE)
    user_list = data.get("users", [])
    return render_template("users.html", users=user_list)


@app.route("/error")
def error():
    message = request.args.get("message", "發生未知錯誤")
    return render_template("error.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)
