from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
from datetime import datetime
import re
import os

app = FastAPI()

# ===============================
# 유틸 함수들
# ===============================

def parse_date_from_text(text: str) -> str:
    text = text.strip()

    if "오늘" in text:
        today = datetime.now()
        return f"{today.month}/{str(today.day).zfill(2)}"

    match = re.search(r"6[./월\s]?\s?([0-9]{1,2})[일]?", text)
    if match:
        day = match.group(1).zfill(2)
        return f"6/{day}"

    return None

def get_nutrition_reply(nutrition_data: dict, date_key: str) -> str:
    if date_key in nutrition_data:
        data = nutrition_data[date_key]
        return (
            f"📅 6월 {date_key[-2:]}일 영양소 분석:\n\n"
            f"🔹 탄수화물: {data['탄수화물']} ({data['탄수화물 상태']})\n"
            f"🔹 단백질: {data['단백질']} ({data['단백질 상태']})\n"
            f"🔹 지방: {data['지방']} ({data['지방 상태']})\n\n"
            f"🔸 비타민 A: {data['비타민A']}\n"
            f"🔸 비타민 C: {data['비타민C']}\n"
            f"🔸 칼슘: {data['칼슘']}\n"
            f"🔸 철분: {data['철분']}"
        )
    else:
        return "❗ 해당 날짜의 영양소 분석 정보가 없습니다."

# ===============================
# JSON 영양소 데이터 불러오기
# ===============================

DATA_PATH = os.path.join(os.path.dirname(__file__), "nutrition_data.json")
with open(DATA_PATH, encoding="utf-8") as f:
    nutrition_data = json.load(f)

# ===============================
# FastAPI 엔드포인트
# ===============================

@app.post("/nutrition")
async def nutrition_info(request: Request):
    try:
        body = await request.json()
        user_msg = body['userRequest']['utterance'].strip()

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

