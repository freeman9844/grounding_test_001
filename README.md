# Google GenAI Search Grounding Test

이 프로젝트는 최신 `google-genai` Python SDK를 사용하여 **Google Search Grounding(구글 검색 그라운딩)** 기능을 테스트하고, 특히 LLM이 과거 데이터가 아닌 **최신 정보(Freshness)만을 기반으로 답변하도록 강제**하는 방법을 시연합니다.

## 📌 주요 파일 설명

이 저장소에는 두 가지 환경(Vertex AI, AI Studio)에 맞춘 테스트 스크립트가 포함되어 있습니다.

### 1. `run_grounding_test.py` (Vertex AI 전용)
* **목적:** Google Cloud의 Vertex AI 엔드포인트를 사용하여 최신 검색 결과를 가져옵니다.
* **핵심 원리:** Vertex AI 백엔드는 현재 SDK 상에서 직접적인 시간 필터(`time_range_filter`)를 지원하지 않습니다. 이를 극복하기 위해 **시스템 인스트럭션(System Instruction)**을 사용하여 모델이 자체적으로 검색 쿼리를 생성할 때 `after:YYYY-MM-DD` 연산자를 무조건 포함하도록 강제합니다.
* **인증:** Google Cloud ADC (`gcloud auth application-default login`)가 필요합니다.

### 2. `search_grounding_test.py` (Google AI Studio 전용)
* **목적:** 일반 Gemini API(AI Studio) 환경에서 최신 검색 결과를 가져옵니다.
* **핵심 원리:** AI Studio 환경에서는 SDK가 제공하는 `time_range_filter` 파라미터를 사용하여 `types.Interval` 객체로 직접 검색 기간을 제한할 수 있습니다.
* **인증:** `GEMINI_API_KEY` 환경변수가 필요합니다.

### 3. `run_test.sh`
* 테스트 스크립트를 간편하게 실행하기 위한 쉘 스크립트입니다.

## 🚀 요구 사항 (Requirements)

```bash
pip install google-genai google-auth
```

## 💡 실행 방법

**Vertex AI 테스트:**
```bash
python3 run_grounding_test.py
```

**AI Studio 테스트:**
```bash
export GEMINI_API_KEY="your_api_key"
python3 search_grounding_test.py
```

## 🔍 출력 결과 (메타데이터 로깅)

두 스크립트 모두 단순히 LLM의 답변만 출력하는 것이 아니라, 응답에 포함된 **Grounding Metadata**를 파싱하여 아래 정보를 로깅합니다.
1. 모델이 실제로 검색 엔진에 질의한 쿼리 원문 (예: `['삼성전자 최신 소식 after:2026-04-02']`)
2. 검색 결과로 참조한 실제 웹 문서(Chunks)의 제목과 URL 링크
