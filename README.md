# NCP + VS Code + Claude Code 랩 가이드

> **대상:** VS Code에 익숙하신 분
>
> **필요사항:** 본 과정에서는 Claude Code를 활용하며, Claude Code는 **유료 요금제** 사용이 필요합니다.

---

## [잠깐] Claude Desktop과 Claude Code의 차이

| 구분 | Claude Desktop | Claude Code |
|------|----------------|-------------|
| 형태 | claude.ai, 데스크톱 앱, 모바일 앱 | 터미널 기반 / IDE 통합 |
| 용도 | 일반 대화형 AI 인터페이스 | 소프트웨어 개발용 **에이전틱 코딩 어시스턴트** |
| 요금제 | 무료 플랜 사용 가능 | **무료 플랜 사용 불가** (최소 Pro $20/월 또는 API 크레딧 필요) |

무료 티어는 웹, iOS, Android, 데스크톱에서 Claude 채팅만 제공하며, 터미널 기반 Claude Code 환경은 최소 Pro 구독($20/월) 또는 API 크레딧이 필요합니다.

---

## Part 1. VS Code 설치

Visual Studio Code(VS Code)는 Microsoft가 만든 무료 코드 에디터입니다. 가볍고 빠르며, 다양한 확장을 통해 거의 모든 개발 환경을 지원합니다.

### 1-1. 다운로드

1. 브라우저로 [https://code.visualstudio.com](https://code.visualstudio.com) 접속
2. 큰 파란색 **[Download]** 버튼 클릭
3. 운영체제가 자동 감지되어 적절한 설치 파일이 다운로드됩니다.

### 1-2. 설치

#### macOS

1. 다운로드한 `.zip` 파일의 압축을 풉니다.
2. 나온 `Visual Studio Code.app`을 `/Applications` 폴더로 드래그합니다.
3. Launchpad에서 Visual Studio Code를 실행합니다.

#### Windows

1. 다운로드한 `.exe` 파일을 더블클릭합니다.
2. 약관 동의 → 설치 경로 → 추가 작업 선택 화면이 나옵니다.
3. **"PATH에 추가" 옵션을 반드시 체크합니다.** (이후 터미널에서 `code` 명령으로 VS Code를 열 수 있게 됩니다.)
4. 설치 완료 후 VS Code를 실행합니다.

---

## Part 2. Claude Code 설치 및 VS Code 연동

Claude Code는 터미널에서 동작하는 Anthropic 공식 AI 코딩 도구입니다. VS Code 확장을 함께 설치하면 에디터에서 코드 변경사항을 실시간으로 확인할 수 있습니다.

### 2-1. Claude Code 설치

1. VS Code → **Extensions** (`Ctrl+Shift+X`)
2. 검색창에 `Claude Code` 입력
3. **"Claude Code for VSCode"** (Anthropic 공식) → **[설치]** 클릭

![Claude Code 확장 설치](images/image1.png)

### 2-2. Claude Code 로그인

1. **Claude.ai Subscription** 클릭
2. 브라우저가 열리면서 Anthropic 로그인 페이지로 이동
3. 로그인 진행
4. 인증 완료 후 터미널로 돌아오면 Claude Code 프롬프트가 표시됩니다.

### 2-3. 연동 확인

1. 아무 폴더든 VS Code로 엽니다.
2. 우측 상단의 **Claude 로고**를 선택합니다.
3. Claude 실행창이 열리는지 확인합니다.

![Claude 실행창 확인](images/image2.png)

---

## Part 3. Remote-SSH 확장 설치

Remote-SSH는 SSH로 원격 서버에 접속해, 로컬 VS Code 창에서 원격 서버의 파일을 직접 편집할 수 있게 해주는 Microsoft 공식 확장입니다.

### 3-1. 확장 설치

1. VS Code 왼쪽 사이드바에서 **Extensions 아이콘** (네모 4개) ![Extensions 아이콘](images/image3.png) 클릭
2. 검색창에 `Remote - SSH` 입력
3. **"Remote - SSH"** (Microsoft 발행, 파란색 인증 마크 확인) → **[설치]** 클릭
4. 함께 설치되는 **"Remote - SSH: Editing Configuration Files"**도 자동 설치됩니다.

### 3-2. 설치 확인

왼쪽 사이드바 가장 아래쪽에 `><` 모양 아이콘(Remote Explorer)이 생기면 정상입니다.

![Remote Explorer 아이콘](images/image4.png)

---

## Part 4. SSH 키와 config 준비

Remote-SSH로 NCP 서버에 접속하려면 두 가지가 필요합니다:

1. 서버용 SSH 개인 키 파일 (`.pem`)
2. SSH 설정 파일 (`~/.ssh/config`)

### 4-1. SSH 키 위치 확인

`provision_server`로 NCP 서버를 만들었다면 다운로드 폴더에 `{서버이름}.pem` 파일이 자동 생성되어 있습니다.

> 예: `web-dev`라는 이름으로 서버를 만들었다면 다운로드 폴더에 `web-dev.pem` 파일이 있어야 합니다.

### 4-2. 서버 공인 IP 확인

1. NCP 콘솔([https://console.ncloud.com](https://console.ncloud.com)) → **Server → Server**
2. 해당 서버의 **"공인 IP"** 컬럼 값을 메모합니다.
3. 또는 Claude Desktop에서 `"내 NCP 서버 목록 보여줘"`로도 확인 가능합니다.

### 4-3. SSH 비밀번호 초기화 (Rocky Linux)

NCP는 처음 생성된 서버에 대해 콘솔에서 "관리자 비밀번호 확인" 절차를 거쳐야 SSH 접속이 가능합니다.

1. NCP 콘솔 → **Server** → 해당 서버 선택
2. 상단 **[서버 관리 및 설정 변경]** → **[관리자 비밀번호 확인]** 클릭
3. 본인이 만든 키 파일(`.pem`) 업로드
4. `root` 계정의 초기 비밀번호가 표시됨 → 메모

> Remote-SSH는 키 기반 접속을 우선 사용하므로, NCP가 부여한 비밀번호 대신 `.pem` 키로 접속합니다. 비밀번호 확인 단계는 콘솔의 안전 장치일 뿐입니다.

### 4-4. SSH config 파일 작성

VS Code Remote-SSH가 사용할 설정 파일을 만듭니다.

**파일 위치:**

| OS | 경로 |
|----|------|
| macOS / Linux / WSL | `~/.ssh/config` |
| Windows (PowerShell) | `C:\Users\사용자명\.ssh\config` |

파일이 없으면 새로 만들고, 있으면 아래 내용을 추가합니다.

```ssh-config
Host ncp-web-dev
    HostName 공인.IP.주소.여기에
    User root
    IdentityFile ~/.ssh/[인증키 파일.pem]
    IdentitiesOnly yes
    StrictHostKeyChecking no
```

### 4-5. config 파일 권한

```bash
chmod 600 ~/.ssh/config
```

---

## Part 5. VS Code에서 NCP 서버에 접속

### 5-1. 접속 시작

1. VS Code 좌측 하단의 **`><` 모양 버튼** 클릭 (또는 `F1` → `Remote-SSH: Connect to Host`)
2. 드롭다운에서 방금 등록한 별칭(예: `ncp-web-dev`) 선택
3. `root`에 대한 비밀번호 요구 시 콘솔 화면에서 확인한 `root` 패스워드 기입

### 5-2. 연결 확인

새 창의 좌측 하단에 `SSH: ncp-web-dev` 같은 표시가 보이면 정상 접속된 것입니다.

---

## 다음 단계 🌸 나의 다이어리 (Personal Diary) 만들어보기
 
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
2. **Git** — [git-scm.com](https://git-scm.com/downloads)
3. **NCP(네이버 클라우드 플랫폼) 계정** — [ncloud.com](https://www.ncloud.com) 에서 가입 (신용카드 등록 필요 — 무료 한도 제공)
4. (배포 시) **NCP Compute 서버** 또는 임의의 Linux 서버
 
---
 
## 🚀 처음부터 끝까지 — 단계별 가이드
 
### 1단계 · 저장소 클론
 
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```
 
### 2단계 · NCP에서 Object Storage 준비
 
#### 2-1. 버킷 생성
1. [NCP 콘솔](https://console.ncloud.com) 로그인
2. 좌측 메뉴 **Services → Storage → Object Storage**
3. **Bucket Management** 화면에서 **버킷 생성** 클릭
4. 버킷 정보 입력:
   - **버킷 이름**: 예) `my-diary-bucket` (전역 고유 — 다른 사람이 쓴 이름은 못 씀)
   - **공개 여부**: **비공개(Private)** 선택 ← 중요
5. 생성 완료 후 버킷 이름을 메모해 둡니다 (`.env`에 입력할 값)
 
#### 2-2. API 인증키 발급
1. 콘솔 우측 상단 본인 계정명 클릭 → **마이페이지**
2. 좌측 메뉴 **계정 관리 → 인증키 관리**
3. **신규 API 인증키 생성** 클릭
4. **Access Key ID** 와 **Secret Key** 두 값을 모두 메모
   - ⚠️ Secret Key는 발급 직후에만 표시됩니다. 잃어버리면 키를 폐기하고 재발급해야 합니다.
   - 메인 계정 키로 발급 시 모든 권한이 자동 부여됩니다.
 
#### 2-3. (선택) Sub Account 사용 시 권한 확인
- 메인 계정 키가 아니라 **Sub Account(IAM)** 키로 운영하려면, 해당 Sub Account에 `NCP_ObjectStorage_FullAccess` 정책이 부여되어 있어야 합니다.
- 콘솔 → **Services → IAM/Sub Account → 사용자 → 정책 부여**
 
### 3단계 · 로컬 환경 구성
 
```bash
# 가상환경 생성 (프로젝트별로 독립된 파이썬 패키지 공간)
python3 -m venv venv
 
# 가상환경 활성화
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows PowerShell
 
# 의존성 설치
pip install -r requirements.txt
```
 
### 4단계 · 환경변수 설정
 
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
 
### 5단계 · 실행
 
```bash
./run.sh
```
 
또는 수동으로:
 
```bash
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000
```
 
브라우저에서 **http://localhost:8000** 으로 접속하면 캘린더가 표시됩니다.
 
원격 서버에 배포한 경우 **http://<서버-공인IP>:8000** 으로 접속하되, 서버의 방화벽(OS)과 **NCP ACG(Access Control Group)** 모두에서 8000번 포트 인바운드가 허용되어 있어야 합니다.
 
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
- **NCP ACG (Access Control Group)**: 콘솔 → Server → ACG → 해당 서버의 ACG → 인바운드 규칙에 **TCP 0.0.0.0/0 8000** 추가
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
