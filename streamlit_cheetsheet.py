import streamlit as st
from datetime import datetime

st.title("🧪 Streamlit ユーザーアクション一覧デモ")

st.header("📝 テキスト入力系")
name = st.text_input("名前を入力")
intro = st.text_area("自己紹介を入力")
age = st.number_input("年齢を入力", min_value=0, max_value=150)

st.header("✅ チェック・選択系")
agree = st.checkbox("規約に同意する")
gender = st.radio("性別を選択", ["男性", "女性", "その他"])
color = st.selectbox("好きな色を選択", ["赤", "青", "緑", "黄色"])
hobbies = st.multiselect("趣味を選択", ["読書", "音楽", "映画", "運動"])

st.header("📆 日時入力系")
birthday = st.date_input("誕生日を選択")
meeting_time = st.time_input("会議時間を選択")

st.header("🎚 スライダー")
temperature = st.slider("今日の気温を選んでください", min_value=-20, max_value=40, value=20)

st.header("🔐 パスワード入力")
password = st.text_input("パスワードを入力", type="password")

st.header("📁 ファイルアップロード")
uploaded_file = st.file_uploader("ファイルをアップロード")
if uploaded_file:
    st.success("ファイルがアップロードされました！")
    st.write("ファイル名:", uploaded_file.name)

st.header("📷 カメラ入力（対応ブラウザのみ）")
camera_photo = st.camera_input("写真を撮影")
if camera_photo:
    st.image(camera_photo, caption="撮影した写真", use_column_width=True)

st.header("🔊 音声ファイルアップロード")
audio_file = st.file_uploader("音声ファイルをアップロード", type=["mp3", "wav"])
if audio_file:
    st.audio(audio_file)

st.header("📋 フォーム（まとめて送信）")
with st.form("my_form"):
    form_name = st.text_input("フォーム内の名前")
    form_age = st.slider("年齢", 0, 120, 25)
    form_submit = st.form_submit_button("送信")
    if form_submit:
        st.success(f"送信されました: {form_name}（{form_age}歳）")

st.header("💡 現在の入力内容の確認")
st.write({
    "名前": name,
    "自己紹介": intro,
    "年齢": age,
    "同意": agree,
    "性別": gender,
    "好きな色": color,
    "趣味": hobbies,
    "誕生日": birthday,
    "会議時間": meeting_time,
    "気温": temperature,
})

st.info("このページでは、Streamlit の主なユーザーインタラクション機能を体験できます。")
