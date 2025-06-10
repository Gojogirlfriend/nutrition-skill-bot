from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
from datetime import datetime
import re

app = FastAPI()

# ===============================
# 유틸 함수들 (utils.py 내용 내장)
# ===============================

def parse_date_from_text(text: str) -> str:
    """
    사용자 메시지에서 날짜 키워드 추출 ('오늘' 또는 '6월 18일' 등)
    반환 형식: '6/18'
    """
    text = text.strip()

    # 오늘 날짜 자동 처리
    if "오늘" in text:
        today = datetime.now()
        return f"{today.month}/{str(today.day).zfill(2)}"  # 예: 6/09

    # 날짜 정규식: 6월 18일, 6/18, 6.18 등
    match = re.search(r"6[./월\s]?\s?([0-9]{1,2})[일]?", text)
    if match:
        day = match.group(1).zfill(2)
        return f"6/{day}"

    return None

def get_nutrition_reply(nutrition_data: dict, date_key: str) -> str:
    """
    영양소 데이터를 바탕으로 해당 날짜의 분석 결과를 문자열로 구성합니다.
    """
    if date_key in nutrition_data:
        data = nutrition_data[date_key]
        return (
            f"📅 6월 {date_key[-2:]}일 영양소 분석:\n"
            f"- 탄수화물: {data['탄수화물']} ({data['탄수화물 상태']})\n"
            f"- 단백질: {data['단백질']} ({data['단백질 상태']})\n"
            f"- 지방: {data['지방']} ({data['지방 상태']})"
        )
    else:
        return "해당 날짜의 영양소 분석 정보가 없습니다."

# ===============================
# JSON 영양소 데이터 불러오기
# ===============================

with open("app/nutrition_data.json", encoding="utf-8") as f:
    nutrition_data = json.load(f)

# ===============================
# FastAPI 엔드포인트
# ===============================

@app.post("/nutrition")
async def nutrition_info(request: Request):
    try:
        body = await request.json()
        user_msg = body['userRequest']['utterance'].strip()

        # 날짜 파싱
        date_keyword = parse_date_from_text(user_msg)

        if date_keyword:
            reply = get_nutrition_reply(nutrition_data, date_keyword)
        else:
            reply = "분석을 원하는 날짜를 '6월 18일' 또는 '오늘'처럼 입력해주세요."

        return JSONResponse({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": reply
                    }
                }]
            }
        })

    except Exception as e:
        print("에러:", e)
        return JSONResponse({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {
                        "text": "⚠️ 서버 오류가 발생했습니다."
                    }
                }]
            }
        })
