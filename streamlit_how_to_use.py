import streamlit as st
import datetime

st.title("Streamlit 入力ウィジェット一覧デモ")

# --- テキスト入力 ---
st.header("文字入力")
st.text_input("名前を入力してください", key="name_input")
st.text_input("パスワード", type="password", key="pw_input")
st.text_area("ご意見・ご感想", key="text_area_input")

# --- 数値入力 ---
st.header("数値・スライダー")
st.number_input("年齢を入力してください", min_value=0, max_value=120, key="age_input")
st.slider("点数を選んでください", 0, 100, 50, key="score_slider")

# --- 日時入力 ---
st.header("日付・時刻")
st.date_input("希望日を選択してください", value=datetime.date.today(), key="date_input")
st.time_input("希望時間を選択してください", key="time_input")

# --- 選択肢入力 ---
st.header("選択肢")
st.checkbox("同意しますか？", key="checkbox_input")
st.radio("性別を選んでください", ["男性", "女性", "その他"], key="radio_input")
st.selectbox("都道府県を選択してください", ["東京", "大阪", "京都", "福岡"], key="selectbox_input")
st.multiselect("得意科目を選択してください", ["国語", "数学", "英語", "理科", "社会"], key="multiselect_input")

# --- ファイル・メディア ---
st.header("ファイル・メディア")
uploaded_file = st.file_uploader("ファイルをアップロード")
if uploaded_file is not None:
    st.success("ファイルがアップロードされました")
    st.text(f"ファイル名: {uploaded_file.name}")

photo = st.camera_input("カメラで撮影（画像）")
if photo:
    st.image(photo)

# --- ボタン ---
st.header("ボタン")
if st.button("送信ボタンを押す"):
    st.success("ボタンが押されました！")

# --- フォームで一括処理 ---
st.header("ログインフォーム（form）")
with st.form("login_form"):
    username = st.text_input("ユーザー名", key="login_user")
    password = st.text_input("パスワード", type="password", key="login_pw")
    submitted = st.form_submit_button("ログイン")
    if submitted:
        st.info(f"{username} さんでログイン処理が実行されました（ダミー）")

