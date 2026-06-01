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

## Part 1. NCP MCP 서버 설치

NCP MCP 서버를 사용하면 Claude에서 자연어만으로 NCP 서버·VPC·Object Storage를 조작할 수 있습니다.

> "rocky8.10으로 서버 하나 만들어줘" → Claude가 VPC·Subnet·ACG·Login Key·Server까지 한 번에 부트스트랩

### 1-1. 주요 기능

- **서버 관리** — 서버 목록 조회 · 상세 조회 · 생성 · 삭제
- **VPC 관리** — VPC · Subnet · Network ACL · ACG 생성/삭제
- **원클릭 부트스트랩** — `provision_server` 한 번으로 VPC + Subnet + ACG 규칙 + Login Key + Server 동시 생성
- **공인 IP 할당** — 서버에 공인 IP 부여
- **Object Storage** — 버킷 생성/삭제, 객체 업로드/다운로드/삭제, URL 발급 (boto3 기반 S3 호환 API)

### 1-2. 사전 준비

| 항목 | 요구사항 |
|---|---|
| Python | 3.10 이상 |
| NCP 계정 | [네이버 클라우드 플랫폼](https://www.ncloud.com) 가입 + Access Key 발급 |

#### NCP Access Key 발급

1. [NCP 콘솔](https://console.ncloud.com) 로그인
2. 우측 상단 '계정 클릭' → **계정 및 보안 관리** → **보안 관리** → **접근 관리** → **API 인증키**
3. **신규 API 인증키 생성** 클릭
4. Access Key ID / Secret Key를 안전한 곳에 보관 (Secret Key는 재조회 불가)

### 1-3. 저장소 클론 및 의존성 설치

**개인 PC의 터미널을 열고 저장소 클론 및 의존성 설치 진행**

```bash
git <repo url>
cd NCP-Claude-Project/ncp-mcp
```

```bash
pip install -r requirements.txt or pip3 install -r requirements.txt
```

> 💡 권장: 가상환경 사용
> ```bash
> python3 -m venv .venv
> source .venv/bin/activate    # Windows: .venv\Scripts\activate
> pip install -r requirements.txt
> ```

---

## Part 2. Claude에 NCP MCP 서버 등록

### 2-1. Claude Desktop (macOS)

설정 파일 위치: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
파일이 이미 생성되어 있는 경우 기존 파일의 내용 상단에 아래 내용을 추가합니다.

```json
{
  "mcpServers": {
    "ncp-server": {
      "command": "python3",
      "args": ["/절대/경로/NCP-Claude-Project/ncp-mcp/ncp_server.py"],
      "env": {
        "NCP_ACCESS_KEY": "your_access_key",
        "NCP_SECRET_KEY": "your_secret_key"
      }
    }
  }
}
```

이미 해당 파일에 내용이 있는 경우, 아래와 같이 반영

{
    "mcpServers": {
      "ncp-server": {
        "command": "python3",
        "args": ["/절대/경로/NCP-Claude-Project/ncp-mcp/ncp_server.py"],
        "env": {
          "NCP_ACCESS_KEY": "your_access_key",
          "NCP_SECRET_KEY": "your_secret_key"
        }
      }
    },
    "preferences": {
      "coworkScheduledTasksEnabled": true,
      "ccdScheduledTasksEnabled": true,
      "coworkWebSearchEnabled": true,
      "remoteToolsDeviceName": "XX",
      "epitaxyPrefs": {
        "starred-local-code-sessions": [],
        "starred-cowork-spaces": [],
        "starred-session-groups": [],
        "dframe-local-slice": {
          "pinnedOrder": [],
          "customGroupAssignments": {},
          "customGroupOrder": {}
        }
      },
      "bypassPermissionsGateByAccount": {
        "X": false
      }
    },
    "coworkUserFilesPath": "/Users/user/Claude"
  }


설정 후 **Claude Desktop을 완전히 종료 후 재시작**합니다.

### 2-2. Claude Desktop (Windows)

설정 파일 위치: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ncp-server": {
      "command": "python",
      "args": ["C:\\절대\\경로\\NCP-Claude-Project\\ncp-mcp\\ncp_server.py"],
      "env": {
        "NCP_ACCESS_KEY": "your_access_key",
        "NCP_SECRET_KEY": "your_secret_key"
      }
    }
  }
}
```

### 2-3. Claude Code에 MCP 등록

Claude Desktop에 이미 설정했다면 아래 두 가지 방법 중 하나를 사용합니다.

#### 방법 A. Claude Desktop 설정에서 가져오기 (Mac / WSL, 권장)

```bash
claude mcp add-from-claude-desktop
```

→ Claude Desktop에 등록된 모든 MCP 서버를 **환경변수(`env` 블록)까지 함께 복사**합니다.
Claude Desktop과 Claude Code에 동일한 키를 두 번 입력할 필요가 없어 가장 간편합니다.

> ⚠️ Windows 네이티브는 미지원입니다. Windows 사용자는 방법 B를 이용하세요.

#### 방법 B. 직접 등록

```bash
claude mcp add ncp-server \
  -e NCP_ACCESS_KEY=your_access_key \
  -e NCP_SECRET_KEY=your_secret_key \
  -- python3 /절대/경로/NCP-Claude-Project/ncp-mcp/ncp_server.py
```

→ `-e` 플래그로 환경변수를 함께 등록하면 셸 `export`가 필요 없습니다.

---

## Part 3. NCP MCP 서버 사용

### 3-1. 사용 예시

Claude에 다음과 같이 자연어로 요청하면 됩니다.

**Step 1.** provision_server로 web-dev 만들어줘.

서버 생성이 완료되었다고 Claude가 답하면 NCP 콘솔에서 완료 여부를 확인합니다.

**Step 2.** web-dev 서버에 public ip도 부여해줘.

### 3-2. 자주 쓰는 값

#### OS 이미지 alias

| alias | 풀 코드 |
|---|---|
| `rocky8.8` | `SW.VSVR.OS.LNX64.ROCKY.0808.B050` |
| `rocky8.10` | `SW.VSVR.OS.LNX64.ROCKY.0810.B050` |

#### 서버 스펙 alias (Standard G2)

| alias | vCPU / 메모리 |
|---|---|
| `s2-g2` | 2 vCPU / 8 GB |
| `s4-g2` | 4 vCPU / 16 GB |
| `s8-g2` | 8 vCPU / 32 GB |
| `s16-g2` | 16 vCPU / 64 GB |
| `s32-g2` | 32 vCPU / 128 GB |

#### 리전 코드

`KR` (기본) · `SGN` · `JPN` · `USWN`

### 3-3. `provision_server` 파라미터 기본값

`provision_server`는 VPC + Subnet + ACG 규칙 + Login Key + Server를 한 번에 부트스트랩하는 핵심 함수입니다. **`server_name` 하나만 지정해도 동작**합니다.

| 파라미터 | 디폴트 값 | 설명 |
|---|---|---|
| `server_name` | **(필수)** | 서버 이름 (3~30자). 다른 자원 이름의 기본값으로도 재사용됨 |
| `image` | `rocky8.10` | OS 이미지 alias |
| `spec` | `s2-g2` | 서버 스펙 alias (2 vCPU / 8 GB) |
| `vpc_name` | `{server_name}-vpc` | 빈 값이면 서버 이름 뒤에 `-vpc` 자동 부여 |
| `vpc_cidr` | `10.0.0.0/16` | 신규 VPC 생성 시 사용 (재사용 시 무시) |
| `subnet_name` | `{server_name}-subnet` | 빈 값이면 서버 이름 뒤에 `-subnet` 자동 부여 |
| `subnet_cidr` | `10.0.1.0/24` | 신규 Subnet 생성 시 사용 (재사용 시 무시) |
| `zone_code` | `KR-2` | Subnet Zone (`KR-1` 또는 `KR-2`) |
| `login_key_name` | `server_name` 값 그대로 | 빈 값이면 서버 이름과 동일하게 설정 |
| `region_code` | `KR` | 리전 (`KR` · `SGN` · `JPN` · `USWN`) |

#### 함수 내부 고정 설정

**ACG 인바운드 규칙**

| 프로토콜 | 출발지 | 포트 | 용도 |
|---|---|---|---|
| TCP | 내 공인 IP (`myip/32`) | 22 | SSH |
| TCP | 내 공인 IP (`myip/32`) | 3389 | RDP |
| TCP | `0.0.0.0/0` | 80 | HTTP (전체 공개) |

**ACG 아웃바운드 규칙**

| 프로토콜 | 목적지 | 포트 |
|---|---|---|
| TCP | `0.0.0.0/0` | 1-65535 |
| UDP | `0.0.0.0/0` | 1-65535 |
| ICMP | `0.0.0.0/0` | 전체 |

**Login Key 저장**
- 저장 경로: `~/Downloads/{login_key_name}.pem`
- 동일 이름 pem 파일이 이미 있으면 **재사용**, 없으면 신규 발급 후 `chmod 600`

#### 동작 특성

1. **멱등성** — 같은 이름의 VPC / Subnet / Login Key가 있으면 그대로 재사용
2. **공인 IP 미포함** — 서버가 RUN 상태가 된 뒤 `assign_public_ip`를 별도 호출해야 함
3. **RUN 대기 안 함** — 서버 생성 요청 직후 바로 반환 (VPC/Subnet은 RUN까지 최대 90초 대기)

#### 사용 예시

```python
# 최소 입력 — 모든 디폴트 사용
provision_server(server_name="demo")

# 스펙·이미지 변경
provision_server(server_name="prod-api", image="rocky8.8", spec="s4-g2")

# 다른 리전 / Zone
provision_server(server_name="sg-app", region_code="SGN", zone_code="KR-1")
```

### 3-4. 문제 해결

| 증상 | 해결 |
|---|---|
| HTTP 401 | `NCP_ACCESS_KEY` / `NCP_SECRET_KEY` 값 확인 |
| HTTP 400 | `vpcNo` · `subnetNo` 값이 유효한지 확인 |
| 서버 삭제 실패 | NSTOP(정지) 상태여야 삭제 가능 |
| Claude에서 툴이 안 보임 | Claude Desktop 완전 종료 후 재시작 |
| `ModuleNotFoundError: No module named 'mcp'` | `pip install -r requirements.txt` 재실행 |
| `boto3 미설치` 안내 | Object Storage 사용 시 `pip install boto3` |

### 3-5. 보안 주의사항

- **`.env`, `*.pem` 파일은 절대 git에 커밋하지 마세요** (`.gitignore`로 차단되어 있음)
- Access Key가 노출되면 즉시 NCP 콘솔에서 재발급
- 공유 PC에서는 환경변수 대신 OS 시크릿 매니저 사용 권장

---

## Part 4. VS Code 설치

Visual Studio Code(VS Code)는 Microsoft가 만든 무료 코드 에디터입니다. 가볍고 빠르며, 다양한 확장을 통해 거의 모든 개발 환경을 지원합니다.

### 4-1. 다운로드

1. 브라우저로 [https://code.visualstudio.com](https://code.visualstudio.com) 접속
2. 큰 파란색 **[Download]** 버튼 클릭
3. 운영체제가 자동 감지되어 적절한 설치 파일이 다운로드됩니다.

### 4-2. 설치

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

## Part 5. Claude Code 설치 및 VS Code 연동

Claude Code는 터미널에서 동작하는 Anthropic 공식 AI 코딩 도구입니다. VS Code 확장을 함께 설치하면 에디터에서 코드 변경사항을 실시간으로 확인할 수 있습니다.

### 5-1. Claude Code 설치

1. VS Code → **Extensions** (`Ctrl+Shift+X`)
2. 검색창에 `Claude Code` 입력
3. **"Claude Code for VSCode"** (Anthropic 공식) → **[설치]** 클릭

### 5-2. Claude Code 로그인

1. **Claude.ai Subscription** 클릭
2. 브라우저가 열리면서 Anthropic 로그인 페이지로 이동
3. 로그인 진행
4. 인증 완료 후 터미널로 돌아오면 Claude Code 프롬프트가 표시됩니다.

### 5-3. 연동 확인

1. 아무 폴더든 VS Code로 엽니다.
2. 우측 상단의 **Claude 로고**를 선택합니다.
3. Claude 실행창이 열리는지 확인합니다.

---

## Part 6. Remote-SSH 확장 설치

Remote-SSH는 SSH로 원격 서버에 접속해, 로컬 VS Code 창에서 원격 서버의 파일을 직접 편집할 수 있게 해주는 Microsoft 공식 확장입니다.

### 6-1. 확장 설치

1. VS Code 왼쪽 사이드바에서 **Extensions 아이콘** (네모 4개) 클릭
2. 검색창에 `Remote - SSH` 입력
3. **"Remote - SSH"** (Microsoft 발행, 파란색 인증 마크 확인) → **[설치]** 클릭
4. 함께 설치되는 **"Remote - SSH: Editing Configuration Files"**도 자동 설치됩니다.

### 6-2. 설치 확인

왼쪽 사이드바 가장 아래쪽에 `><` 모양 아이콘(Remote Explorer)이 생기면 정상입니다.


---

## Part 7. SSH 키와 config 준비

Remote-SSH로 NCP 서버에 접속하려면 두 가지가 필요합니다:

1. 서버용 SSH 개인 키 파일 (`.pem`)
2. SSH 설정 파일 (`~/.ssh/config`)

### 7-1. SSH 키 위치 확인

`provision_server`로 NCP 서버를 만들었다면 다운로드 폴더에 `{서버이름}.pem` 파일이 자동 생성되어 있습니다.

> 예: `web-dev`라는 이름으로 서버를 만들었다면 다운로드 폴더에 `web-dev.pem` 파일이 있어야 합니다.

### 7-2. 서버 공인 IP 확인

1. NCP 콘솔 → ** Computee→ Server**
2. 해당 서버의 **"공인 IP"** 컬럼 값을 메모합니다.
3. 또는 Claude Desktop에서 `"내 NCP 서버 목록 보여줘"`로도 확인 가능합니다.

### 7-3. SSH 비밀번호 초기화 (Rocky Linux)

NCP는 처음 생성된 서버에 대해 콘솔에서 "관리자 비밀번호 확인" 절차를 거쳐야 SSH 접속이 가능합니다.

1. NCP 콘솔 → **Server** → 해당 서버 선택
2. 상단 **[서버 관리 및 설정 변경]** → **[관리자 비밀번호 확인]** 클릭
3. 본인이 만든 키 파일(`.pem`) 업로드
4. `root` 계정의 초기 비밀번호가 표시됨 → 메모

> Remote-SSH는 키 기반 접속을 우선 사용하므로, NCP가 부여한 비밀번호 대신 `.pem` 키로 접속합니다. 비밀번호 확인 단계는 콘솔의 안전 장치일 뿐입니다.

### 7-4. SSH config 파일 작성

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

### 7-5. config 파일 권한

```bash
chmod 600 ~/.ssh/config
```

---

## Part 8. VS Code에서 NCP 서버에 접속

### 8-1. 접속 시작

1. VS Code 좌측 하단의 **`><` 모양 버튼** 클릭 (또는 `F1` → `Remote-SSH: Connect to Host`)
2. 드롭다운에서 방금 등록한 별칭(예: `ncp-web-dev`) 선택
3. `root`에 대한 비밀번호 요구 시 콘솔 화면에서 확인한 `root` 패스워드 기입

### 8-2. 연결 확인

새 창의 좌측 하단에 `SSH: ncp-web-dev` 같은 표시가 보이면 정상 접속된 것입니다.
