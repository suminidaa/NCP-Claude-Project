"""NCP CLOVA OCR client.

응답을 자동 감지하여 두 가지 도메인 타입을 모두 지원:

1. Receipt 사전학습 도메인 (유료 모델)
   - `images[0].receipt.result.totalPrice / storeInfo / paymentInfo` 구조로 반환
2. General OCR 도메인 (Free 모델)
   - `images[0].fields[]` 안에 `inferText` 들이 들어있어, 한국어 영수증 패턴으로 직접 파싱
"""
import json
import os
import re
import time
import uuid
from typing import Any, Optional

import requests


# 한국 영수증에서 "총액"을 가리키는 흔한 라벨
TOTAL_KEYWORDS = (
    "합계", "총액", "총합계",
    "결제금액", "받을금액", "지불금액",
    "받으실금액", "결제대상금액", "총결제금액",
    "TOTAL", "Total",
)
# "합계"가 들어있어도 실제 총액이 아닌 항목들 — 매칭에서 제외
EXCLUDE_KEYWORDS = ("부가세", "공급가액", "면세", "할인", "VAT", "거스름", "받은금액", "거스름돈")

# 날짜 패턴
DATE_RE = re.compile(r"(\d{4})[.\-/년]\s*(\d{1,2})[.\-/월]\s*(\d{1,2})")
DATE_SHORT_RE = re.compile(r"(\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})")

# 금액 패턴
PRICE_WITH_COMMA = re.compile(r"\d{1,3}(?:,\d{3})+")
PRICE_PLAIN = re.compile(r"\d{3,7}")

# 상점 이름으로 잡지 말아야 할 헤더 텍스트
SKIP_STORE_TEXTS = {
    "영수증", "RECEIPT", "Receipt",
    "거래내역", "거래내역서",
    "TAX INVOICE", "신용카드매출전표",
    "현금영수증", "간이영수증",
    "감사합니다", "Thank you", "THANK YOU",
}


class OCRClient:
    def __init__(self) -> None:
        self.api_url = os.environ.get("OCR_APIGW_URL", "").strip()
        self.secret = os.environ.get("OCR_SECRET_KEY", "").strip()

    @property
    def configured(self) -> bool:
        return bool(
            self.api_url
            and self.secret
            and not self.api_url.startswith("https://xxxxxxxxxxx")
        )

    def extract_receipt(self, image_bytes: bytes, image_format: str = "jpg") -> dict[str, Any]:
        if not self.configured:
            raise RuntimeError("OCR_APIGW_URL / OCR_SECRET_KEY not configured in .env")
        if image_format == "jpeg":
            image_format = "jpg"
        message = {
            "version": "V2",
            "requestId": str(uuid.uuid4()),
            "timestamp": int(time.time() * 1000),
            "images": [{"format": image_format, "name": "receipt"}],
        }
        files = {"file": (f"receipt.{image_format}", image_bytes)}
        data = {"message": json.dumps(message)}
        headers = {"X-OCR-SECRET": self.secret}
        r = requests.post(self.api_url, headers=headers, data=data, files=files, timeout=45)
        r.raise_for_status()
        return r.json()

    # ---------- 공개 API: 두 응답 구조를 모두 시도 ----------

    @staticmethod
    def extract_total_amount(result: dict[str, Any]) -> Optional[int]:
        amount = _from_receipt_total(result)
        if amount is not None:
            return amount
        return _from_general_total(result)

    @staticmethod
    def extract_store_name(result: dict[str, Any]) -> Optional[str]:
        name = _from_receipt_store(result)
        if name:
            return name
        return _from_general_store(result)

    @staticmethod
    def extract_payment_date(result: dict[str, Any]) -> Optional[str]:
        date = _from_receipt_date(result)
        if date:
            return date
        return _from_general_date(result)


# ---------- Receipt 사전학습 도메인 파서 ----------

def _from_receipt_total(result: dict[str, Any]) -> Optional[int]:
    try:
        price = result["images"][0]["receipt"]["result"]["totalPrice"]["price"]
    except (KeyError, TypeError, IndexError):
        return None
    if not isinstance(price, dict):
        return None
    fmt = price.get("formatted")
    if isinstance(fmt, dict):
        v = fmt.get("value")
        if v:
            cleaned = re.sub(r"[^\d]", "", str(v))
            if cleaned:
                return int(cleaned)
    text = price.get("text", "")
    cleaned = re.sub(r"[^\d]", "", str(text))
    return int(cleaned) if cleaned else None


def _from_receipt_store(result: dict[str, Any]) -> Optional[str]:
    try:
        return result["images"][0]["receipt"]["result"]["storeInfo"]["name"]["text"]
    except (KeyError, TypeError, IndexError):
        return None


def _from_receipt_date(result: dict[str, Any]) -> Optional[str]:
    try:
        date = result["images"][0]["receipt"]["result"]["paymentInfo"]["date"]
    except (KeyError, TypeError, IndexError):
        return None
    if not isinstance(date, dict):
        return None
    fmt = date.get("formatted")
    if isinstance(fmt, dict):
        y, m, d = fmt.get("year"), fmt.get("month"), fmt.get("day")
        if y and m and d:
            try:
                return f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
            except (ValueError, TypeError):
                pass
    return _parse_date_text(date.get("text", "") or "")


# ---------- General OCR (Free) 도메인 파서 ----------

def _general_fields(result: dict[str, Any]) -> list[dict]:
    try:
        return result["images"][0]["fields"]
    except (KeyError, TypeError, IndexError):
        return []


def _from_general_total(result: dict[str, Any]) -> Optional[int]:
    fields = _general_fields(result)
    if not fields:
        return None
    texts = [str(f.get("inferText", "")).strip() for f in fields]

    # 1) 키워드(합계/결제금액 등) 옆에 붙은 금액 찾기
    for i, t in enumerate(texts):
        normalized = t.replace(" ", "").upper()
        if any(ex.upper() in normalized for ex in EXCLUDE_KEYWORDS):
            continue
        if not any(kw.upper() in normalized for kw in TOTAL_KEYWORDS):
            continue
        # 같은 필드 내에 금액이 함께 있으면 먼저 시도
        embedded = _parse_price(t)
        if embedded:
            return embedded
        # 다음 1~5개 필드에서 금액 찾기
        for j in range(i + 1, min(i + 6, len(texts))):
            p = _parse_price(texts[j])
            if p:
                return p

    # 2) 키워드를 못 찾았을 때 — comma-formatted 금액 중 가장 큰 값
    candidates: list[int] = []
    for t in texts:
        for m in PRICE_WITH_COMMA.finditer(t):
            try:
                v = int(m.group(0).replace(",", ""))
                if 100 <= v <= 9_999_999:
                    candidates.append(v)
            except ValueError:
                continue
    return max(candidates) if candidates else None


def _from_general_store(result: dict[str, Any]) -> Optional[str]:
    fields = _general_fields(result)
    # 영수증 상단(앞쪽 필드) 중 의미 있는 첫 텍스트
    for f in fields[:12]:
        t = str(f.get("inferText", "")).strip()
        if not t or len(t) < 2:
            continue
        if t in SKIP_STORE_TEXTS:
            continue
        # 숫자/날짜/구두점만으로 이루어진 텍스트 스킵
        if re.fullmatch(r"[\d.\-/,:\s]+", t):
            continue
        # 주소/전화로 시작하는 줄 스킵
        if re.match(r"^(주소|TEL|Tel|전화|T\.|☎|대표자|사업자)\b", t):
            continue
        return t
    return None


def _from_general_date(result: dict[str, Any]) -> Optional[str]:
    fields = _general_fields(result)
    for f in fields:
        t = str(f.get("inferText", ""))
        parsed = _parse_date_text(t)
        if parsed:
            return parsed
    return None


# ---------- 공용 헬퍼 ----------

def _parse_price(text: str) -> Optional[int]:
    """텍스트에서 첫 번째 가격을 정수(원)로 반환."""
    if not text:
        return None
    m = PRICE_WITH_COMMA.search(text) or PRICE_PLAIN.search(text)
    if not m:
        return None
    cleaned = m.group(0).replace(",", "")
    try:
        v = int(cleaned)
    except ValueError:
        return None
    if 100 <= v <= 9_999_999:
        return v
    return None


def _parse_date_text(text: str) -> Optional[str]:
    if not text:
        return None
    m = DATE_RE.search(text)
    if m:
        y, mo, d = m.groups()
        try:
            return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
        except ValueError:
            return None
    m = DATE_SHORT_RE.search(text)
    if m:
        y, mo, d = m.groups()
        y_int = int(y)
        if y_int < 100:
            y_int += 2000
        try:
            return f"{y_int:04d}-{int(mo):02d}-{int(d):02d}"
        except ValueError:
            return None
    return None
