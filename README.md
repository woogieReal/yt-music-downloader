# YouTube MP3 Downloader 🎵

Python으로 작성된 모던하고 깔끔한 CLI/TUI 기반 유튜브 오디오 다운로더입니다. `yt-dlp`를 활용하여 최고 음질의 오디오를 추출하고, `ffmpeg`를 통해 `192kbps`의 MP3 파일로 변환합니다. `Textual`과 `Rich` 라이브러리를 사용하여 터미널 환경에서도 직관적이고 세련된 인터랙티브 UI(TUI)를 제공합니다.

## ✨ 주요 기능

- **강력한 터미널 사용자 인터페이스(TUI)**: 명령어뿐만 아니라 화려한 대화형 TUI를 제공합니다. 다운로드 URL 입력, 커스텀 이미지 설정, 메타데이터 수동 입력 등을 화면 안에서 직관적으로 조작할 수 있습니다.
- **고음질 오디오 추출**: 자동으로 최상위 품질의 오디오 포맷을 다운로드하여 `192kbps` MP3로 자동 변환합니다.
- **ID3 태그 및 메타데이터 관리**:
  - `mutagen`을 사용하여 다운로드된 MP3 파일에 메타데이터(Title, Artist, Album, Year, Track Number)를 자동으로 입력합니다.
  - **수동 메타데이터 입력**: 다운로드 시 아티스트, 앨범명, 발매 연도를 직접 입력해 일괄 적용할 수 있습니다.
- **앨범 자켓 커스터마이징**:
  - 유튜브 영상의 썸네일을 추출하여 앨범 자켓으로 자동 삽입합니다.
  - **커스텀 앨범 자켓 지원**: 웹상의 이미지 URL이나 로컬 이미지 파일 경로를 입력해 원하는 사진으로 커버 아트를 변경할 수 있습니다. (WSL 환경 경로 변환 완벽 호환)
  - **플레이리스트 커버 통일**: 플레이리스트 다운로드 시, 대표 썸네일을 모든 트랙의 앨범 자켓으로 일괄 적용하는 옵션이 지원됩니다.
- **디렉터리 메타데이터(xattr) 저장**: 플레이리스트 다운로드 시 디렉터리 자체에 대표 아티스트(`user.artist`)와 최소 발매 연도(`user.year`)를 확장 속성으로 자동 기록합니다.
- **단일 영상 & 플레이리스트 지원**:
  - 단일 영상: `download/제목.mp3` 형식으로 저장됩니다.
  - 플레이리스트: `download/` 하위에 **플레이리스트 제목**으로 폴더를 생성하고, `1 - 제목.mp3` 형식으로 정리합니다.
- **안정성 유지 (견고한 예외 처리)**: 플레이리스트 내 접근 불가능한 비공개/삭제 영상이 있어도 다운로드가 멈추지 않고 건너뛴 후 안전하게 계속 진행됩니다.

---

## 🚀 설치 및 실행 방법

### 1. 사전 준비 사항

방문한 시스템에 **Python 3.8 이상** 버전과 **ffmpeg**가 설치되어 있어야 합니다.

**Ubuntu / Debian 환경:**

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip ffmpeg
```

**macOS (Homebrew) 환경:**

```bash
brew install ffmpeg python
```

### 2. 저장소 클론(Clone)

```bash
git clone https://github.com/woogieReal/yt-music-downloader.git
cd yt-music-downloader
```

### 3. 가상 환경 설정 및 패키지 설치

```bash
# 가상 환경(venv) 생성
python3 -m venv .venv

# 가상 환경 활성화
# Linux / macOS:
source .venv/bin/activate
# Windows (Git Bash / PowerShell):
# .\.venv\Scripts\activate

# 의존성 패키지 리스트 설치
pip install -r requirements.txt
```

---

## 💻 사용 방법

가장 추천하는 방법은 `TUI 모드`를 사용하는 것입니다.

### 터미널 UI (TUI) 모드 - 강력 추천!

URL 없이 스크립트를 실행하면 대화형 TUI 창이 열립니다.

```bash
python main.py
```
> URL을 직접 입력하고 커스텀 기능(메타데이터, 앨범 자켓)을 체크박스를 통해 손쉽게 활성화할 수 있습니다.

### 간편 실행 스크립트 (macOS / Linux)

가상 환경 활성화와 프로그램 실행을 한 번에 처리해주는 스크립트를 제공합니다. 더블클릭이나 터미널 실행 모두 가능합니다.

```bash
./run_app.command
```

### CLI 자동 모드 (단일 영상 & 플레이리스트)

URL을 직접 인자로 전달하면 UI 과정을 건너뛰고 바로 터미널에서 다운로드가 시작됩니다. 자동화나 스크립트 사용 시 유용합니다.

```bash
# 단일 영상
python main.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"

# 플레이리스트
python main.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

### ID3 태그 스크립트로 수동 관리 (`edit_tags.py`)

다운로드된 파일 또는 디렉터리의 ID3 태그를 개별/일괄적으로 수정하고 싶을 때 사용할 수 있는 유틸리티 스크립트입니다.

```bash
# 단일 파일 수정
python edit_tags.py "path/to/music.mp3" --artist="가수명" --album="앨범명" --year="2024"

# 디렉터리 내 모든 MP3 파일 일괄 수정 (xattr 자동 동기화 포함)
python edit_tags.py "path/to/album_directory" --artist="가수명" --album="앨범명" --year="2024"
```

---

*참고: 특수문자(`&` 등)로 인한 쉘 파싱 오류를 방지하기 위해 CLI에서 파라미터로 URL을 넘길 때는 반드시 큰따옴표(`""`)로 감싸서 실행하는 것을 권장합니다.*
