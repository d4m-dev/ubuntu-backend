import jwt
import bcrypt  # 🚀 DÙNG TRỰC TIẾP LÕI BCRYPT, SA THẢI PASSLIB
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

# ==========================================
# ⚙️ CẤU HÌNH ADMIN & TOKEN
# ==========================================
ADMIN_USERNAME = getattr(settings, "ADMIN_USERNAME", "admin")
_ADMIN_PASSWORD_RAW = getattr(settings, "ADMIN_PASSWORD", "admin123")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security_scheme = HTTPBearer()

# ==========================================
# 🔐 HỆ THỐNG MÃ HÓA (Chuẩn Bcrypt Trực Tiếp)
# ==========================================
def get_password_hash(password: str) -> str:
    """Băm mật khẩu người dùng trước khi lưu vào DB."""
    # Đổi chuỗi text thành byte trước khi băm
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # Trả về dạng string bình thường để dễ dàng lưu vào MariaDB/SQLite
    return hashed_password.decode('utf-8')

# Khởi tạo mã băm cho Admin ngay khi hệ thống vừa thức giấc
_ADMIN_PASSWORD_HASH = get_password_hash(_ADMIN_PASSWORD_RAW)

def verify_password(plain_password: str, hashed_password: str = None) -> bool:
    """
    Kiểm tra mật khẩu đa năng:
    - Nếu có hashed_password: So sánh cho User SSO.
    - Nếu không có hashed_password: Mặc định so sánh cho Admin.
    """
    password_byte_enc = plain_password.encode('utf-8')

    # Nếu không truyền mã băm vào, tự hiểu là đang test tài khoản Admin
    if hashed_password is None:
        hashed_password = _ADMIN_PASSWORD_HASH

    # Đảm bảo mã băm trong Database được chuyển về dạng byte để so sánh
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    try:
        return bcrypt.checkpw(password_byte_enc, hashed_password)
    except ValueError:
        # Chống sập web nếu mã băm trong Database bị ai đó sửa bậy bạ
        return False

# ==========================================
# 🎫 HỆ THỐNG CẤP PHÁT & XÁC THỰC TOKEN
# ==========================================
def create_access_token(data: dict):
    """Đúc thẻ bài JWT"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    """Giải mã và kiểm tra tính hợp lệ của Token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="⚠️ Phiên đăng nhập đã hết hạn!")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="❌ Token không hợp lệ hoặc đã bị giả mạo!")