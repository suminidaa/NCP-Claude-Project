# 💰 나의 가계부 (Personal Budget with OCR)

영수증 사진을 업로드하면 **NCP CLOVA OCR**이 자동으로 총액을 인식해 가계부를 채워주는 웹앱.
**FastAPI + NCP Object Storage + CLOVA OCR + Chart.js** 로 동작합니다.

> 📌 이 가이드는 처음 NCP를 쓰는 분도 따라 할 수 있도록 작성되었습니다.

---

## ✨ 주요 기능

- 📸 **영수증 사진 업로드** → **🤖 OCR이 총액·상점·날짜 자동 추출**
- 💵 **월별 예산 설정** — 자유롭게 입력·수정
- 📊 실시간 잔여 예산, 사용률, 일평균 지출 통계
- 📈 **일자별 소비 흐름 차트** (Chart.js 바 차트)
- 🗓️ 일자별 영수증 상세 페이지 — 인식이 틀린 금액은 직접 수정 가능
- ✅ 저장 완료 토스트 알림 · 모바일 반응형 · 민트 그린 톤 친근한 UI

---

## 🛠 기술 스택

| 영역 | 기술 |
|---|---|
| Backend | FastAPI, Uvicorn, boto3, requests |
| Storage | NCP Object Storage (S3 호환) |
| OCR | NCP CLOVA OCR (Receipt 도메인) |
| Chart | Chart.js 4 (CDN) |
| Frontend | Jinja2 + Vanilla JS + CSS |
| Runtime | Python 3.11+ |

---

## 📋 사전 준비

1. **원격 Linux 서버** (NCP Compute)
2. **Python 3.11 이상** (서버에 설치되어 있어야 함)
4. **NCP 계정** ([ncloud.com](https://www.ncloud.com))
5. 로컬 PC에서 서버에 접속하기 위한 **vscode** (이전 과정에서 vscode + Claude + SSH 설치 진행)
6. **Compute > Server > ACG에서 서버에 적용된 ACG(ex.web-dev-vpc-default-acg)에 TCP MyIP에 대한 8001 포트 접근 허용 필요**

---

## 🚀 단계별 가이드

### 0단계 · 원격 서버 접속

이전 과정에서 진행한대로 VSCode를 통해 원격 서버에 접속합니다.

### 1단계 · 프로젝트 받기 (git clone)

원격 서버(VSCode 통합 터미널)에서 git 저장소를 클론합니다.

```bash
git clone <저장소-URL> budget-app
cd budget-app
```

> 💡 위 `<저장소-URL>` 자리에는  GitHub 저장소 주소를 넣으세요.


### 2단계 · NCP Object Storage 준비

#### 2-1. 버킷 생성

1. [NCP 콘솔](https://console.ncloud.com) → **Services → Storage → Object Storage**
2. **Bucket Management → 버킷 생성**
3. 버킷 이름 입력 (예: `my-budget-bucket`) — 버킷 이름은 고유해야 합니다.
4. 하단의 '다음' 버튼 클릭
5. 설정관리, 암호화 관리는 디폴트 값 유지 후 하단의 '다음' 버튼 클릭
6. 권한관리 > 전체 공개 부분에  **공개 안함** 선택 후 하단의 '다음' 버튼 클릭
7. 최종 확인 페이지에서 하단의 '버킷 생성' 클릭

#### 2-2. API 인증키 발급

1. 콘솔 우측 상단 본인 계정명 → **계정 및 보안 관리 → 보안 관리 →  접근관리 → API 인증키**
2. **신규 API 인증키 생성** → Access Key / Secret Key 메모(기존에 발급받은 API키값이 있다면 해당 키 사용)

### 3단계 · NCP CLOVA OCR 신청 (영수증 도메인) ⭐ 가계부 핵심

#### 3-1. CLOVA OCR 서비스 신청 (한 번만)

1. NCP 콘솔 → **Services → AI·Service → CLOVA OCR**
2. **이용 신청** 버튼 클릭 → 약관 동의 → 신청 완료

#### 3-2. 도메인 생성 (Receipt 타입)

1. CLOVA OCR 대시보드 → **Domain → Domain 생성 → 일반/템플릿 도메인 생성**
2. 정보 입력:
   - **도메인 명**: 예) `my-receipt-domain` 입력 후 우측의 '중복확인' 클릭(이미 사용중인 도메인 명이라면 다른 이름 입력)
   - **도메인 코드**: **`Receipt`** 입력 후 우측의 '중복확인' 클릭(이미 사용중인 도메인 코드라면 다른 코드명 입력)
   - **인식 언어**: 한국어
   - **서비스 타입**: 템플릿
   - **인식 모델**: Basic
   - **서비스 플랜**: Basic (Basic플랜은 최대300건의 API만 호출이 가능합니다. 그 이상이 필요할 경우엔 유료 플랜 사용이 필요합니다.)
3. 생성 후 '템플릿빌더'를 클릭하여 상세 페이지로 이동

#### 3-3. APIGW URL과 Secret Key 발급

1.  **APIGW 연동 탭 클릭 → 연동 클릭**
2.  **Secret Key 우측의 '생성' 클릭**  표시되는 Secret Key 복사
3.  **APIGW Invoke URL** 복사 — 형태:
   ```
   https://xxxxxxxxxxx.apigw.ntruss.com/custom/v1/00000/xxxxxxxxxx/document/receipt
   ```
4. **두 값을 메모해 둡니다 (5단계에서 `.env`에 입력)**

#### 3-4. OCR 서비스 배포
1.  **좌측메뉴 중 '템플릿 목록' 클릭**
2.  **상단의 '+템플릿 생성'클릭**
   - **템플릿명** : 영수증 입력 후 우측의 확인 버튼 클릭
   - **샘플 이미지 업로드** : https://kr.object.ncloudstorage.com/academy2025/receipt-budgetapp.png
   - **대표 샘플명** : 영수증 입력 후 우측의 확인 클릭(빨간색 박스 영역을 움직여서 업로드 한 이미지의 '영수증' 부분 선택)
   - **필드지정** : '+필드추가' 클릭 후 박스 영역을 움직어 '배스킨라빈스 광교아브뉴프랑점' 영역 선택 -> 필드이름은 상점으로 기입
3.  **하단의 '저장' 버튼 클릭**
4.  **좌측 메뉴 상단의 '배포관리' 클릭**
5.  **방금 생성한 영수증 템플리 선택 후 상단의 '베타 배포' 클릭**(안내 팝업나오면 확인 클릭)
6.  **베타 배포 완료 후 '베타 배포' 옆 '서비스 배포' 버튼 클릭**(베타 배포가 끝나야 서비스 배포 버튼이 활성화됩니다)

 💡 위 배포과정을 진행하지 않으면 OCR API가 정상동작하지 않습니다.

### 4단계 · Python 가상환경 및 의존성 설치

원격 서버 셸에서 실행:

```bash
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

> 시스템 기본 `python3`가 3.11 미만이면 `python3.11 -m venv venv` 처럼 명시적으로 호출하세요.

### 5단계 · 환경변수 설정

```bash
cp .env.example .env
```

`.env`를 편집:

```dotenv
# Object Storage
NCP_ACCESS_KEY=발급받은_액세스_키
NCP_SECRET_KEY=발급받은_시크릿_키
NCP_ENDPOINT=https://kr.object.ncloudstorage.com
NCP_REGION=kr-standard
NCP_BUCKET=2-1단계_버킷_이름

# CLOVA OCR
OCR_APIGW_URL=3-3단계_APIGW_URL
OCR_SECRET_KEY=3-3단계_Secret_Key

APP_HOST=0.0.0.0
APP_PORT=8001
```

### 6단계 · 실행

```bash
./run.sh
# 또는
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8001
```

브라우저에서 **http://<서버의 공인IP>:8001** 접속.

원격 서버라면 OS 방화벽과 **NCP ACG** myip에 대한 **TCP 8001** 인바운드를 열어주세요.
모든 IP에 대한 8001포트를 오픈하는 것은 보안상 추천하지 않습ㄴ디ㅏ. 

---

## 📂 프로젝트 구조

```
budget/
├─ app.py                  # FastAPI 라우터
├─ storage.py              # NCP Object Storage 클라이언트 (SigV2/v4 분리)
├─ ocr.py                  # CLOVA OCR Receipt API 클라이언트
├─ templates/
│  ├─ base.html            # 공통 레이아웃 + 토스트
│  ├─ index.html           # 월간 대시보드 (예산, 차트, 업로드)
│  └─ day.html             # 일자별 영수증 상세
├─ static/
│  └─ style.css            # 민트/그린 톤 디자인
├─ requirements.txt
├─ .env.example
├─ .gitignore
├─ run.sh
└─ README.md
```

### Object Storage 키 구조

```
my-budget-bucket/
├─ budgets/
│  └─ 2026-05.json                       # { "month": "2026-05", "amount": 1500000 }
├─ receipts/
│  └─ 2026-05-18/
│     └─ <uuid>.json                     # 영수증 메타 (date, total, store, image_key, ocr_status, ...)
└─ receipt-images/
   └─ 2026-05-18/
      └─ <uuid>.jpg                      # 원본 이미지
```

영수증 JSON 예시:
```json
{
  "id": "1b95...",
  "date": "2026-05-18",
  "total": 12500,
  "store": "스타벅스 강남점",
  "image_key": "receipt-images/2026-05-18/1b95....jpg",
  "image_filename": "IMG_0123.jpg",
  "ocr_status": "ok",
  "uploaded_at": "2026-05-18T07:01:50Z"
}
```

`ocr_status` 값:
- `ok` — OCR이 총액 추출에 성공
- `no_match` — OCR은 호출됐지만 총액을 못 찾음 (수동 입력 필요)
- `error` — OCR 호출 자체가 실패 (네트워크/인증/한도)
- `no_ocr` — OCR이 환경변수에 미설정

---

## 🌐 라우트 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/` | 이번 달 대시보드 (예산·차트·일별 표·업로드) |
| GET | `/?ym=YYYY-MM` | 특정 월 대시보드 |
| POST | `/budget` | 월 예산 저장 |
| POST | `/receipts` | 영수증 업로드 → OCR → 저장 |
| GET | `/day/{YYYY-MM-DD}` | 일자별 영수증 목록 / 수정 |
| POST | `/receipts/{id}/update` | 총액·상점 수정 |
| POST | `/receipts/{id}/delete` | 영수증 + 이미지 삭제 |

---

## 🤖 OCR 동작 흐름

```
사용자가 영수증 사진 업로드
   ↓
서버: NCP Object Storage에 원본 이미지 저장
   ↓
서버: CLOVA OCR Receipt API 호출 (multipart, X-OCR-SECRET 헤더)
   ↓
응답 파싱:
   • totalPrice.price.formatted.value  → 총액 (원)
   • storeInfo.name.text              → 상점 이름
   • paymentInfo.date.formatted       → 영수증 날짜
   ↓
영수증 JSON 생성 → Object Storage에 저장
   ↓
일자별 상세 페이지로 리다이렉트
```

OCR 응답에서 총액 추출이 실패해도 업로드 자체는 성공합니다. 일자별 페이지에서 직접 금액을 입력·수정하면 됩니다.

---

## 🐛 트러블슈팅

### Q1. 영수증을 업로드해도 총액이 0으로만 저장됩니다

다음을 순서대로 점검:
1. **`.env`의 `OCR_APIGW_URL`과 `OCR_SECRET_KEY`가 비어있지 않은지** — 비어있으면 페이지 상단에 노란 경고가 표시됩니다.
2. **CLOVA OCR Domain의 Service Type이 `Receipt`인지** — General이면 텍스트만 옵니다.
3. **영수증 사진이 또렷한지** — 흐릿하거나 휘었거나 잘렸으면 인식 실패. 정면에서 평평하게 촬영하세요.
4. 인식이 끝나도 OCR이 가격을 못 찾는 영수증이 있습니다(수기/특수 양식). 페이지에서 직접 금액을 입력·수정하세요.

### Q2. 영수증 사진은 업로드되는데 OCR API 호출에서 401 / 403 에러

- `OCR_SECRET_KEY`가 정확한지 확인. 공백 포함 여부, 따옴표 등.
- NCP CLOVA OCR 도메인이 **활성화 상태**인지 콘솔에서 확인.

### Q3. `AccessDenied` (Object Storage)

다이어리 프로젝트와 같은 이슈로, NCP는 작업별로 받아들이는 S3 서명 버전이 다를 수 있습니다 (`PutObject`만 SigV2 필요). [storage.py](storage.py)에서 이미 두 boto3 클라이언트로 분리해 처리하고 있어, 일반적으로 그대로 동작합니다.

여전히 실패하면 콘솔 UI에서 같은 버킷에 직접 업로드가 되는지 확인해 계정/조직 차원 제약 여부를 가립니다.

### Q4. 차트가 비어 보입니다

- 해당 월에 영수증이 한 건도 없으면 모든 일별 값이 0이라 막대가 안 보입니다.
- 영수증을 한 건 업로드한 뒤 페이지를 새로고침해 보세요.

### Q5. 사진이 안 보입니다 (presigned URL 만료)

- 이미지 링크는 1시간 동안 유효한 presigned URL입니다. 새로고침해 새 URL을 받으세요.
- 서버 시간과 NCP 엔드포인트 시간이 ±15분 이내인지 (`date -u`).

### Q6. 다른 NCP 리전(싱가포르·일본)을 쓰고 싶습니다

`.env`의 `NCP_ENDPOINT`와 `NCP_REGION` 변경:

| 리전 | NCP_ENDPOINT | NCP_REGION |
|---|---|---|
| 한국 (기본) | https://kr.object.ncloudstorage.com | kr-standard |
| 싱가포르 | https://sg.object.ncloudstorage.com | sg-standard |
| 일본 | https://jp.object.ncloudstorage.com | jp-standard |

CLOVA OCR도 리전이 다르면 다른 APIGW URL이 발급됩니다.

---

## 🔒 보안 메모

- 본 앱은 **인증 기능이 없습니다.** 영수증에는 개인정보가 포함될 수 있으니 외부 노출 시 다음 중 하나로 보호:
  - nginx Basic Auth 리버스 프록시
  - NCP API Gateway Authorizer
  - 방화벽으로 접근 IP 제한
- `.env` 파일은 외부에 공유하지 마세요 — NCP 자격증명과 OCR Secret Key가 들어있습니다. (`.gitignore`에 등록되어 있어 `git push` 시 자동으로 제외됩니다)
- API 키와 OCR Secret Key는 정기적으로 교체, 노출 시 즉시 폐기·재발급
- 영수증 이미지는 비공개 버킷 + presigned URL로만 접근

---

## 🧪 개발 팁

자동 리로드:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8001
```

OCR API 테스트 (요청만 보내보기):
```bash
venv/bin/python -c "
import os, json, base64
from dotenv import load_dotenv
load_dotenv()
from ocr import OCRClient
ocr = OCRClient()
print('OCR configured:', ocr.configured)
with open('test_receipt.jpg', 'rb') as f:
    result = ocr.extract_receipt(f.read(), 'jpg')
print(json.dumps(result, indent=2, ensure_ascii=False)[:2000])
print('총액:', OCRClient.extract_total_amount(result))
print('상점:', OCRClient.extract_store_name(result))
print('날짜:', OCRClient.extract_payment_date(result))
"
```

NCP 버킷 객체 직접 조회:
```bash
venv/bin/python -c "
import os, boto3
from botocore.client import Config
from dotenv import load_dotenv
load_dotenv()
s3 = boto3.client('s3', endpoint_url=os.environ['NCP_ENDPOINT'],
    aws_access_key_id=os.environ['NCP_ACCESS_KEY'],
    aws_secret_access_key=os.environ['NCP_SECRET_KEY'],
    region_name='kr-standard', config=Config(signature_version='s3v4'))
for page in s3.get_paginator('list_objects_v2').paginate(Bucket=os.environ['NCP_BUCKET']):
    for o in page.get('Contents', []):
        print(o['Key'], o['Size'])
"
```

---

## 📜 라이선스

MIT — 자유롭게 수정·사용하세요.
