# -*- coding: utf-8 -*-
# Tên file: ubuntu-backend/services/profile_service.py
import os
import shutil
import random
import string
from fastapi import HTTPException, UploadFile
from core.security import get_password_hash
from core.database import db_executor, db_updater
from services.email_service import send_otp_email
from schemas.auth_schemas import (
    UpdateProfileRequest, ChangeEmailRequest, VerifyChangeEmailRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)

ALLOWED_AVATAR_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

def get_user_profile(user_id: int):
    users = db_executor.select_as_list_dict(
        "SELECT id, username, full_name, email, phone, dob, address, avatar_url, role, active FROM users WHERE id=%s", (user_id,)
    )
    if not users: raise HTTPException(status_code=404, detail="Không tìm thấy người dùng.")
    user = users[0]
    if not user.get("avatar_url"): 
        user["avatar_url"] = f"https://ui-avatars.com/api/?name={user['username']}&background=random&color=fff"
    return user

def update_user_profile(user_id: int, data: UpdateProfileRequest):
    if data.cccd:
        dups = db_executor.select_as_list_dict("SELECT id FROM users WHERE cccd=%s AND id!=%s", (data.cccd, user_id))
        if dups: raise HTTPException(status_code=400, detail="❌ Số CCCD này đã được liên kết với một tài khoản khác!")
    sql = "UPDATE users SET full_name=%s, phone=%s, cccd=%s, dob=%s, address=%s WHERE id=%s"
    db_updater.update(sql, (data.full_name, data.phone, data.cccd, data.dob, data.address, user_id))

def upload_user_avatar(user_id: int, username: str, file: UploadFile):
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_AVATAR_EXTENSIONS or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Chỉ cho phép tải lên định dạng ảnh!")
        
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    avatar_dir = os.path.join(base_dir, "images_workspace", "avatar", username)
    os.makedirs(avatar_dir, exist_ok=True)
    filename = f"avatar_{username}_{random.randint(1000, 9999)}.{file_ext}"
    
    with open(os.path.join(avatar_dir, filename), "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
        
    avatar_url = f"/images_workspace/avatar/{username}/{filename}"
    db_updater.update("UPDATE users SET avatar_url=%s WHERE id=%s", (avatar_url, user_id))
    return avatar_url

def request_email_change(user_id: int, username: str, data: ChangeEmailRequest):
    if db_executor.select_as_list_dict("SELECT id FROM users WHERE email=%s", (data.new_email,)):
        raise HTTPException(status_code=400, detail="Email này đã được sử dụng bởi người khác!")
    otp_code = ''.join(random.choices(string.digits, k=6))
    if not send_otp_email(data.new_email, otp_code, username): 
        raise HTTPException(status_code=500, detail="Lỗi máy chủ khi gửi Email.")
    db_updater.update("UPDATE users SET otp_code=%s WHERE id=%s", (otp_code, user_id))

def verify_email_change(user_id: int, data: VerifyChangeEmailRequest):
    users = db_executor.select_as_list_dict("SELECT otp_code FROM users WHERE id=%s", (user_id,))
    if not users or not users[0]['otp_code'] or users[0]['otp_code'] != data.otp: 
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác.")
    db_updater.update("UPDATE users SET email=%s, otp_code=NULL WHERE id=%s", (data.new_email, user_id))

def process_forgot_password(data: ForgotPasswordRequest):
    users = db_executor.select_as_list_dict("SELECT id, username FROM users WHERE email=%s", (data.email,))
    if not users: raise HTTPException(status_code=404, detail="Email này chưa từng được đăng ký trong hệ thống!")
    user = users[0]
    otp_code = ''.join(random.choices(string.digits, k=6))
    if not send_otp_email(data.email, otp_code, user['username']): 
        raise HTTPException(status_code=500, detail="Lỗi trạm phát sóng Email.")
    db_updater.update("UPDATE users SET otp_code=%s WHERE id=%s", (otp_code, user['id']))

def process_reset_password(data: ResetPasswordRequest):
    users = db_executor.select_as_list_dict("SELECT id, otp_code FROM users WHERE email=%s", (data.email,))
    if not users or not users[0]['otp_code'] or users[0]['otp_code'] != data.otp: 
        raise HTTPException(status_code=400, detail="Mã OTP không chính xác hoặc đã hết hạn!")
    hashed_password = get_password_hash(data.new_password)
    db_updater.update("UPDATE users SET password_hash=%s, otp_code=NULL WHERE id=%s", (hashed_password, users[0]['id']))