

# 🌸 나의 다이어리 (Personal Diary)

따뜻한 톤의 캘린더형 개인 다이어리 웹앱. **FastAPI + Naver Cloud Platform Object Storage** 로 동작합니다.
일자별로 텍스트 일기와 사진을 함께 저장하고, 한 달의 분위기를 한눈에 볼 수 있는 캘린더 뷰를 제공합니다.

> 📌 이 가이드는 **웹 서비스 구성 경험이 없는 분도** 처음부터 따라 할 수 있도록 작성되었습니다.

---

## ✨ 주요 기능

- 📅 **월간 캘린더 뷰** — 이전/다음 달 이동, 오늘 강조, 일기가 있는 날에 큰 이모지 표시
- 📝 **텍스트 + 📸 사진 동시 저장** — 한 폼·한 클릭으로 함께 기록
- 🎭 **18종 분위기 이모지** — 행복 😊 / 카페 ☕ / 여행 ✈️ / 축하 🎉 ... 날마다 다른 이모지로 캘린더가 풍부해집니다
- 🌈 요일별 이모지 자동 표시 (월☕ 화🌿 수🌤 목🌷 금🎉 토🌈 일🛋)
- ✅ 저장 완료 토스트 팝업
- 🎨 살구색 따뜻한 톤의 친근한 UI · 모바일 반응형

---

## 🛠 기술 스택

| 영역 | 기술 |
|---|---|
| Backend | FastAPI, Uvicorn, boto3 |
| Storage | Naver Cloud Platform Object Storage (S3 호환) |
| Frontend | Jinja2 + Vanilla JS + CSS |
| 런타임 | Python 3.11+ |

---

## 📋 사전 준비

1. **Python 3.11 이상** — [python.org](https://www.python.org/downloads/) 에서 다운로드
2. **Git** 
3. **NCP(네이버 클라우드 플랫폼) 계정** — [ncloud.com](https://www.ncloud.com) 에서 가입 (신용카드 등록 필요 — 무료 한도 제공)
4. (배포 시) **NCP Compute 서버** 또는 임의의 Linux 서버

---

## 🚀 처음부터 끝까지 — 단계별 가이드

### 1단계 · 저장소 클론

```bash
git clone <저장소-URL> 
cd diary-app
```

### 2단계 · NCP에서 Object Storage 준비

#### 2-1. 버킷 생성

1. [NCP 콘솔](https://console.ncloud.com) 로그인
2. 좌측 메뉴 **Services → Storage → Object Storage**
3. **Bucket Management** 화면에서 **버킷 생성** 클릭
4. 버킷 정보 입력:
   - **버킷 이름**: 예) `my-diary-bucket` (오브젝트스토리지 이름은 고유해야합니다)입력 후 하단의 '다음' 버튼 클릭
   - 설정관리, 암호화 관리는 디폴트값 유지 후 하단의 '다음' 버튼 클릭
   - 권한 관리 > 전체 공개 > '공개 안함' 선택 후 하단의 '다음' 버튼 클릭
   - 하단의 '버킷 생성' 클릭
5. 생성 완료 후 버킷 이름을 메모해 둡니다 (`.env`에 입력할 값)

#### 2-2. API 인증키 발급

1. 콘솔 우측 상단 본인 계정명 클릭 → **마이페이지**
2. 좌측 메뉴 **계정 및 보안 관리 → 보안 관리 → 접근 관리 이동**
3. **Access Key ID** 와 **Secret Key** 두 값을 모두 메모(이전 과정에서 API Key값을 생성하였기에 기 생성된 키 값을 복사합니다. 이전 과정에서 생성하지 않으신 분들은 '새로운 API 인증키 생성'을 통해 생성 진행합니다.)


#### 2-3. ACG설정

- **ACG (Access Control Group) 규칙 추가**: 콘솔 → Server → ACG → 해당 서버의 ACG → 인바운드 규칙에 **TCP myip에 대한 8000포트** 추가


### 3단계 · 환경변수 설정

```bash
cp .env.example .env
```

생성된 `.env`를 편집기로 열어서, 2단계에서 메모한 값들로 채웁니다:

```dotenv
NCP_ACCESS_KEY=발급받은_액세스_키
NCP_SECRET_KEY=발급받은_시크릿_키
NCP_ENDPOINT=https://kr.object.ncloudstorage.com
NCP_REGION=kr-standard
NCP_BUCKET=2-1단계에서_생성한_버킷_이름

APP_HOST=0.0.0.0
APP_PORT=8000
```

> ⚠️ `.env` 파일은 절대 깃에 커밋하지 마세요. `.gitignore`에 이미 등록되어 있습니다.

### 4단계 · 가상환경 생성 및 의존성 설치

`run.sh`는 프로젝트 폴더 안의 `venv/` 가상환경을 활성화한 뒤 앱을 실행합니다. 따라서 최초 1회는 아래 명령으로 가상환경을 만들고 패키지를 설치해야 합니다.

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> 💡 Windows(PowerShell)에서는 활성화 명령이 `venv\Scripts\Activate.ps1` 입니다.
> 💡 이 단계를 건너뛰면 실행 시 `./run.sh: line 4: venv/bin/activate: No such file or directory` 오류가 발생합니다.

### 5단계 · 실행

```bash
./run.sh
```

 **http://<서버-공인IP>:8000** 으로 접속하되, 서버의 방화벽(OS)과 **NCP ACG(Access Control Group)** 모두에서 8000번 포트 인바운드가 허용되어 있어야 합니다.

---

## 📂 프로젝트 구조

```
diary/
├─ app.py              # FastAPI 라우터 + 비즈니스 로직
├─ storage.py          # NCP Object Storage 클라이언트 (서명 분리 처리)
├─ templates/
│  ├─ base.html        # 공통 레이아웃 + 토스트 컴포넌트
│  ├─ index.html       # 캘린더 뷰 + 일기 목록
│  └─ entry.html       # 날짜별 일기 작성/조회 (통합 폼)
├─ static/
│  └─ style.css        # 따뜻한 톤 디자인
├─ requirements.txt
├─ .env.example        # 환경변수 템플릿
├─ run.sh              # 실행 스크립트
├─ .gitignore
└─ README.md
```

### Object Storage 키 구조

NCP 버킷 안에는 다음 형태로 데이터가 저장됩니다:

```
ncp-diary/
├─ entries/
│  ├─ 2026-05-18.json     # 해당 날짜의 일기 (텍스트 + 사진 메타 + 분위기)
│  ├─ 2026-05-19.json
│  └─ ...
└─ photos/
   ├─ 2026-05-18/
   │  ├─ 1b95fcb3....png  # 원본 사진 (uuid로 안전 저장)
   │  └─ ...
   └─ ...
```

각 `entries/*.json` 파일 예시:
```json
{
  "date": "2026-05-18",
  "text": "오늘은 카페에서 책을 읽었다.",
  "photos": [
    { "id": "1b95...", "key": "photos/2026-05-18/1b95....png",
      "filename": "cafe.png", "content_type": "image/png",
      "size": 92481, "uploaded_at": "2026-05-18T07:01:50Z" }
  ],
  "mood": "☕",
  "updated_at": "2026-05-18T07:01:50Z"
}
```

---

## 🌐 라우트 요약

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/` | 캘린더 + 일기 목록 |
| GET | `/entry/{YYYY-MM-DD}` | 해당 날짜 일기 조회/작성 페이지 |
| POST | `/entry/{YYYY-MM-DD}` | 텍스트 + 사진 + 분위기 통합 저장 |
| POST | `/entry/{YYYY-MM-DD}/photos/{photo_id}/delete` | 사진 개별 삭제 |
| GET | `/favicon.ico` | 인라인 SVG 파비콘 |
| GET | `/static/*` | 정적 자원 (CSS) |

---

## 🐛 트러블슈팅

### Q1. 이미지 업로드 시 `AccessDenied` 만 발생합니다 (텍스트는 저장됨)

NCP Object Storage 환경에 따라 **`PutObject`만 SigV4를 거부하고 SigV2를 요구**하는 경우가 있습니다. 이 프로젝트의 [storage.py](storage.py)는 이미 다음과 같이 두 개의 boto3 클라이언트로 분리해 처리하고 있어, 일반적으로는 그대로 동작합니다:

```python
self.client = boto3.client("s3", **common, config=Config(signature_version="s3v4"))  # list/get/delete
self.writer = boto3.client("s3", **common, config=Config(signature_version="s3"))    # put 전용
```

여전히 `AccessDenied`가 나면 다음을 차례로 점검:
1. NCP 콘솔 UI에서 같은 버킷에 직접 파일 업로드가 되는지 — 안 되면 계정/조직 차원 제약 (NCP 고객지원 문의)
2. 사용 중인 키가 Sub Account 키라면 `s3:PutObject` 권한이 부여되었는지
3. 결제 정보 및 사용량 한도

### Q2. 공인 IP로 접속이 안 됩니다

- OS 방화벽: `iptables -L INPUT -n` 으로 8000번 ACCEPT 확인
- **NCP ACG (Access Control Group)**: 콘솔 → Server → ACG → 해당 서버의 ACG → 인바운드 규칙에 **TCP myip/0 8000** 추가
- 앱이 `0.0.0.0`에 바인딩되었는지 확인 (`.env`의 `APP_HOST=0.0.0.0`)

### Q3. 사진이 보이지 않습니다 (404 또는 접근 거부)

사진은 1시간 유효한 **presigned URL**로 접근합니다. 다음을 확인:
- 서버 시간과 NCP 엔드포인트의 시간 차이가 ±15분 이내인지 (`date -u` 로 확인)
- 페이지를 1시간 이상 띄워둔 상태에서 보고 있다면 새로고침해 새 presigned URL 받기

### Q4. 캘린더에 이모지가 표시되지 않습니다

- 일기를 저장한 다음 캘린더 페이지를 새로고침해야 합니다.
- 분위기 이모지를 선택하지 않은 일기는 글/사진 유무에 따라 자동으로 📝 / 🖼️ / 📸가 표시됩니다.

### Q5. 다른 리전(싱가포르/일본 등)을 쓰고 싶습니다

`.env`의 `NCP_ENDPOINT`와 `NCP_REGION`을 해당 리전 값으로 변경:

| 리전 | NCP_ENDPOINT | NCP_REGION |
|---|---|---|
| 한국 (기본) | https://kr.object.ncloudstorage.com | kr-standard |
| 싱가포르 | https://sg.object.ncloudstorage.com | sg-standard |
| 일본 | https://jp.object.ncloudstorage.com | jp-standard |

### Q6. 의존성 설치 실패 (`pip install` 에러)

- Python 3.11 이상인지 확인: `python3 --version`
- pip 업그레이드: `pip install --upgrade pip`
- 패키지 빌드 도구가 부족하면: `sudo dnf install gcc python3-devel` (RHEL/CentOS) / `sudo apt install build-essential python3-dev` (Debian/Ubuntu)

---

## 🔒 보안 메모

- 이 앱은 **인증 기능이 없습니다.** 외부 노출 시 다음 중 하나로 보호하세요:
  - nginx Basic Auth 리버스 프록시
  - NCP **Cloud Functions Authorizer** 또는 API Gateway
  - 방화벽으로 접근 IP 제한
- `.env`는 깃에 절대 커밋 금지 (`.gitignore`에 등록되어 있음)
- API 키는 정기적으로 회전(rotate), 노출 의심 시 즉시 NCP 콘솔에서 폐기·재발급
- 사진은 비공개 버킷에 저장되며 presigned URL로만 접근 가능 (만료 시 자동 차단)

---

## 🧪 로컬 개발 팁

자동 리로드로 개발:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

서버 로그 보기 (백그라운드 실행 시):
```bash
tail -f /tmp/diary.log
```

NCP 버킷에 어떤 객체가 들어있는지 확인:
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
        print(o['Key'], o['Size'], 'bytes')
"
```

---

## 📜 라이선스

MIT License — 자유롭게 fork/수정/배포하세요.

---

## 🙋 기여

이슈와 Pull Request 환영합니다.
직접 만든 분위기 이모지 세트나 새로운 캘린더 표시 모드 등을 제안해 주세요!
