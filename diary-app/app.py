"""Personal diary web app — text per date + photos on NCP Object Storage."""
import os
import re
from datetime import date as date_cls, datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

from storage import ObjectStorage  # noqa: E402

BASE_DIR = Path(__file__).parent
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/heic"}
MAX_PHOTO_BYTES = 20 * 1024 * 1024  # 20 MB

MOOD_EMOJIS: list[tuple[str, str]] = [
    ("😊", "행복"), ("😍", "설렘"), ("🥰", "감동"), ("😎", "멋짐"),
    ("😌", "평온"), ("🤔", "고민"), ("😴", "피곤"), ("😢", "슬픔"),
    ("🥳", "신남"), ("✨", "특별"), ("🌸", "봄날"), ("🌙", "고요"),
    ("☕", "카페"), ("✈️", "여행"), ("🏃", "운동"), ("📚", "공부"),
    ("🎬", "영화"), ("🎉", "축하"),
]
ALLOWED_MOODS = {e for e, _ in MOOD_EMOJIS}

app = FastAPI(title="Personal Diary")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
storage = ObjectStorage()


def _validate_date(value: str) -> str:
    if not DATE_RE.match(value):
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")
    return value


def _attach_urls(photos: list[dict]) -> list[dict]:
    for p in photos:
        p["url"] = storage.presigned_url(p["key"], expires_in=3600)
    return photos


FAVICON_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    b'<rect width="64" height="64" rx="12" fill="#3b82f6"/>'
    b'<text x="50%" y="54%" text-anchor="middle" dominant-baseline="middle"'
    b' font-size="38" font-family="Apple Color Emoji, Segoe UI Emoji, sans-serif">\xf0\x9f\x93\x93</text>'
    b'</svg>'
)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    entries = storage.list_entries()
    today = date_cls.today().isoformat()
    return templates.TemplateResponse(
        request,
        "index.html",
        {"entries": entries, "today": today},
    )


WEEKDAY_KO = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
WEEKDAY_EMOJI = ["☕", "🌿", "🌤️", "🌷", "🎉", "🌈", "🛋️"]


@app.get("/entry/{entry_date}", response_class=HTMLResponse)
def view_entry(request: Request, entry_date: str):
    _validate_date(entry_date)
    entry = storage.load_entry(entry_date)
    entry["photos"] = _attach_urls(entry.get("photos", []))
    wd = datetime.strptime(entry_date, "%Y-%m-%d").weekday()
    return templates.TemplateResponse(
        request,
        "entry.html",
        {
            "entry": entry,
            "date": entry_date,
            "weekday_name": WEEKDAY_KO[wd],
            "weekday_emoji": WEEKDAY_EMOJI[wd],
            "mood_emojis": MOOD_EMOJIS,
        },
    )


@app.post("/entry/{entry_date}")
async def save_entry(
    entry_date: str,
    text: str = Form(""),
    mood: str = Form(""),
    files: list[UploadFile] = File(default=[]),
):
    _validate_date(entry_date)
    if mood and mood not in ALLOWED_MOODS:
        mood = ""
    existing = storage.load_entry(entry_date)
    photos = list(existing.get("photos", []))

    for upload in files:
        if not upload.filename:
            continue
        ctype = (upload.content_type or "").lower()
        if ctype not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ctype}")
        data = await upload.read()
        if len(data) == 0:
            continue
        if len(data) > MAX_PHOTO_BYTES:
            raise HTTPException(status_code=413, detail=f"File too large: {upload.filename}")
        meta = storage.upload_photo(entry_date, upload.filename or "photo", ctype, data)
        photos.append(meta)

    storage.save_entry(entry_date, text, photos, mood)
    return RedirectResponse(url=f"/entry/{entry_date}?saved=1", status_code=303)


@app.post("/entry/{entry_date}/photos/{photo_id}/delete")
def delete_photo(entry_date: str, photo_id: str):
    _validate_date(entry_date)
    entry = storage.load_entry(entry_date)
    photos = entry.get("photos", [])
    target = next((p for p in photos if p["id"] == photo_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Photo not found")
    storage.delete_photo(target["key"])
    remaining = [p for p in photos if p["id"] != photo_id]
    storage.save_entry(entry_date, entry.get("text", ""), remaining, entry.get("mood", ""))
    return RedirectResponse(url=f"/entry/{entry_date}", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.environ.get("APP_HOST", "0.0.0.0"),
        port=int(os.environ.get("APP_PORT", "8000")),
        reload=False,
    )
