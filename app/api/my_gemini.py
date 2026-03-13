# import os
import time
from pathlib import Path
# from dotenv import load_dotenv
from google import genai
from google.genai import Client
from google.genai import types
from app.core. config import settings

# # .envファイルからgemini api keyを取得して返す
# def get_gemini_api_key():
#     # .envファイルの内容を読み込む
#     load_dotenv()
#     # APIキーを取得
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#     if GEMINI_API_KEY:
#         print("Gemini APIキーの読み込みに成功しました")
#     else:
#         print("Gemini APIキーが見つかりません")
#     return GEMINI_API_KEY

# prompt作成
def make_prompt(v_info: dict):
    prompt = f"""
    提供したJSONLファイルは、YouTubeのコメントデータです。
    該当するYoutube動画は、{v_info["publishedAt"]}に
    「{v_info["channelTitle"]}」チャンネルに投稿された「{v_info["title"]}」という名前の動画です。
    JSONLファイルの各行は 「"textOriginal": "コメント内容",
    "likeCount": 高評価数, "publishedAt": コメントの投稿日時」 の形式になっています。
    これらを分析し、以下の点を1000文字以内でレポートしてください。
    1. 全体的な反応の傾向
    2. 特に高評価（likeCount）が多いコメントの共通点
    3. 目立つキーワードや話題
    """
    return prompt

# JSONLファイルをGoogleのサーバーへアップロードする
# ※ 24時間後に自動で削除される
def upload_jsonl(client: Client, jsonl_path: Path):
    uploaded_file = client.files.upload(
    file=jsonl_path,
    config=types.UploadFileConfig(mime_type="application/json")
)
    
    # 処理が完了するまで待機（大きなファイルの場合に必要）
    while uploaded_file.state.name == "PROCESSING":
        print("ファイルを処理中...")
        time.sleep(2)
        uploaded_file = client.files.get(name=uploaded_file.name)

    if uploaded_file.state.name == "FAILED":
        raise ValueError("ファイルのアップロードに失敗しました")
    
    return uploaded_file

# Gemini API 関連の全ての処理をまとめる
def summarize_comments(jsonl_path: Path, v_info: dict):
    # クライアント構築
    client = genai.Client(api_key=settings.gemini_api_key)
    
    # prompt作成
    prompt = make_prompt(v_info)
    
    # 1. ファイルをGoogleのサーバーへアップロード
    # ※ 24時間後に自動で削除される
    uploaded_file = upload_jsonl(client, jsonl_path)
    
    # ローカルファイルの削除(読み込み後であれば削除可能)
    jsonl_path.unlink()
    
    # 2. アップロードしたファイル(URL)とプロンプトを渡して、コメントのサマリーを作成
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=[prompt, uploaded_file]
    )
    
    return response.text