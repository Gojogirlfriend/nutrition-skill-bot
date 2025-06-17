from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import re

app = FastAPI()

# 직접 넣은 영양소 데이터
nutrition_data = {
  "6/17": {
    "탄수화물": "59%", "탄수화물 상태": "적정",
    "단백질": "22.4%", "단백질 상태": "약간 높음",
    "지방": "16.0%", "지방 상태": "적정",
    "비타민A": "약간 부족",
    "비타민C": "충분",
    "칼슘": "충분",
    "철분": "약간 부족"
  },
  "6/18": {
    "탄수화물": "53.8%", "탄수화물 상태": "약간 낮음",
    "단백질": "17.9%", "단백질 상태": "적정",
    "지방": "27.9%", "지방 상태": "적정",
    "비타민A": "약간 부족",
    "비타민C": "충분",
    "칼슘": "약간 부족",
    "철분": "약간 부족"
  },
  "6/19": {
    "탄수화물": "58.9%", "탄수화물 상태": "적정",
    "단백질": "16.6%", "단백질 상태": "적정",
    "지방": "23.8%", "지방 상태": "적정",
    "비타민A": "부족",
    "비타민C": "약간 부족",
    "칼슘": "약간 부족",
    "철분": "충분"
  },
  "6/20": {
    "탄수화물": "62.5%", "탄수화물 상태": "적정",
    "단백질": "11.8%", "단백질 상태": "적정",
    "지방": "22.3%", "지방 상태": "적정",
    "비타민A": "부족",
    "비타민C": "약간 부족",
    "칼슘": "충분",
    "철분": "약간 부족"
  },
  "6/23": {
    "탄수화물": "54.7%", "탄수화물 상태": "적정",
    "단백질": "19.1%", "단백질 상태": "적정",
    "지방": "25.1%", "지방 상태": "적정",
    "비타민A": "부족",
    "비타민C": "충분",
    "칼슘": "약간 부족",
    "철분": "충분"
  }
}

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

def get_nutrition_reply(date_key: str) -> str:
    data = nutrition_data.get(date_key)
    if not data:
        return "❗ 해당 날짜의 영양소 분석 정보가 없습니다."
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

@app.post("/nutrition")
async def nutrition_info(request: Request):
    try:
        body = await request.json()
        user_msg = body['userRequest']['utterance'].strip()
        date_key = parse_date_from_text(user_msg)

        if date_key:
            reply = get_nutrition_reply(date_key)
        else:
            reply = "분석을 원하는 날짜를 '6월 18일' 또는 '오늘'처럼 입력해주세요."

        return JSONResponse({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {"text": reply}
                }]
            }
        })

    except Exception as e:
        print("Error:", e)
        return JSONResponse({
            "version": "2.0",
            "template": {
                "outputs": [{
                    "simpleText": {"text": "⚠️ 서버 오류가 발생했습니다."}
                }]
            }
        })
