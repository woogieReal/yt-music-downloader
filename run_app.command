#!/bin/bash

# 현재 스크립트가 위치한 디렉토리로 이동
cd -- "$(dirname "$0")"

# 가상환경 경로 설정
VENV_PATH="./.venv"

# 가상환경이 존재하는지 확인
if [ -d "$VENV_PATH" ]; then
    echo "가상환경을 활성화하는 중..."
    source "$VENV_PATH/bin/activate"
else
    echo "오류: 가상환경($VENV_PATH)을 찾을 수 없습니다."
    echo "의존성 설치가 완료되었는지 확인해주세요."
    read -p "종료하려면 엔터를 누르세요..."
    exit 1
fi

echo "YouTube Music Downloader를 시작합니다..."
# 앱 실행
python main.py

# 프로그램 종료 후 터미널이 바로 닫히지 않도록 대기 (선택 사항)
# read -p "종료하려면 엔터를 누르세요..."
