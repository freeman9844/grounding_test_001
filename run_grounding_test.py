#!/usr/bin/env python3
import sys
import urllib.parse
from datetime import datetime, timedelta

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ 'google-genai' 패키지가 설치되어 있지 않습니다.")
    print("실행 전 다음 명령어로 패키지를 설치해주세요:")
    print("pip install google-genai google-auth")
    sys.exit(1)

def main():
    # 설정 정보
    PROJECT_ID = "jwlee-argolis-202104"
    LOCATION = "global"  # Vertex AI는 리전(Region) 설정이 필요합니다. 기본값으로 global 사용.

    # 1. 3일 전 날짜 계산 (YYYY-MM-DD 형식)
    three_days_ago = datetime.now() - timedelta(days=3)
    date_str = three_days_ago.strftime("%Y-%m-%d")

    # 2. 프롬프트 구성 (after: 연산자 포함)
    query = f"삼성전자 최신 소식 알려줘 after:{date_str}"
    print(f"==================================================")
    print(f"🚀 테스트 시작: Vertex AI - Grounding with Google Search")
    print(f"✅ 프로젝트: {PROJECT_ID} ({LOCATION})")
    print(f"==================================================")
    print(f"생성된 프롬프트: {query}\n")

    # 3. Vertex AI 클라이언트 초기화 (ADC 인증 기반)
    try:
        # vertexai=True 플래그를 통해 Vertex AI 엔드포인트 사용 선언
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)
    except Exception as e:
         print(f"❌ 클라이언트 초기화 실패: {e}")
         print("\n💡 GCP 인증이 필요합니다. 터미널에서 다음 명령어를 실행하여 로그인해주세요:")
         print("gcloud auth application-default login")
         print(f"gcloud config set project {PROJECT_ID}")
         return

    # 4. 모델 호출 (Grounding with Google Search 활성화)
    model_name = "gemini-3.1-flash-lite-preview"
    print(f"[{model_name}] 모델에 요청을 보내는 중 (약간의 시간이 소요될 수 있습니다)...\n")

    try:
        # 1. System Instruction: 검색 쿼리에 'after:' 연산자를 강제로 포함시켜 
        # 검색 단계에서 과거 데이터를 배제하도록 유도합니다.
        system_instruction = (
            f"당신은 구글 검색을 활용하여 최신 정보를 제공하는 AI입니다. "
            f"검색 쿼리를 생성할 때는 반드시 검색어 뒤에 'after:{date_str}' 연산자를 포함시켜서 "
            f"최신 정보만 검색되도록 하세요. 과거 정보는 제외하고 가장 최신 정보 위주로 답변하세요."
        )

        # 2. Vertex AI 에서는 google-genai 최신 SDK 기준으로 
        # google_search_retrieval 대신 google_search 필드를 사용해야 합니다.
        google_search_tool = types.Tool(
            google_search=types.GoogleSearch()
        )

        response = client.models.generate_content(
            model=model_name,
            contents=query,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                # Google Search Tool 활성화
                tools=[google_search_tool],
                # 결과의 일관성을 위해 temperature를 낮춤
                temperature=0.0
            )
        )

        # 5. 결과 출력
        print("==================================================")
        print("✨ [최종 응답 결과]")
        print("==================================================")
        print(response.text)
        print("==================================================")

        # 6. 중간 로그 (Grounding 메타데이터) 확인 및 검증
        print("\n==================================================")
        print("🔍 [내부 검색 로그 (Grounding Metadata)]")
        print("==================================================")
        
        candidates = response.candidates
        if candidates and candidates[0].grounding_metadata:
            metadata = candidates[0].grounding_metadata
            
            # (1) 모델이 내부적으로 생성 및 실행한 실제 검색어 (webSearchQueries)
            search_queries = metadata.web_search_queries
            
            if search_queries:
                print("1. 사용된 Google 검색어 (webSearchQueries):")
                print(f"   원본 리스트: {search_queries}\n")
                
                print("   💡 [UI 디스플레이 규정 시뮬레이션: Search Suggestion 칩]")
                print("   (사용자가 직접 클릭하여 Google 검색 결과를 확인할 수 있도록 제공해야 함)")
                
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
        print(f"❌ API 호출 중 오류 발생: {e}")
        print("\n💡 참고: '403 Permission Denied' 오류 발생 시 아래 권한을 확인하세요.")
        print("   - Vertex AI API 활성화 여부")
        print("   - 계정에 'Vertex AI 사용자(roles/aiplatform.user)' 권한 부여 여부")
        print(f"   - 지정된 리전({LOCATION})에서 해당 모델({model_name}) 지원 여부")

if __name__ == "__main__":
    main()
