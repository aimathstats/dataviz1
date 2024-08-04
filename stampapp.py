import streamlit as st
from datetime import date

# セッションステートにスタンプを保存
if 'stamps' not in st.session_state:
    st.session_state.stamps = []

st.title("スタンプカードアプリ")

# 今日の日付
today = date.today().isoformat()

# 今日のスタンプが既に存在するか確認
if today not in st.session_state.stamps:
    # 新しいスタンプを追加
    st.session_state.stamps.append(today)
    st.info("本日のスタンプを押しました！")
else:
    st.warning("今日は既にスタンプを押しています。")

# 全てのスタンプを表示
st.subheader("これまでのスタンプ")
for stamp in st.session_state.stamps:
    st.write(stamp)
