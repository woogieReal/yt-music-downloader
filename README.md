# YouTube MP3 Downloader 🎵

Python으로 작성된 모던하고 깔끔한 CLI 기반 유튜브 오디오 다운로더입니다. `yt-dlp`를 활용하여 최고 음질의 오디오를 추출하고, `ffmpeg`를 통해 `192kbps`의 MP3 파일로 변환합니다. 또한 `Rich` 라이브러리를 사용하여 터미널 환경에서도 직관적이고 세련된 실시간 다운로드 UI를 제공합니다.

## ✨ 주요 기능

- **고음질 오디오 추출**: 자동으로 최상위 품질의 오디오 포맷을 다운로드하여 `192kbps` MP3로 자동 변환합니다.
- **ID3 태그 자동 입력**: `mutagen`을 사용하여 다운로드된 MP3 파일에 메타데이터를 자동으로 입력합니다. (Title, Artist, Album, Year, Track Number)
- **디렉터리 메타데이터(xattr) 저장**: 플레이리스트 다운로드 시, 해당 디렉터리 자체에 대표 아티스트(`user.artist`)와 최소 발매 연도(`user.year`)를 확장 속성으로 자동 기록합니다.
- **앨범 자켓 자동 삽입**: 유튜브 영상의 썸네일을 추출하여 다운로드된 MP3 파일에 앨범 자켓(표지 이미지)으로 자동 삽입합니다.
- **단일 영상 & 플레이리스트 지원**:
  - 단일 영상 다운로드 시 `download/제목.mp3` 형식으로 깔끔하게 저장됩니다.
  - 플레이리스트 다운로드 시 `download/` 하위에 **플레이리스트 제목**으로 폴더를 자동 생성하고, 그 안에 `1 - 제목.mp3` 형식으로 순번을 붙여 정리합니다.
- **Rich 터미널 UI**:
  - 다운로드를 시작하기 전, 추출될 트랙들의 정보를 요약된 표(Table) 형태로 미리 보여줍니다.
  - 플레이리스트 다운로드 시 이중 진행 바(전체 작업 진행률 + 현재 트랙 진행률)를 통해 예상 남은 시간(ETA), 속도, 퍼센티지 등을 실시간으로 표시합니다.
- **안정성 (견고한 예외 처리)**: 플레이리스트 내에 비공개 처리되거나 삭제되어 접근할 수 없는 영상이 있어도 프로그램이 멈추지 않고, 해당 곡만 건너뛴 후 나머지 곡들을 계속해서 안전하게 다운로드합니다.

---

## 🚀 설치 및 실행 방법

### 1. 사전 준비 사항

먼저 시스템에 **Python 3.12 이상** 버전과 **ffmpeg**가 설치되어 있어야 합니다.

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
python3 -m venv venv

# 가상 환경 활성화
# Linux / macOS:
source venv/bin/activate
# Windows (Git Bash / PowerShell):
# .\venv\Scripts\activate

# 의존성 패키지 리스트 설치
pip install -r requirements.txt
```

---

## 💻 사용 방법

가상 환경이 활성화된 상태에서, `main.py`에 다운로드할 유튜브 URL을 전달하여 실행합니다.

### 단일 영상 다운로드

```bash
python main.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
```

### 플레이리스트 다운로드

```bash
python main.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

### (New) 여러 개의 URL 일괄 다운로드

프로젝트 폴더 내에 `items.txt` 파일을 생성하고, 다운로드할 URL들을 한 줄씩 입력한 후, 매개변수 없이 `main.py`를 실행하세요.

1. `items.txt` 내용 예시:

```txt
https://music.youtube.com/playlist?list=OLAK5uy_lSogrSY4JibkASVaZt-QVeJ2TDMFrGREc&si=zcNOeoPV2le_d8bv
https://music.youtube.com/playlist?list=OLAK5uy_nwZ6zMHtubNwcxA5oWIwfMz7DDtjv7OtY&si=OKOwso8NjTeWskaE
```

1. 명령어 실행:

```bash
python main.py
```

### (New) ID3 태그 수동 수정

이미 다운로드된 MP3 파일 또는 디렉터리 내의 모든 MP3 파일에 대해 ID3 태그를 수동으로 입력하거나 수정하고 싶을 때 `edit_tags.py`를 사용합니다.

```bash
# 단일 파일 수정
python edit_tags.py "path/to/music.mp3" --artist="가수명" --album="앨범명" --year="2024"

# 디렉터리 내 모든 MP3 파일 일괄 수정
python edit_tags.py "path/to/album_directory" --artist="가수명" --album="앨범명" --year="2024"
```

- 인자로 전달한 태그(`--artist`, `--album`, `--year`)만 업데이트되며, 지정하지 않은 태그는 기존 값을 유지합니다.
- 디렉터리 경로를 입력하면 하위의 모든 `.mp3` 파일을 찾아 업데이트함과 동시에, **디렉터리 자체의 확장 속성(xattr)**에도 아티스트와 연도 정보를 동기화합니다.

---

*참고: 특수문자(`&` 등)로 인한 쉘 파싱 오류를 방지하기 위해 CLI에서 URL을 직접 입력할 때는 반드시 큰따옴표(`""`)로 감싸서 실행하는 것을 권장합니다.*
