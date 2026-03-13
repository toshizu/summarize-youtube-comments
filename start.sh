#!/bin/bash

# 1. FastAPI をバックグラウンドで起動
# モジュールとしての実行（app.main）を指定し、作業ディレクトリを基準にします
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2. Streamlit をフォアグラウンドで起動
# ui.py の場所を正しく指定します
streamlit run app/ui.py --server.port=8080 --server.address=0.0.0.0