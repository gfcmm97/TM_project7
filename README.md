# TM_project7

### 환경 설정
* back/requirements.txt로 의존성 설치
    - 가상환경을 back 하위에 두고 작업. 다른 위치에 생성할 경우 경로 수정 필요.
* TM+PROJECT7 내에 .env 파일 생성 후 다음과 같은 인증키 설정 필요
    - EASYDRUG_API_KEY: https://www.data.go.kr/data/15075057/openapi.do 해당 사이트에서 활용신청
    - GEMINI_API_KEY: Google Gemini 인증키
    - IPSTACK_KEY: IPStack 키 (사용자 위치 파악)
    - KAKAO_REST_API_KEY: KaKao API 중 REST API 키

---
### 실행
* Windows: run_site.bat
* MacOS: run_site.sh(실행 미확인)
    - MacOS에서 실행 안 될시, back에서 서버 실행 후 front의 main.html 수동 실행 필요.
    - 서버 실행 명령문: uvicorn main:app --reload