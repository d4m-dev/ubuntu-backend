# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import jwt
from core.config import settings
from core.database import db_executor, db_inserter, db_deleter

router = APIRouter(prefix="/api/social", tags=["Social Hub"])

# ==========================================
# 🛡️ BỘ LỌC BẢO MẬT & ĐỊNH DANH TOKEN SSO THÔNG MINH
# ==========================================
def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu thẻ định danh (Token)")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        if payload.get("active") != 1:
            raise HTTPException(status_code=403, detail="Tài khoản chưa được kích hoạt")
            
        # 🚀 FIX LỖI THIẾU ID: Nếu Token không có user_id, tự động lấy từ Database thông qua username (sub)
        user_id = payload.get("user_id") or payload.get("id")
        if not user_id:
            username = payload.get("sub")
            if not username:
                raise HTTPException(status_code=401, detail="Token không hợp lệ (Không có định danh)")
                
            user_db = db_executor.select_as_list_dict("SELECT id FROM users WHERE username=%s", (username,))
            if user_db:
                payload["user_id"] = user_db[0]["id"]
            else:
                raise HTTPException(status_code=401, detail="Không tìm thấy tài khoản trong Database")
        else:
            payload["user_id"] = user_id
            
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Thẻ định danh đã hết hạn")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Thẻ định danh không hợp lệ")


# ==========================================
# 📦 SCHEMAS (ĐỊNH DẠNG DỮ LIỆU)
# ==========================================
class PostCreate(BaseModel):
    content: str
    attached_media: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None


# ==========================================
# 🚀 CÁC ĐƯỜNG DẪN API (ENDPOINTS)
# ==========================================
@router.get("/feed")
def get_feed(current_user: dict = Depends(get_current_user)):
    """Lấy danh sách bảng tin an toàn chống Crash 100%"""
    try:
        # 🚀 FIX LỖI TÊN: Dùng COALESCE để đảm bảo không bao giờ bị Null (Ưu tiên fullname -> full_name -> username)
        sql = """
            SELECT 
                p.id as post_id, p.content, p.created_at, p.attached_media, p.media_type,
                u.id as user_id, u.username, 
                COALESCE(u.fullname, u.full_name, u.username) as fullname, 
                u.avatar_url, u.role,
                m.file_url 
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN media m ON p.id = m.post_id
            ORDER BY p.created_at DESC 
            LIMIT 50
        """
        posts = db_executor.select_as_list_dict(sql)
        
        formatted_posts = []
        for post in posts:
            # 🚀 FIX LỖI NGÀY THÁNG: Kiểm tra kiểu dữ liệu kỹ càng trước khi ép chuỗi (isoformat)
            dt = post.get("created_at")
            dt_str = dt.isoformat() if hasattr(dt, "isoformat") else str(dt) if dt else None
                
            formatted_posts.append({
                "post_id": post["post_id"],
                "user_id": post["user_id"],
                "username": post["username"],
                "fullname": post["fullname"],
                "avatar_url": post["avatar_url"],
                "role": post["role"],
                "content": post["content"],
                "created_at": dt_str,
                "attached_media": post["attached_media"],
                "media_type": post["media_type"],
                "stream_links": {"vocal_url": post["file_url"], "video_url": post["file_url"], "cover_url": ""} if post.get("file_url") else None
            })
            
        return {"status": "success", "data": formatted_posts}
    except Exception as e:
        return {"status": "error", "message": f"Lỗi nội bộ Database: {str(e)}", "data": []}


@router.post("/posts")
def create_post(post: PostCreate, current_user: dict = Depends(get_current_user)):
    """Đăng bài mới - Khóa cứng ID của người đăng từ Token"""
    user_id = current_user.get("user_id")
    
    # Lưu bài viết chính
    sql_post = "INSERT INTO posts (user_id, content, attached_media, media_type) VALUES (%s, %s, %s, %s)"
    post_id = db_inserter.insert(sql_post, (user_id, post.content, post.attached_media, post.media_type))
    
    if not post_id:
        raise HTTPException(status_code=500, detail="Lỗi khi lưu bài viết vào Database")

    # Nếu có đính kèm nhạc/video, lưu vào bảng media
    if post.media_url:
        sql_media = "INSERT INTO media (post_id, file_url, media_type) VALUES (%s, %s, %s)"
        db_inserter.insert(sql_media, (post_id, post.media_url, post.media_type or 'image'))

    return {"status": "success", "message": "Đăng bài thành công", "post_id": post_id}


@router.delete("/posts/{post_id}")
def delete_post(post_id: int, current_user: dict = Depends(get_current_user)):
    """Xóa bài viết - Cấp quyền tối cao cho Admin"""
    user_id = current_user.get("user_id")
    role = current_user.get("role", 0)

    sql_check = "SELECT user_id FROM posts WHERE id = %s"
    post_data = db_executor.select_as_list_dict(sql_check, (post_id,))
    
    if not post_data:
        raise HTTPException(status_code=404, detail="Bài viết không tồn tại")
        
    post_owner_id = post_data[0]["user_id"]

    # Rào chắn: Chỉ có chủ sở hữu hoặc Admin (role = 1) mới được xóa
    if post_owner_id != user_id and int(role) != 1:
        raise HTTPException(status_code=403, detail="Sếp không có quyền xóa bài của người khác!")

    sql_delete = "DELETE FROM posts WHERE id = %s"
    affected = db_deleter.delete(sql_delete, (post_id,))
    
    if affected > 0:
        return {"status": "success", "message": "Đã cho bay màu vĩnh viễn"}
    else:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi xóa")