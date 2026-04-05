# Google GenAI Search Grounding Test

이 프로젝트는 최신 `google-genai` Python SDK를 사용하여 **Google Search Grounding(구글 검색 그라운딩)** 기능을 테스트하고, 특히 LLM이 과거 데이터가 아닌 **최신 정보(Freshness)만을 기반으로 답변하도록 강제**하는 방법을 시연합니다.

## 💡 핵심 아이디어 (Core Idea)

Vertex AI 엔드포인트는 백엔드 API에서 검색 기간을 제한하는 `time_range_filter` 파라미터를 현재 제공하지 않습니다. 이 제약을 우회하여 완벽한 "최신성(Freshness)"을 보장하기 위해 본 프로젝트는 다음과 같은 아키텍처를 사용합니다.

1. **검색 연산자(Operator) 강제 주입:** `System Instruction`을 사용하여 LLM에게 지시를 내립니다. 모델이 검색 쿼리를 스스로 작성할 때, `after:YYYY-MM-DD` (예: `after:2026-04-02`) 형태의 구글 검색 연산자를 무조건 덧붙이도록 세뇌시킵니다.
2. **Google 검색 엔진의 강력한 필터링:** 쿼리에 포함된 `after:` 연산자를 구글 검색 엔진이 직접 해석하여, 지정된 날짜 이전의 낡은 뉴스나 문서를 1차적으로 완전히 차단합니다.
3. **최신 데이터 기반 Grounding:** 모델은 구글 검색 엔진이 엄선해 준 최신 문서(Chunks)만을 바탕으로 최종 답변을 합성하므로, 과거 데이터로 인한 할루시네이션(Hallucination)이 원천 차단됩니다.

## 📌 주요 파일 설명

이 저장소는 Google Cloud의 Vertex AI 환경에 맞춘 테스트 스크립트를 포함합니다.

### `run_grounding_test.py` (Vertex AI 전용)
* **목적:** Google Cloud의 Vertex AI 엔드포인트를 사용하여 최신 검색 결과를 가져옵니다.
* **핵심 원리:** Vertex AI 백엔드는 현재 SDK 상에서 직접적인 시간 필터(`time_range_filter`)를 지원하지 않습니다. 이를 극복하기 위해 **시스템 인스트럭션(System Instruction)**을 사용하여 모델이 자체적으로 검색 쿼리를 생성할 때 `after:YYYY-MM-DD` 연산자를 무조건 포함하도록 강제합니다.
* **인증:** Google Cloud ADC (`gcloud auth application-default login`)가 필요합니다.

### `run_test.sh`
* 테스트 스크립트를 간편하게 실행하기 위한 쉘 스크립트입니다.

## 🚀 요구 사항 (Requirements)

```bash
pip install google-genai google-auth
```

## 💡 실행 방법

**Vertex AI 테스트:**

스크립트 실행 시 `--query` (또는 `-q`) 와 `--days` (또는 `-d`) 옵션을 통해 동적으로 검색어와 최신성 기준(며칠 전)을 설정할 수 있습니다.

```bash
# 기본 실행 (삼성전자, 최근 3일)
python3 run_grounding_test.py

# 커스텀 실행 (예: 엔비디아 주가, 최근 1일)
python3 run_grounding_test.py -q "엔비디아 주가 동향" -d 1
```

## 🔍 출력 결과 (메타데이터 로깅)

이 스크립트는 단순히 LLM의 답변만 출력하는 것이 아니라, 응답에 포함된 **Grounding Metadata**를 파싱하여 아래 정보를 로깅합니다.
1. 모델이 실제로 검색 엔진에 질의한 쿼리 원문 (예: `['삼성전자 최신 소식 after:2026-04-02']`)
2. 검색 결과로 참조한 실제 웹 문서(Chunks)의 제목과 URL 링크

## 📝 실행 샘플 (Sample Output)

```text
==================================================
🚀 테스트 시작: Vertex AI - Grounding with Google Search
✅ 프로젝트: jwlee-argolis-202104 (global)
==================================================
생성된 프롬프트: 삼성전자 최신 소식 알려줘 after:2026-04-02

[gemini-3.1-flash-lite-preview] 모델에 요청을 보내는 중 (약간의 시간이 소요될 수 있습니다)...

==================================================
✨ [최종 응답 결과]
==================================================
2026년 4월 2일 이후 확인된 삼성전자의 주요 소식은 다음과 같습니다.

1. 1분기 잠정 실적 발표 예정 (4월 7일)
*   삼성전자는 오는 4월 7일 2026년 1분기 잠정 실적을 발표할 예정입니다. 시장에서는 반도체 업황 개선에 힘입어 삼성전자가 매우 강력한 실적을 기록할 것으로 기대하고 있습니다.

2. DS부문 '2026년 상생협력 DAY' 개최 (4월 3일)
*   삼성전자 DS(반도체)부문은 협력회사와의 동반 성장을 도모하기 위해 '2026년 상생협력 DAY'를 개최했습니다. 

요약하자면, 삼성전자는 현재 반도체 부문의 호황을 바탕으로 1분기 사상 최대 수준의 실적 발표를 앞두고 있으며, 협력사와의 상생 경영을 강화하는 한편 AI 인프라 시장에서의 주도권 확보를 위한 대규모 투자를 지속하고 있습니다.
==================================================

==================================================
🔍 [내부 검색 로그 (Grounding Metadata)]
==================================================
1. 사용된 Google 검색어 (webSearchQueries):
   원본 리스트: ['삼성전자 최신 소식 after:2026-04-02']

   💡 [UI 디스플레이 규정 시뮬레이션: Search Suggestion 칩]
   (사용자가 직접 클릭하여 Google 검색 결과를 확인할 수 있도록 제공해야 함)
   [1] 검색어: '삼성전자 최신 소식 after:2026-04-02'
       👉 Google 검색 결과 확인: https://www.google.com/search?q=%EC%82%BC%EC%84%B1%EC%A0%84%EC%9E%90%20%EC%B5%9C%EC%8B%A0%20%EC%86%8C%EC%8B%9D%20after%3A2026-04-02

2. 검색해서 읽어온 문서(Chunks) 목록:
   [1] choicenews.co.kr
       URL: https://vertexaisearch.cloud.google.com/grounding-api-redirect/...
   [2] dt.co.kr
       URL: https://vertexaisearch.cloud.google.com/grounding-api-redirect/...
```
