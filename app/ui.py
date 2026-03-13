import streamlit as st
import requests

st.set_page_config(page_title="YouTube分析ツール", layout="centered")

st.title("Youtubeコメント分析レポート")
st.write("動画のURLを入力すると、AIが視聴者の反応を要約します。")

# 入力フォーム
with st.form("summarize_form"):
    url = st.text_input(
        "ここにYoutube動画のURLを入力",
        placeholder="https://www.youtube.com/watch?v=..."
    )
    submit = st.form_submit_button("分析を開始する")
    
if submit:
    if url:
        with st.spinner("コメントを取得して分析中... (1~2分かかる場合があります)"):
            try:
                # ローカルまたはCloud Run上のFastAPIエンドポイントを叩く
                response = requests.post(
                    "http://localhost:8000/summarize", json={"youtube_url": url}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("分析が完了しました")
                    st.subheader("分析レポート")
                    st.markdown(result["summary"])
                else:
                    st.error(f"APIエラー: ステータスコード{response.status_code}")
                    st.write(response.text)
            except Exception as e:
                st.error(f"接続エラー: {e}")
    else:
        st.warning("URLを入力してください。")