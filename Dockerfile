# 1. ベースとなるOSとPython環境（プロジェクト指定の3.12系)
FROM python:3.12.10-slim

# 2. コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 3. 依存関係ファイルを先にコピー（キャッシュ効率化のため）
COPY requirements.txt .

# 4. ライブラリをインストール
# --no-cache-dirでイメージサイズを軽量化
RUN pip install --no-cache-dir -r requirements.txt

# 5. アプリケーションのソースコードをコピー
# app/ ディレクトリなどの構成を維持して配置
COPY . .

# # プロジェクトルート（/app）をPythonの検索パスに追加
# ENV PYTHONPATH=/app 

# 6. Cloud Runはデフォルトで8080ポートを使用するため環境変数を設定
ENV PORT=8080
# Pythonのログ出力をリアルタイムにする
ENV PYTHONUNBUFFERED=1

# start.sh に実行権限を付与
RUN chmod +x start.sh

# 起動コマンドを start.sh に変更
CMD ["./start.sh"]