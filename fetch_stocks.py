#!/usr/bin/env python3
"""핀버스 위치 체크기용 데이터 수집기.
Yahoo Finance chart API에서 인기 종목의 최근 3개월 일봉을 받아
20일 기준 위치·거래·추세·모멘텀 지표를 계산해 data.json으로 저장한다.
매일 장 마감 후 GitHub Actions가 실행한다. (전일 종가 기준)
"""
import json
import os
import statistics
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
BASE = os.path.dirname(os.path.abspath(__file__))

# (표시 이름, 종목코드, 시장) — 검증 단계에서 Yahoo 응답으로 확인한다
STOCKS = [
    # 코스피
    ("삼성전자", "005930", "KS"), ("SK하이닉스", "000660", "KS"),
    ("현대차", "005380", "KS"), ("LG에너지솔루션", "373220", "KS"),
    ("삼성바이오로직스", "207940", "KS"), ("기아", "000270", "KS"),
    ("셀트리온", "068270", "KS"), ("NAVER", "035420", "KS"),
    ("카카오", "035720", "KS"), ("POSCO홀딩스", "005490", "KS"),
    ("LG화학", "051910", "KS"), ("삼성SDI", "006400", "KS"),
    ("현대모비스", "012330", "KS"), ("메리츠금융지주", "138040", "KS"),
    ("KB금융", "105560", "KS"), ("신한지주", "055550", "KS"),
    ("하나금융지주", "086790", "KS"), ("우리금융지주", "316140", "KS"),
    ("삼성화재", "000810", "KS"), ("SK", "034730", "KS"),
    ("LG", "003550", "KS"), ("삼성물산", "028260", "KS"),
    ("HD현대중공업", "329180", "KS"), ("한화에어로스페이스", "012450", "KS"),
    ("LIG넥스원", "079550", "KS"), ("현대로템", "064350", "KS"),
    ("두산에너빌리티", "034020", "KS"), ("한국전력", "015760", "KS"),
    ("SK텔레콤", "017670", "KS"), ("KT", "030200", "KS"),
    ("LG유플러스", "032640", "KS"), ("KT&G", "033780", "KS"),
    ("아모레퍼시픽", "090430", "KS"), ("LG생활건강", "051900", "KS"),
    ("유한양행", "000100", "KS"), ("삼성E&A", "028050", "KS"),
    ("LG이노텍", "011070", "KS"), ("삼성전기", "009150", "KS"),
    ("HMM", "011200", "KS"), ("현대건설", "000720", "KS"),
    ("포스코인터내셔널", "047050", "KS"), ("S-Oil", "010950", "KS"),
    ("SK이노베이션", "096770", "KS"), ("포스코퓨처엠", "003670", "KS"),
    ("고려아연", "010130", "KS"), ("미래에셋증권", "006800", "KS"),
    ("키움증권", "039490", "KS"), ("삼성증권", "016360", "KS"),
    ("한국금융지주", "071050", "KS"), ("현대글로비스", "086280", "KS"),
    ("대한항공", "003490", "KS"), ("한화시스템", "272210", "KS"),
    ("한국항공우주", "047810", "KS"), ("한미반도체", "042700", "KS"),
    ("한화", "000880", "KS"), ("DB손해보험", "005830", "KS"),
    ("삼성생명", "032830", "KS"), ("삼성중공업", "010140", "KS"),
    ("HD한국조선해양", "009540", "KS"), ("한화오션", "042660", "KS"),
    ("LG디스플레이", "034220", "KS"), ("롯데케미칼", "011170", "KS"),
    ("현대제철", "004020", "KS"), ("NH투자증권", "005940", "KS"),
    ("CJ", "001040", "KS"), ("롯데지주", "004990", "KS"),
    ("GS", "078930", "KS"), ("GS건설", "006360", "KS"),
    ("CJ대한통운", "000120", "KS"), ("코웨이", "021240", "KS"),
    ("크래프톤", "259960", "KS"), ("넷마블", "251270", "KS"),
    ("엔씨소프트", "036570", "KS"), ("펄어비스", "263750", "KS"),
    ("네오위즈", "095660", "KQ"), ("위메이드", "112040", "KQ"),
    ("제일기획", "030000", "KS"), ("카카오뱅크", "323410", "KS"),
    ("카카오페이", "377300", "KS"), ("두산", "000150", "KS"),
    ("효성중공업", "298040", "KS"), ("LS", "006260", "KS"),
    ("LS ELECTRIC", "010120", "KS"), ("일진전기", "103590", "KS"),
    ("대한전선", "001440", "KS"), ("HD현대일렉트릭", "267260", "KS"),
    ("HD현대", "267250", "KS"), ("SK스퀘어", "402340", "KS"),
    ("SKC", "011790", "KS"), ("금호석유", "011780", "KS"),
    ("한미약품", "128940", "KS"), ("대웅제약", "069620", "KS"),
    ("종근당", "185750", "KS"), ("GC녹십자", "006280", "KS"),
    ("오리온", "271560", "KS"), ("농심", "004370", "KS"),
    ("하이트진로", "000080", "KS"), ("롯데칠성", "005300", "KS"),
    ("CJ제일제당", "097950", "KS"), ("대상", "001680", "KS"),
    # 코스닥
    ("실리콘투", "257720", "KQ"), ("에이피알", "278470", "KQ"),
    ("코스맥스", "192820", "KQ"), ("한국콜마", "161890", "KQ"),
    ("HLB", "028300", "KQ"), ("알테오젠", "196170", "KQ"),
    ("리가켐바이오", "141080", "KQ"), ("에코프로", "086520", "KQ"),
    ("에코프로비엠", "247540", "KQ"),
    ("JYP Ent.", "035900", "KQ"), ("하이브", "352820", "KQ"),
    ("에스엠", "041510", "KQ"), ("YG엔터테인먼트", "122870", "KQ"),
    ("카카오게임즈", "293490", "KQ"), ("CJ ENM", "035760", "KQ"),
    ("휴젤", "145020", "KQ"),
    ("클래시스", "214150", "KQ"),
    ("SK바이오팜", "326030", "KQ"), ("SK바이오사이언스", "302440", "KQ"),
    ("스튜디오드래곤", "131100", "KQ"), ("솔브레인", "036830", "KQ"),
    ("리노공업", "058470", "KQ"), ("이오테크닉스", "039030", "KQ"),
    ("원익IPS", "240810", "KQ"), ("주성엔지니어링", "036930", "KQ"),
    ("신성델타테크", "065350", "KQ"), ("나노신소재", "121600", "KQ"),
    ("케어젠", "214370", "KQ"), ("에스티팜", "237690", "KQ"),
    ("티씨케이", "064760", "KQ"), ("유진테크", "084370", "KQ"),
    ("동진쎄미켐", "253450", "KQ"), ("대주전자재료", "078600", "KQ"),
    ("펩트론", "087010", "KQ"), ("삼천당제약", "000250", "KQ"),
    ("HLB생명과학", "067630", "KQ"), ("레인보우로보틱스", "277810", "KQ"),
    ("로보티즈", "108490", "KQ"), ("두산테스나", "131970", "KQ"),
    ("테크윙", "089030", "KQ"), ("한양디지텍", "078350", "KQ"),
]


def fetch(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=3mo&interval=1d"
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            if attempt == 2:
                return {"_error": str(e)}
            time.sleep(2 * (attempt + 1))
    return {"_error": "unknown"}


def clamp(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def build(name, code, market):
    symbol = f"{code}.{market}"
    raw = fetch(symbol)
    if "_error" in raw:
        return None, f"{symbol}: {raw['_error']}"
    try:
        res = raw["chart"]["result"][0]
    except Exception:
        return None, f"{symbol}: no result"
    meta = res.get("meta", {})
    if meta.get("currency") != "KRW":
        return None, f"{symbol}: not KRW ({meta.get('currency')})"
    ts = res.get("timestamp") or []
    q = (res.get("indicators") or {}).get("quote", [{}])[0]
    closes = [c for c in (q.get("close") or []) if c is not None]
    highs = [h for h in (q.get("high") or []) if h is not None]
    lows = [l for l in (q.get("low") or []) if l is not None]
    vols = [v for v in (q.get("volume") or []) if v is not None]
    if len(closes) < 25 or not ts:
        return None, f"{symbol}: too few bars ({len(closes)})"
    last = closes[-1]
    prev = closes[-2]
    # 기준 범위: 오늘을 제외한 최근 20거래일 '종가' 고저 (참고 앱과 동일 기준)
    prev20 = closes[-21:-1]
    h20 = max(prev20)
    l20 = min(prev20)
    pos = (last - l20) / (h20 - l20) * 100 if h20 > l20 else 50.0
    avg_vol = statistics.fmean(vols[-21:-1])
    vol_ratio = vols[-1] / avg_vol if avg_vol else 0
    ma5 = statistics.fmean(closes[-5:])
    ma20 = statistics.fmean(closes[-20:])
    trend = (last - ma20) / ma20 * 100 if ma20 else 0
    mom5 = (last - closes[-6]) / closes[-6] * 100 if len(closes) >= 6 else 0
    # 레이더 축 (0~100)
    pos_score = clamp(pos)
    vol_score = clamp(vol_ratio / 3 * 100)  # 3배면 100
    trend_score = clamp(50 + trend * 5)  # 이평 대비 ±10% → 0~100
    mom_score = clamp(50 + mom5 * 5)  # 5일 ±10% → 0~100
    from datetime import datetime, timezone, timedelta
    kst = timezone(timedelta(hours=9))
    as_of = datetime.fromtimestamp(ts[-1], tz=kst).strftime("%Y-%m-%d")
    return {
        "name": name,
        "code": code,
        "market": "코스피" if market == "KS" else "코스닥",
        "symbol": symbol,
        "price": last,
        "prev_close": prev,
        "change_pct": round((last - prev) / prev * 100, 2) if prev else 0,
        "high20": h20,
        "low20": l20,
        "position_pct": round(pos, 1),
        "volume": vols[-1],
        "avg_volume20": round(avg_vol),
        "volume_ratio": round(vol_ratio, 2),
        "ma20": round(ma20),
        "trend_pct": round(trend, 2),
        "momentum5_pct": round(mom5, 2),
        "scores": {
            "position": round(pos_score),
            "volume": round(vol_score),
            "trend": round(trend_score),
            "momentum": round(mom_score),
        },
        "as_of": as_of,
    }, None


def main():
    out = {}
    failed = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        results = list(ex.map(lambda s: (s, build(*s)), STOCKS))
    for (name, code, market), (item, err) in results:
        if item:
            out[f"{code}"] = item
        else:
            failed.append(err)
    payload = {
        "as_of": max((v["as_of"] for v in out.values()), default=""),
        "count": len(out),
        "source": "Yahoo Finance (전일 종가 기준)",
        "stocks": out,
    }
    with open(os.path.join(BASE, "data.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    stock_list = [
        {"name": v["name"], "code": v["code"], "market": v["market"]}
        for v in sorted(out.values(), key=lambda x: x["name"])
    ]
    with open(os.path.join(BASE, "stocks.json"), "w", encoding="utf-8") as f:
        json.dump(stock_list, f, ensure_ascii=False, indent=1)
    print(f"OK {len(out)} / {len(STOCKS)}")
    for e in failed:
        print("FAIL:", e)


if __name__ == "__main__":
    main()
