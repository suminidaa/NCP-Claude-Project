"""Personal budget web app — receipts + OCR + monthly view."""
import os
import re
import uuid
from datetime import date as date_cls, datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

load_dotenv()

from storage import ObjectStorage  # noqa: E402
from ocr import OCRClient  # noqa: E402

BASE_DIR = Path(__file__).parent
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
YM_RE = re.compile(r"^\d{4}-\d{2}$")
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/heic"}
MAX_IMAGE_BYTES = 20 * 1024 * 1024  # 20 MB

app = FastAPI(title="Personal Budget")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")
storage = ObjectStorage()
ocr = OCRClient()


FAVICON_SVG = (
    b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    b'<rect width="64" height="64" rx="12" fill="#10b981"/>'
    b'<text x="50%" y="56%" text-anchor="middle" dominant-baseline="middle"'
    b' font-size="36" font-family="Apple Color Emoji, Segoe UI Emoji, sans-serif">\xf0\x9f\x92\xb0</text>'
    b"</svg>"
)


def _validate_date(value: str) -> str:
    if not DATE_RE.match(value):
        raise HTTPException(status_code=400, detail="Date must be YYYY-MM-DD")
    return value


def _validate_ym(value: str) -> str:
    if not YM_RE.match(value):
        raise HTTPException(status_code=400, detail="ym must be YYYY-MM")
    return value


def _current_ym() -> str:
    return date_cls.today().isoformat()[:7]


def _days_in_month(ym: str) -> int:
    y, m = map(int, ym.split("-"))
    if m == 12:
        ny, nm = y + 1, 1
    else:
        ny, nm = y, m + 1
    return (date_cls(ny, nm, 1) - date_cls(y, m, 1)).days


def _shift_month(ym: str, delta: int) -> str:
    y, m = map(int, ym.split("-"))
    m += delta
    while m < 1:
        m += 12
        y -= 1
    while m > 12:
        m -= 12
        y += 1
    return f"{y:04d}-{m:02d}"


def _aggregate_daily(receipts: list[dict], ym: str) -> dict[str, int]:
    days = _days_in_month(ym)
    daily = {f"{ym}-{d:02d}": 0 for d in range(1, days + 1)}
    for r in receipts:
        if r["date"] in daily:
            daily[r["date"]] += int(r.get("total", 0) or 0)
    return daily


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(content=FAVICON_SVG, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
def index(request: Request, ym: str | None = None):
    ym = _validate_ym(ym) if ym else _current_ym()
    receipts = storage.list_receipts_for_month(ym)
    budget = storage.get_budget(ym)
    daily = _aggregate_daily(receipts, ym)
    spent = sum(daily.values())
    remaining = budget - spent

    days_in_month = _days_in_month(ym)
    today_iso = date_cls.today().isoformat()
    if ym == _current_ym():
        day_no = int(today_iso[8:10])
        avg = spent // day_no if day_no > 0 else 0
    else:
        avg = spent // days_in_month if days_in_month > 0 else 0

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "ym": ym,
            "prev_ym": _shift_month(ym, -1),
            "next_ym": _shift_month(ym, 1),
            "current_ym": _current_ym(),
            "today": today_iso,
            "budget": budget,
            "spent": spent,
            "remaining": remaining,
            "daily": daily,
            "receipts": receipts,
            "days_in_month": days_in_month,
            "avg_per_day": avg,
            "ocr_configured": ocr.configured,
        },
    )


@app.post("/budget")
def save_budget_endpoint(ym: str = Form(...), amount: int = Form(...)):
    _validate_ym(ym)
    storage.save_budget(ym, max(0, int(amount)))
    return RedirectResponse(url=f"/?ym={ym}&saved=budget", status_code=303)


@app.post("/receipts")
async def upload_receipt(
    file: UploadFile = File(...),
    override_date: str = Form(""),
):
    ctype = (file.content_type or "").lower()
    if ctype not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ctype}")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="File too large")

    ocr_total: int | None = None
    ocr_store: str | None = None
    ocr_date: str | None = None
    ocr_error: str | None = None
    if ocr.configured:
        try:
            image_format = ctype.split("/")[-1]
            result = ocr.extract_receipt(data, image_format=image_format)
            ocr_total = OCRClient.extract_total_amount(result)
            ocr_store = OCRClient.extract_store_name(result)
            ocr_date = OCRClient.extract_payment_date(result)
        except Exception as exc:  # OCR failure shouldn't block upload
            ocr_error = str(exc)[:200]

    if override_date and DATE_RE.match(override_date):
        receipt_date = override_date
    elif ocr_date and DATE_RE.match(ocr_date):
        receipt_date = ocr_date
    else:
        receipt_date = date_cls.today().isoformat()

    img_meta = storage.upload_image(receipt_date, file.filename or "receipt.jpg", ctype, data)

    if ocr_error:
        status = "error"
    elif ocr_total:
        status = "ok"
    elif ocr.configured:
        status = "no_match"
    else:
        status = "no_ocr"

    receipt = {
        "id": uuid.uuid4().hex,
        "date": receipt_date,
        "total": int(ocr_total or 0),
        "store": ocr_store or "",
        "image_key": img_meta["key"],
        "image_filename": img_meta["filename"],
        "ocr_status": status,
        "ocr_error": ocr_error or "",
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
    }
    storage.save_receipt(receipt)
    return RedirectResponse(url=f"/day/{receipt_date}?just_uploaded={receipt['id']}", status_code=303)


@app.get("/day/{date}", response_class=HTMLResponse)
def day_view(request: Request, date: str):
    _validate_date(date)
    receipts = storage.list_receipts_for_date(date)
    for r in receipts:
        if r.get("image_key"):
            r["image_url"] = storage.presigned_url(r["image_key"], expires_in=3600)
    daily_total = sum(int(r.get("total", 0) or 0) for r in receipts)
    return templates.TemplateResponse(
        request,
        "day.html",
        {
            "date": date,
            "ym": date[:7],
            "receipts": receipts,
            "daily_total": daily_total,
        },
    )


@app.post("/receipts/{receipt_id}/update")
def update_receipt(
    receipt_id: str,
    date: str = Form(...),
    total: int = Form(...),
    store: str = Form(""),
):
    _validate_date(date)
    receipt = storage.load_receipt(date, receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    receipt["total"] = max(0, int(total))
    receipt["store"] = store
    receipt["updated_at"] = datetime.utcnow().isoformat() + "Z"
    storage.save_receipt(receipt)
    return RedirectResponse(url=f"/day/{date}?updated=1", status_code=303)


@app.post("/receipts/{receipt_id}/delete")
def delete_receipt_endpoint(receipt_id: str, date: str = Form(...)):
    _validate_date(date)
    receipt = storage.load_receipt(date, receipt_id)
    if receipt is None:
        raise HTTPException(status_code=404, detail="Receipt not found")
    storage.delete_receipt(receipt)
    return RedirectResponse(url=f"/day/{date}?deleted=1", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host=os.environ.get("APP_HOST", "0.0.0.0"),
        port=int(os.environ.get("APP_PORT", "8001")),
        reload=False,
    )
