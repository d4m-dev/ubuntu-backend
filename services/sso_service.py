# -*- coding: utf-8 -*-
# Tên file: ubuntu-backend/services/sso_service.py
import jwt
import random
import string
from fastapi import HTTPException, Header
from core.security import verify_password, create_access_token, get_password_hash, ADMIN_USERNAME
from core.database import db_executor, db_inserter, db_updater
from services.email_service import send_otp_email
from schemas.auth_schemas import LoginRequest, SSORegisterRequest, SSOVerifyOTP

# ==========================================
# 🛡️ LÁ CHẮN RADAR XÁC THỰC
# ==========================================
def get_current_user_id(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập lại.")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("id"), payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Token hết hạn hoặc lỗi.")

def verify_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập lại.")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        role = payload.get("role")
        if role != 1 and role != "admin":
            raise HTTPException(status_code=403, detail="CẢNH BÁO: Không đủ thẩm quyền! Chỉ Tư Lệnh mới được cấp phép truy cập.")
        return payload.get("id"), payload.get("sub")
    except Exception:
        raise HTTPException(status_code=401, detail="Token hết hạn hoặc lỗi.")

# ==========================================
# 🔑 NGHIỆP VỤ SSO & AUTHENTICATION
# ==========================================
def process_admin_login(req: LoginRequest):
    if req.username != ADMIN_USERNAME or not verify_password(req.password):
        raise HTTPException(status_code=401, detail="❌ Sai thông tin đăng nhập!")
    return create_access_token(data={"sub": req.username, "role": "admin"})

def process_sso_register(data: SSORegisterRequest):
    existing = db_executor.select_as_list_dict("SELECT id FROM users WHERE username=%s OR email=%s", (data.username, data.email))
    if existing: raise HTTPException(status_code=400, detail="Tài khoản hoặc Email đã tồn tại!")
    
    otp_code = ''.join(random.choices(string.digits, k=6))
    if not send_otp_email(data.email, otp_code, data.username): 
        raise HTTPException(status_code=500, detail="Lỗi gửi mail hệ thống.")
    
    hashed_password = get_password_hash(data.password)
    sql = "INSERT INTO users (username, password_hash, full_name, email, is_verified, otp_code) VALUES (%s, %s, %s, %s, FALSE, %s)"
    db_inserter.insert(sql, (data.username, hashed_password, data.full_name, data.email, otp_code))

def process_sso_verify(data: SSOVerifyOTP):
    users = db_executor.select_as_list_dict("SELECT id, otp_code FROM users WHERE email=%s AND is_verified=FALSE", (data.email,))
    if not users or users[0]['otp_code'] != data.otp: 
        raise HTTPException(status_code=400, detail="OTP không hợp lệ hoặc sai email!")
    db_updater.update("UPDATE users SET is_verified=TRUE, otp_code=NULL WHERE id=%s", (users[0]['id'],))

def process_sso_login(data: LoginRequest):
    users = db_executor.select_as_list_dict(
        "SELECT id, username, password_hash, is_verified, full_name, role, active FROM users WHERE (username=%s OR email=%s)", 
        (data.username, data.username)
    )
    if not users or not verify_password(data.password, users[0]['password_hash']): 
        raise HTTPException(status_code=401, detail="Sai thông tin đăng nhập!")
    user = users[0]
    if not user['is_verified']: 
        raise HTTPException(status_code=403, detail="Tài khoản chưa được xác thực Email!")
        
    return create_access_token(
        data={
            "sub": user['username'], "id": user['id'],
            "full_name": user['full_name'] or user['username'],
            "role": user['role'], "active": user['active']
        }
    )