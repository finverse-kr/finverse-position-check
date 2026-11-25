# 핀버스 내 종목 위치 체크기

종목명만 치면 내 종목의 지금 위치를 보여주는 도구입니다.
최근 20거래일 고저 대비 위치, 거래 강도, 추세, 단기 모멘텀을
게이지와 레이더 차트로 보여주고, 핀버스 블로그 강의로 이어줍니다.

- 라이브: https://finverse-kr.github.io/finverse-position-check/
- 데이터: Yahoo Finance 일봉 (전일 종가 기준, 매일 장 마감 후 자동 갱신)
- 종목 수: 141개 (인기 종목 중심, `fetch_stocks.py`의 STOCKS 목록에서 관리)

## 파일

- `index.html` — 도구 페이지 (단일 파일 + JSON 로드)
- `stocks.json` — 종목명·코드 목록 (검색 자동완성용)
- `data.json` — 종목별 지표 (매일 갱신)
- `fetch_stocks.py` — 데이터 수집기 (Yahoo Finance chart API)
- `og-image.png` — 링크 미리보기 이미지 (1200x630)
- `.github/workflows/update-data.yml` — 평일 17:00 KST 자동 갱신

## 종목 추가

`fetch_stocks.py`의 STOCKS 목록에 `(이름, 코드, 시장)`을 추가하고
`python3 fetch_stocks.py`를 실행하면 `stocks.json`·`data.json`이 갱신됩니다.
시장: 코스피 `KS`, 코스닥 `KQ`.

## 주의

교육용 참고 자료입니다. 매수·매도 권유가 아니며, 특정 종목에 대한
투자 판단을 대신하지 않습니다.
