import os
from datetime import datetime, timedelta
from google import genai
from google.genai import types

def main():
    # 1. 3일 전 날짜 계산 (YYYY-MM-DD 형식)
    three_days_ago = datetime.now() - timedelta(days=3)
    date_str = three_days_ago.strftime("%Y-%m-%d")

    # 2. 프롬프트 구성 (after: 연산자 포함)
    query = f"삼성전자 최신 소식 알려줘 after:{date_str}"
    print(f"생성된 프롬프트: {query}\n")

    # 3. Gemini 클라이언트 초기화 (GEMINI_API_KEY 환경변수 필요)
    try:
        client = genai.Client()
    except Exception as e:
         print(f"클라이언트 초기화 실패: {e}")
         print("GEMINI_API_KEY 환경 변수가 설정되어 있는지 확인하세요.")
         return

    # 4. 모델 호출 (Grounding with Google Search 활성화)
    model_name = "gemini-3.1-flash-lite-preview"
    print(f"[{model_name}] 모델에 요청을 보내는 중...\n")

    try:
        # Google Search Tool 활성화 (기간 필터 추가 - AI Studio 전용 기능)
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch(
                time_range_filter=types.Interval(
                    start_time=three_days_ago
                )
            )
        )

        response = client.models.generate_content(
            model=model_name,
            contents=query,
            config=types.GenerateContentConfig(
                tools=[google_search_tool],
                # 결과의 일관성을 위해 temperature를 낮춤
                temperature=0.0
            )
        )

        # 5. 결과 출력
        print("="*50)
        print("[응답 결과]")
        print("="*50)
        print(response.text)
        print("="*50)

        # 6. 중간 로그 (Grounding 메타데이터) 확인 및 검증
        print("\n[🔍 내부 검색 로그 (Grounding Metadata)]")
        candidates = response.candidates
        if candidates and candidates[0].grounding_metadata:
            metadata = candidates[0].grounding_metadata
            
            # (1) 모델이 내부적으로 생성 및 실행한 실제 검색어 (webSearchQueries)
            # 가이드 참고: 단일 프롬프트라도 여러 개의 검색어가 생성될 수 있으며, 생성된 검색어 단위로 과금이 발생할 수 있음.
            search_queries = metadata.web_search_queries
            
            if search_queries:
                print("1. 사용된 Google 검색어 (webSearchQueries):")
                print(f"   원본 리스트: {search_queries}\n")
                
                print("   💡 [UI 디스플레이 규정 시뮬레이션: Search Suggestion 칩]")
                print("   (사용자가 직접 클릭하여 Google 검색 결과를 확인할 수 있도록 제공해야 함)")
                import urllib.parse
                for i, q in enumerate(search_queries):
                    # 검색어를 URL 인코딩하여 구글 검색 링크 생성
                    encoded_query = urllib.parse.quote(q)
                    search_url = f"https://www.google.com/search?q={encoded_query}"
                    print(f"   [{i+1}] 검색어: '{q}'")
                    print(f"       👉 Google 검색 결과 확인: {search_url}")
            else:
                print("1. 모델이 실행한 검색어 로그가 없습니다.")
            
            print("\n2. 검색해서 읽어온 문서(Chunks) 목록:")
            # (2) 검색 결과로 가져온 문서 출처
            if metadata.grounding_chunks:
                for i, chunk in enumerate(metadata.grounding_chunks):
                    if chunk.web:
                        print(f"   [{i+1}] {chunk.web.title}")
                        print(f"       URL: {chunk.web.uri}")
            else:
                print("   검색된 웹 출처가 없습니다.")
        else:
            print("Grounding 메타데이터가 없습니다.")

    except Exception as e:
        print(f"API 호출 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
