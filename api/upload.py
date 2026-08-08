import os
from fastapi import Request
import shutil
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from core.security import verify_token
from fastapi.responses import FileResponse, StreamingResponse
import mimetypes

router = APIRouter(prefix="/api/admin", tags=["Admin Upload"])

# Thiết lập đường dẫn động linh hoạt, tự nhận diện thư mục gốc
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUDIO_WORKSPACE = os.path.join(BASE_DIR, "audio_workspace", "music")
IMAGES_WORKSPACE = os.path.join(BASE_DIR, "images_workspace")

def get_file_extension(filename: str):
    return os.path.splitext(filename)[1]

# =========================================================
# 🔓 API TRỰC TIẾP TRẢ FILE: TÍCH HỢP STREAMING VIDEO CHUẨN
# =========================================================
@router.get("/preview/{folder_type}/{name}/{filename}")
async def direct_preview_media(request: Request, folder_type: str, name: str, filename: str):
    """
    API nội bộ chuyên để Stream Media. 
    Hỗ trợ phát ngắt quãng (Chunked Streaming) cho Video MP4.
    """
    if folder_type == "music":
        path = os.path.join(AUDIO_WORKSPACE, name, filename)
    elif folder_type == "image":
        path = os.path.join(IMAGES_WORKSPACE, name, filename)
    else:
        raise HTTPException(status_code=400, detail="Loại thư mục không hợp lệ")
        
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Bó tay, file không tồn tại trên ổ cứng!")

    # Đoán chuẩn định dạng file (MIME type)
    content_type, _ = mimetypes.guess_type(path)
    content_type = content_type or "application/octet-stream"

    # 🚀 TÍNH NĂNG PRO: Xử lý truyền phát Video MP4 theo từng đoạn (Range Requests)
    if filename.endswith(".mp4"):
        file_size = os.path.getsize(path)
        range_header = request.headers.get("Range")

        # Nếu trình duyệt yêu cầu tải từng khúc (Range)
        if range_header:
            byte_range = range_header.replace("bytes=", "").split("-")
            start = int(byte_range[0])
            end = int(byte_range[1]) if len(byte_range) > 1 and byte_range[1] else file_size - 1

            chunk_size = (end - start) + 1

            def file_iterator(file_path, start_byte, chunk_size):
                with open(file_path, "rb") as f:
                    f.seek(start_byte)
                    bytes_read = 0
                    while bytes_read < chunk_size:
                        # Đọc mỗi lần 64KB để không làm nghẽn RAM server
                        chunk = f.read(min(65536, chunk_size - bytes_read))
                        if not chunk:
                            break
                        bytes_read += len(chunk)
                        yield chunk

            headers = {
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Accept-Ranges": "bytes",
                "Content-Length": str(chunk_size),
                "Content-Type": content_type,
            }
            # Trả về mã 206 (Partial Content) cho trình duyệt biết
            return StreamingResponse(file_iterator(path, start, chunk_size), headers=headers, status_code=206)

    # Nếu là file Ảnh hoặc Audio nhẹ, dùng FileResponse bình thường để tối ưu tài nguyên
    return FileResponse(path, media_type=content_type)


# =========================================================
# API CHECK THƯ MỤC (Cập nhật đường dẫn URL mới)
# =========================================================
@router.get("/check-folder", dependencies=[Depends(verify_token)])
async def check_folder_exists(
    folder_type: str = Query(...), 
    name: str = Query(...)
):
    file_status = {}
    
    if folder_type == "music":
        target_dir = os.path.join(AUDIO_WORKSPACE, name)
        exists = os.path.exists(target_dir) and os.path.isdir(target_dir)
        
        if exists:
            def check_file(ext, suffix=""):
                file_name = f"{name}{suffix}{ext}"
                path = os.path.join(target_dir, file_name)
                if os.path.exists(path):
                    # 👉 SỬ DỤNG API TRỰC TIẾP VỪA TẠO Ở TRÊN
                    return {"exists": True, "url": f"/api/admin/preview/music/{name}/{file_name}"}
                return {"exists": False}
            
            file_status["audio"] = check_file(".mp3")
            file_status["beat"] = check_file(".mp3", "_beat")
            file_status["video"] = check_file(".mp4")
            file_status["lyric"] = check_file(".lrc")
            
            cover_res = {"exists": False}
            for ext in [".jpg", ".png", ".jpeg", ".webp"]:
                res = check_file(ext)
                if res["exists"]:
                    cover_res = res
                    break
            file_status["cover"] = cover_res
            
    elif folder_type == "image":
        target_dir = os.path.join(IMAGES_WORKSPACE, name)
        exists = os.path.exists(target_dir) and os.path.isdir(target_dir)
    else:
        raise HTTPException(status_code=400, detail="Loại thư mục không hợp lệ")
    
    return {
        "status": "success", 
        "exists": exists, 
        "name": name, 
        "files": file_status
    }



# ---------------------------------------------------------
# API 2: Upload Nhạc (Trọn bộ 5 file)
# ---------------------------------------------------------
@router.post("/upload-music", dependencies=[Depends(verify_token)])
async def upload_music(
    base_name: str = Form(...),
    audio: Optional[UploadFile] = File(None),
    beat: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
    cover: Optional[UploadFile] = File(None),
    lyric: Optional[UploadFile] = File(None)
):
    """Xử lý tải lên 5 file nhạc và tự động đổi tên theo base_name"""
    
    target_dir = os.path.join(AUDIO_WORKSPACE, base_name)
    os.makedirs(target_dir, exist_ok=True) # Tự tạo nếu chưa có, cho phép nếu đã có
    
    saved_files = []

    # Định nghĩa quy tắc tự động đổi tên
    file_mappings = {
        "audio": (audio, f"{base_name}"),           
        "beat": (beat, f"{base_name}_beat"),        
        "video": (video, f"{base_name}"),           
        "cover": (cover, f"{base_name}"),           
        "lyric": (lyric, f"{base_name}")            
    }

    for key, (file_obj, new_name_without_ext) in file_mappings.items():
        if file_obj:
            ext = get_file_extension(file_obj.filename)
            final_filename = f"{new_name_without_ext}{ext}"
            file_path = os.path.join(target_dir, final_filename)
            
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file_obj.file, buffer)
            saved_files.append(final_filename)

    if not saved_files:
        raise HTTPException(status_code=400, detail="Không có file nào được tải lên!")

    return {"status": "success", "message": f"Đã lưu/ghi đè thành công {len(saved_files)} file vào thư mục '{base_name}'"}


# ---------------------------------------------------------
# API 3: Upload Ảnh (Hàng loạt & Tự động tăng ID)
# ---------------------------------------------------------
@router.post("/upload-images", dependencies=[Depends(verify_token)])
async def upload_images(
    folder_name: str = Form(...),
    images: List[UploadFile] = File(...)
):
    """Xử lý tải ảnh hàng loạt, tự động đếm và tăng ID nối tiếp"""
    
    target_dir = os.path.join(IMAGES_WORKSPACE, folder_name)
    os.makedirs(target_dir, exist_ok=True)
    
    # Đếm số file ảnh đang có sẵn trong thư mục để cấp ID tiếp theo (Cộng dồn)
    existing_files = len([name for name in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, name))])
    current_id = existing_files + 1
    
    saved_count = 0
    for img in images:
        ext = get_file_extension(img.filename)
        
        # Đặt tên file logic
        if len(images) == 1 and existing_files == 0:
            final_name = f"{folder_name}{ext}"
        else:
            final_name = f"{folder_name}_images_{current_id}{ext}"
            
        file_path = os.path.join(target_dir, final_name)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(img.file, buffer)
            
        current_id += 1
        saved_count += 1
        
    return {"status": "success", "message": f"Đã tải lên và đổi tên {saved_count} ảnh vào thư mục '{folder_name}'"}
