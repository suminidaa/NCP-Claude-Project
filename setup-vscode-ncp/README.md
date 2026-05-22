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


