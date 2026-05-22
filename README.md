# 🚀 NCP + Claude Code 실습 워크샵

> **네이버 클라우드 플랫폼(NCP)** 위에 **VS Code + Claude Code**로 실제 웹 서비스 두 개를 직접 만들어보는 실습 가이드입니다.
>
> 클라우드/AI 코딩 도구를 처음 써보시는 분도 **위에서부터 순서대로** 따라하시면 완성할 수 있도록 구성했습니다.

---

## 📁 폴더 구조와 각 폴더의 역할

```
ncp-claudecode/
├─ setup-vscode-ncp/   # 🛠️  [STEP 1] 개발 환경 세팅 가이드
├─ diary-app/          # 🌸  [STEP 2] 실습 1 - 다이어리 웹앱 (Object Storage 입문)
├─ budget-app/         # 💰  [STEP 3] 실습 2 - 가계부 웹앱 (Object Storage + CLOVA OCR)
└─ README.md           # 📖  현재 보고 있는 전체 안내 문서
```

### 1) `setup-vscode-ncp/` — 개발 환경 세팅 🛠️

| 항목 | 내용 |
|---|---|
| **목적** | 실습을 위한 **VS Code, Claude Code, Remote-SSH** 설치 및 NCP 서버 원격 접속 |
| **핵심 내용** | VS Code 설치 → Claude Code 확장 설치/로그인 → Remote-SSH 확장 설치 → SSH 키·config 준비 → NCP 서버 접속 |
| **결과물** | VS Code에서 NCP 클라우드 서버에 SSH로 접속한 상태 (이후 모든 실습이 이 서버 위에서 진행됨) |

> 💡 **이 단계를 가장 먼저** 진행해야 합니다. 이후 실습은 모두 여기서 만든 서버에서 동작합니다.

### 2) `diary-app/` — 실습 1: 나의 다이어리 🌸

| 항목 | 내용 |
|---|---|
| **목적** | **NCP Object Storage**의 기본기를 익히기 (S3 호환 파일 저장소 사용) |
| **기술 스택** | FastAPI · NCP Object Storage · Jinja2 · boto3 |
| **핵심 기능** | 월간 캘린더 + 텍스트 일기 + 사진 업로드 + 분위기 이모지 |
| **사용 포트** | `8000` |
| **난이도** | ⭐⭐ (입문) |

### 3) `budget-app/` — 실습 2: 나의 가계부 💰

| 항목 | 내용 |
|---|---|
| **목적** | **Object Storage + CLOVA OCR**을 함께 연동해 더 실전적인 서비스를 구성 |
| **기술 스택** | FastAPI · NCP Object Storage · **NCP CLOVA OCR** · Chart.js · boto3 |
| **핵심 기능** | 영수증 사진 업로드 → OCR로 금액·상점 자동 추출 → 월별 예산/소비 차트 |
| **사용 포트** | `8001` |
| **난이도** | ⭐⭐⭐ (다이어리보다 한 단계 심화) |

> 💡 다이어리 → 가계부 순서로 진행하시면 코드 구조가 비슷해서 학습 곡선이 완만합니다.

---

## 🗺️ 실행 순서 (반드시 위에서 아래로!)

```
[STEP 1] setup-vscode-ncp 의 README 따라하기
              │
              ▼
       VS Code + Claude Code + Remote-SSH 설치
              │
              ▼
       NCP 콘솔에서 서버 생성 + 공인 IP 확보
              │
              ▼
       VS Code에서 SSH로 NCP 서버 접속
              │
              ▼
[STEP 2] diary-app 의 README 따라하기
              │
              ▼
       NCP Object Storage 버킷 생성 + API 키 발급
              │
              ▼
       서버에서 git clone → .env 설정 → ./run.sh 실행
              │
              ▼
       브라우저에서 http://<공인IP>:8000 접속 확인
              │
              ▼
[STEP 3] budget-app 의 README 따라하기
              │
              ▼
       NCP CLOVA OCR 도메인 생성 + 템플릿 배포
              │
              ▼
       서버에서 .env 설정 → ./run.sh 실행
              │
              ▼
       브라우저에서 http://<공인IP>:8001 접속 확인 🎉
```

각 단계의 **상세 가이드**는 해당 폴더의 `README.md`에 있습니다. 위 흐름을 그대로 따라가면서 각 폴더의 README를 펼쳐보세요.

---

## ✅ 사전 준비물 체크리스트

실습을 시작하기 전에 아래 항목을 준비해 주세요.

| # | 준비물 | 비고 |
|---|---|---|
| 1 | **PC (macOS / Windows)** | VS Code가 설치 가능한 환경 |
| 2 | **NCP 계정** | [ncloud.com](https://www.ncloud.com) 가입 (신용카드 등록 필요, 무료 한도 제공) |
| 3 | **Claude 유료 구독** | Claude Code는 **무료 플랜 사용 불가** — Pro($20/월) 이상 또는 API 크레딧 필요 |
| 4 | **인터넷 연결** | NCP 콘솔 + Claude.ai 접속용 |
| 5 | **Git 기본 사용 경험** | `clone`, `pull` 정도면 충분 |

> 💳 NCP는 사용량 기반 과금입니다. 실습 종료 후에는 **서버를 반드시 반납(정지·삭제)** 하여 비용 발생을 막아주세요.

---

## ⚡ 빠른 시작 (요약 버전)

이미 환경 세팅을 마치신 분을 위한 요약입니다. 처음 진행하신다면 **위의 실행 순서대로** 각 폴더 README를 펼쳐보세요.

```bash
# 1. NCP 서버에 SSH 접속 후, 이 저장소를 클론
git clone <repo url>
cd NCP-Claude-Project

# 2. 다이어리 앱 실행
cd diary-app
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # .env 파일 편집 후 NCP 키 입력
./run.sh                   # http://<공인IP>:8000

# 3. 가계부 앱 실행 (별도 터미널에서)
cd ../budget-app
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # .env 파일 편집 후 NCP 키 + Object Storage 버킷 명 + OCR 정보 입력
./run.sh                   # http://<공인IP>:8001
```

> ⚠️ 외부 접속을 위해 **NCP 콘솔 → Server → ACG**에서 해당 포트(8000, 8001)에 대해 **TCP MyIP 인바운드**를 허용해야 합니다.

---

## 🤔 자주 묻는 질문 (FAQ)

### Q1. 꼭 NCP 클라우드 서버에서 돌려야 하나요? 내 PC에서 해도 되나요?
- **내 PC에서도 가능**하지만, 이 워크샵은 **클라우드 환경 체험**이 목적이므로 NCP 서버에서 진행하는 것을 권장합니다.
- 단, NCP Object Storage와 CLOVA OCR은 외부에서도 호출 가능하므로 로컬에서 실행해도 동작은 합니다.

### Q2. Claude Code 없이도 이 실습을 따라할 수 있나요?
- 코드는 이미 완성되어 있으니 **Claude Code 없이도 실행만은 가능**합니다.
- 하지만 코드를 수정·확장하거나 트러블슈팅을 할 때 Claude Code가 큰 도움이 되므로 설치를 권장합니다.

### Q3. 다이어리/가계부 앱이 동시에 실행되나요?
- 네. **포트가 8000(diary)과 8001(budget)으로 다르기 때문에** 동시에 실행 가능합니다.
- ACG에서 두 포트를 모두 열어주세요.

### Q4. 비용이 얼마나 나오나요?
- **NCP Compute**: 서버 사양마다 다르지만 Standard 2vCPU,8GBmemory, SSD기준 월 88,000원의 요금이 발생할 수 있습니다. 상세 요금은 네이버클라우드플랫폼 요금계산기(https://www.ncloud.com/charge/calc/ko)를 확인해주세요.
- **NCP Object Storage**: 무료 한도 안에서 충분히 실습 가능
- **NCP CLOVA OCR Basic 플랜**: 월 300건 호출까지 무료
- 💡 **실습이 끝나면 반드시 서버 정지·삭제**로 비용을 막아주세요.

### Q5. 에러가 났을 때 어디를 봐야 하나요?
1. 각 폴더(`diary-app`, `budget-app`)의 **README 하단 트러블슈팅 섹션**을 먼저 확인
2. NCP 콘솔에서 ACG/방화벽/버킷 권한 점검
3. `.env` 파일의 키 값 오타 점검 (가장 흔한 원인!)
4. Claude Code에게 에러 메시지를 직접 붙여넣고 물어보기

---

## 📚 참고 링크

| 분류 | 링크 |
|---|---|
| NCP 콘솔 | https://console.ncloud.com |
| NCP 사용 가이드 | https://guide.ncloud-docs.com |
| Claude Code 공식 문서 | https://docs.claude.com/claude-code |
| VS Code | https://code.visualstudio.com |
| FastAPI 공식 문서 | https://fastapi.tiangolo.com |

---

## 🔒 보안 주의사항

- **`.env` 파일을 절대 git에 커밋하지 마세요.** NCP Access Key, Secret Key, OCR Secret Key가 포함됩니다. 각 폴더의 `.gitignore`에 등록되어 있어 기본적으로는 자동으로 제외됩니다.
- API 키 노출 의심 시 **즉시 NCP 콘솔에서 폐기·재발급**하세요.
- 실습용 앱에는 **인증 기능이 없으므로** 외부 노출 시 IP 제한 또는 리버스 프록시(Basic Auth)로 보호하세요.

---

## 📜 라이선스

MIT License — 자유롭게 fork / 수정 / 배포하세요.

---

## 🙋 도움이 더 필요하신가요?

- 각 폴더 안에 **세부 가이드 README**가 있습니다. 먼저 그쪽부터 확인해 주세요.
- 추가 질문은 이슈로 등록하거나, VS Code 안에서 **Claude Code에게 직접 물어보세요** — 워크샵에서 익힌 가장 강력한 도구입니다 🤖✨
