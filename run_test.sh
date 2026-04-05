#!/bin/bash

echo "==============================================="
echo "1. uv로 파이썬 가상환경(test_env) 생성 중..."
echo "==============================================="
rm -rf test_env
uv venv test_env

echo -e "\n==============================================="
echo "2. 가상환경 활성화 및 패키지 설치 중..."
echo "==============================================="
source test_env/bin/activate
uv pip install --index-url https://pypi.org/simple/ google-genai google-auth pyopenssl

echo -e "\n==============================================="
echo "3. Vertex AI Grounding 테스트 스크립트 실행 중..."
echo "==============================================="
python3 run_grounding_test.py

echo -e "\n==============================================="
echo "4. 가상환경 종료"
echo "==============================================="
deactivate
