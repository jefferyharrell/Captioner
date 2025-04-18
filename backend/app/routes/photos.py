from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.responses import FileResponse, Response
from app.schemas import PhotoResponse
from app.crud import add_photo, get_photo_by_hash, get_all_photos, update_photo_caption
from app.db import get_db
from app.image_utils import (
    hash_image_bytes,
    save_image_file,
    get_image_file_path,
    scan_photos_folder_on_startup,
)
from PIL import UnidentifiedImageError
from pathlib import Path
import mimetypes

router = APIRouter()


from fastapi import Request


@router.post(
    "/photos",
    response_model=PhotoResponse,
    status_code=201,
    operation_id="upload_photo",
)
def upload_photo(request: Request, file: UploadFile = File(...)) -> PhotoResponse:
    photos_dir = request.app.state.photos_dir
    session_maker = getattr(request.app.state, "db_sessionmaker", None)
    db_gen = get_db(session_maker=session_maker)
    db = next(db_gen)
    contents = file.file.read()
    sha256 = hash_image_bytes(contents)
    filename = file.filename
    assert filename is not None, "UploadFile filename is required"
    existing = get_photo_by_hash(db, sha256)
    if existing:
        raise HTTPException(
            status_code=409, detail="Photo with this hash already exists."
        )
    save_image_file(photos_dir, filename, contents)
    photo = add_photo(db, sha256, filename, caption=None)
    return PhotoResponse(
        hash=photo.hash_value,
        filename=photo.filename_value,
        caption=photo.caption_value,
    )


@router.get("/photos", response_model=list[PhotoResponse], operation_id="get_photos")
def get_photos(request: Request) -> list[PhotoResponse]:
    session_maker = getattr(request.app.state, "db_sessionmaker", None)
    db_gen = get_db(session_maker=session_maker)
    db = next(db_gen)
    # Rescan folder to pick up new images (watcher removed)
    scan_photos_folder_on_startup(request.app.state.photos_dir, db)
    return [
        PhotoResponse(
            hash=p.hash_value, filename=p.filename_value, caption=p.caption_value
        )
        for p in get_all_photos(db)
    ]


@router.post("/rescan", operation_id="rescan_photos")
def rescan_photos(request: Request) -> dict[str, str]:
    photos_dir = request.app.state.photos_dir
    session_maker = getattr(request.app.state, "db_sessionmaker", None)
    db_gen = get_db(session_maker=session_maker)
    db = next(db_gen)
    scan_photos_folder_on_startup(photos_dir, db)
    return {"detail": "Rescan started."}


@router.get(
    "/photos/{hash}", response_model=PhotoResponse, operation_id="get_photo_by_hash"
)
def get_photo_by_hash_endpoint(request: Request, hash: str) -> PhotoResponse:
    session_maker = getattr(request.app.state, "db_sessionmaker", None)
    db_gen = get_db(session_maker=session_maker)
    db = next(db_gen)
    photo = get_photo_by_hash(db, hash)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    return PhotoResponse(
        hash=photo.hash_value,
        filename=photo.filename_value,
        caption=photo.caption_value,
    )


@router.patch(
    "/photos/{hash}/caption",
    response_model=PhotoResponse,
    operation_id="patch_photo_caption",
)
def patch_photo_caption_route(
    request: Request, hash: str, caption: str = Body(..., embed=True)
) -> PhotoResponse:
    session_maker = getattr(request.app.state, "db_sessionmaker", None)
    db_gen = get_db(session_maker=session_maker)
    db = next(db_gen)
    photo = update_photo_caption(db, hash, caption)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    return PhotoResponse(
        hash=photo.hash_value,
        filename=photo.filename_value,
        caption=photo.caption_value,
    )


@router.get("/photos/{hash}/image", operation_id="get_photo_image")
def get_photo_image(request: Request, hash: str) -> FileResponse:
    photos_dir = request.app.state.photos_dir
    session_maker = getattr(request.app.state, "db_sessionmaker", None)
    db_gen = get_db(session_maker=session_maker)
    db = next(db_gen)
    photo = get_photo_by_hash(db, hash)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    ext = Path(photo.filename_value).suffix
    file_path = get_image_file_path(
        photos_dir, photo.hash_value, ext, photo.filename_value
    )
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found.")
    mimetype, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        path=file_path, media_type=mimetype or "application/octet-stream"
    )


@router.get("/photos/{hash}/thumbnail", operation_id="get_photo_thumbnail")
def get_photo_thumbnail(request: Request, hash: str) -> Response:
    from app.image_utils import get_or_create_thumbnail, LRUThumbnailCache

    photos_dir = request.app.state.photos_dir
    session_maker = getattr(request.app.state, "db_sessionmaker", None)
    db_gen = get_db(session_maker=session_maker)
    db = next(db_gen)
    photo = get_photo_by_hash(db, hash)
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found.")
    # Get or create cache
    cache = getattr(request.app.state, "thumbnail_cache", None)
    if cache is None:
        import os

        max_mb = float(os.environ.get("THUMBNAIL_CACHE_MB", "100"))
        cache = LRUThumbnailCache(int(max_mb * 1024 * 1024))
        request.app.state.thumbnail_cache = cache
    try:
        thumb_bytes = get_or_create_thumbnail(
            photos_dir, photo.hash_value, photo.filename_value, cache
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Image file not found.")
    except UnidentifiedImageError as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Thumbnail error: {e}")
    from fastapi.responses import Response

    return Response(content=thumb_bytes, media_type="image/jpeg")
