from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI
from app.api import my_gemini, my_youtube
from fastapi.middleware.cors import CORSMiddleware
# from .core.config import settings  # 環境設定を読み込む想定

# 送られてくるデータの形式をPydanticライブラリで定義。
# これにより、不正なデータを自動的に弾くことができる
class SummarizeRequest(BaseModel):
    # HttpUrl型を使う事で、正しいURL形式か自動チェックされる
    youtube_url: HttpUrl
    
app = FastAPI(title="Summarize Youtube Comment")

# どこからのリクエストも受け付けるようにする
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 全てのドメインからのアクセスを許可
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    # 1. コメントの取得と保存
    jsonl_path, v_info = my_youtube.get_youtube_comments(str(request.youtube_url))
    
    # 2. Geminiによる要約
    summary_text = my_gemini.summarize_comments(jsonl_path, v_info)
    
    # 3. 出てきた値を返す
    return {
        "status": "success",
        "message": "Youtubeのコメント取得と要約が完了しました。",
        "summary": summary_text
    }