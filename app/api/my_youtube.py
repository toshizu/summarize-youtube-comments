import json
from pathlib import Path
from pytube import extract
from googleapiclient.discovery import build
from googleapiclient.discovery import Resource
from app.core.config import settings

# appディレクトリを取得
def get_app_dir():
    CURRENT_FILE = Path(__file__).resolve()
    APP_DIR = CURRENT_FILE.parents[1]
    return APP_DIR

# # .envファイルからyoutube api keyを取得して返す
# def get_youtube_api_key():
#     # .envファイルの内容を読み込む
#     load_dotenv()
#     # APIキーを取得
#     YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
#     if YOUTUBE_API_KEY:
#         print("Youtube APIキーの読み込みに成功しました")
#     else:
#         print("Youtube APIキーが見つかりません")
#     return YOUTUBE_API_KEY

# コメントデータのレスポンスから、キーに基づいて情報を抽出する
def extract_data(response: dict, keys: list):
    # データ用リスト
    data = []
    
    # データの抽出
    for item in response.get("items", []):
        comment = {k: item["snippet"]["topLevelComment"]["snippet"][k] for k in keys}
        data.append(comment)
    return data

# youtube動画のURLから、IDを取得する
def video_id_from_url(video_url: str):
    return extract.video_id(video_url)

# youtube動画のIDから、該当動画の情報を取得する
def get_video_info(video_id: str, youtube: Resource):
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    ).execute()

    # タイトル、説明文、チャンネル名、投稿時間
    keys = ["publishedAt", "title", "channelTitle"]
    v_info = {k: request["items"][0]["snippet"][k] for k in keys}
    
    return v_info

# youtube動画のIDから、全てののコメント情報を取得する
def get_all_comments(video_id: str, youtube: Resource):
    # 抽出するデータのキー
    keys = ["textOriginal", "likeCount", "publishedAt"]  # コメントの投稿日時も入れたいなぁ
    
    # データ用リスト
    data = []
    # ページネーション用のオブジェクト
    next_page_token = None

    # テスト段階でリクエスト数を節約するためのカウンター変数
    count = 0
    while True:
        # APIリクエスト処理...
        count += 1
        
        # snippetのみを指定してクォータ消費を最小限に(1リクエスト=2点)
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,  # 1回で取れる最大数
            pageToken=next_page_token,
            textFormat="plainText"
        )
        response = request.execute()
        
        # データの抽出(それぞれが1つのデータを示す辞書が入ったリスト)
        subset_data = extract_data(response, keys)
        data += subset_data

        # 次のページがあるか確認
        next_page_token = response.get("nextPageToken")

        # 次のページがなければ、または5回(500件)に達したらループ終了
        # 動作確認ができたら、countを外せば全取得モードになる
        if not next_page_token or count >= 1:
            break

    return data

# コメント情報を辞書で入れているリストから、JSONLファイルで保存する
def save_jsonl(data: list, file_name: str):
    # dataディレクトリ取得
    APP_DIR = get_app_dir()
    DATA_DIR = Path(APP_DIR, "data")
    # 安全のために、ディレクトリが存在しない場合に作成する処理を入れる
    DATA_DIR.mkdir(exist_ok=True)
    
    # ファイルパス作成
    jsonl_path = Path(DATA_DIR, Path(file_name).with_suffix(".jsonl"))
    
    # JSONLファイルへの書き込み処理
    with open(jsonl_path, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
            
    return jsonl_path

# youtube API関連のすべての処理をまとめる
def get_youtube_comments(youtube_url: str):
    # # YOUTUBE API KEYの取得
    # ログを追加
    # print(f"DEBUG: 使用するYouTube APIキー: {settings.youtube_api_key[:5]}***")
    
    # APIクライアントの構築
    youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)
    
    # ここにレポートが欲しい動画のURLを挿入
    video_id = video_id_from_url(youtube_url)
    
    # コメントのサンプルを取得する
    data = get_all_comments(video_id, youtube)
    
    # コメント情報の入ったデータセットから、欲しい情報を抽出してJSONLファイルで保存する
    jsonl_path = save_jsonl(data=data, file_name="comment_data")

    # 動画自体の情報
    v_info = get_video_info(video_id, youtube)
    
    return jsonl_path, v_info