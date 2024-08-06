import streamlit as st
import fitz
import requests
 
# PDFファイルのURL
url = 'https://www.zaimu.metro.tokyo.lg.jp/syukei1/zaisei/20231207hutuukaikeikessann.pdf'
#https://www.mhlw.go.jp/content/001282915.pdf
 
# requestsを使用してPDFをダウンロード
response = requests.get(url)
response.raise_for_status() # エラーになった時用
 
# ローカルにPDFファイルを保存
with open('settlement_reiwa4.pdf', 'wb') as f:
    f.write(response.content)
 
pdf_document = fitz.open('settlement_reiwa4.pdf', filetype="pdf")  
  
pdf_page_1 = pdf_document[0]
# テキストを抽出
pdf_text_1 = pdf_page_1.get_text("text")
print(pdf_text_1)


#########################
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

# 日本のタイムゾーンを設定
JST = pytz.timezone('Asia/Tokyo')

# CSVファイルのパス
CSV_FILE = 'data/stamps.csv'

# CSVファイルを読み込んでセッションステートに保存
if 'stamps' not in st.session_state:
    if os.path.exists(CSV_FILE):
        try:
            st.session_state.stamps = pd.read_csv(CSV_FILE)['datetime'].tolist()
        except Exception as e:
            st.error(f"CSVファイルの読み込みに失敗しました: {e}")
            st.session_state.stamps = []
    else:
        st.session_state.stamps = []

st.title("スタンプカードアプリ")

# 現在の時刻（日本時間）
now = datetime.now(JST)

# 5分単位に切り捨て
rounded_now = now - timedelta(minutes=now.minute % 10, seconds=now.second, microseconds=now.microsecond)
formatted_time = rounded_now.strftime('%Y-%m-%d %H:%M')

# 5分ごとのスタンプが既に存在するか確認
if formatted_time not in st.session_state.stamps:
    # 新しいスタンプを追加
    st.session_state.stamps.append(formatted_time)
    st.info(f"{formatted_time} のスタンプを押しました！")

    # デバッグ用にスタンプリストを表示
    st.write("追加後のスタンプリスト:", st.session_state.stamps)

    # CSVファイルに保存
    try:
        df = pd.DataFrame(st.session_state.stamps, columns=['datetime'])
        df.to_csv(CSV_FILE, index=False)
        st.success(f"{CSV_FILE} にスタンプを保存しました。")
    except Exception as e:
        st.error(f"CSVファイルの保存に失敗しました: {e}")
else:
    st.warning(f"{formatted_time} のスタンプは既に押しています。")

# 全てのスタンプを表示
st.subheader("これまでのスタンプ")
for stamp in st.session_state.stamps:
    st.write(stamp)


#
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import os

# 日本のタイムゾーンを設定
JST = pytz.timezone('Asia/Tokyo')

# CSVファイルのパス
CSV_FILE = 'data/stamps.csv'

# CSVファイルを読み込んでセッションステートに保存
if 'stamps' not in st.session_state:
    if os.path.exists(CSV_FILE):
        st.session_state.stamps = pd.read_csv(CSV_FILE)['datetime'].tolist()
    else:
        st.session_state.stamps = []

st.title("スタンプカードアプリ")
st.write(pd.read_csv(CSV_FILE)['datetime'].tolist())

# 現在の時刻（日本時間）
now = datetime.now(JST)

# 5分単位に切り捨て
rounded_now = now - timedelta(minutes=now.minute % 10, seconds=now.second, microseconds=now.microsecond)
formatted_time = rounded_now.strftime('%Y-%m-%d %H:%M')

# 5分ごとのスタンプが既に存在するか確認
if formatted_time not in st.session_state.stamps:
    # 新しいスタンプを追加
    st.session_state.stamps.append(formatted_time)
    st.info(f"{formatted_time} のスタンプを押しました！")

    # CSVファイルに保存
    df = pd.DataFrame(st.session_state.stamps, columns=['datetime'])
    df.to_csv(CSV_FILE, index=False)
    
    st.write(st.session_state.stamps)
else:
    st.warning(f"{formatted_time} のスタンプは既に押しています。")

# 全てのスタンプを表示
st.subheader("これまでのスタンプ")
for stamp in st.session_state.stamps:
    st.write(stamp)



# 5分ごとのスタンプ（日本時間）
# ユーザ名、パスワード、sqlite3なし
# 
import streamlit as st
from datetime import datetime, timedelta
import pytz

# 日本のタイムゾーンを設定
JST = pytz.timezone('Asia/Tokyo')

# セッションステートにスタンプを保存
if 'stamps' not in st.session_state:
    st.session_state.stamps = []

st.title("スタンプカードアプリ")

# 現在の時刻（日本時間）
now = datetime.now(JST)

# 5分単位に切り捨て
rounded_now = now - timedelta(minutes=now.minute % 10, seconds=now.second, microseconds=now.microsecond)
formatted_time = rounded_now.strftime('%Y-%m-%d %H:%M')

# 5分ごとのスタンプが既に存在するか確認
if formatted_time not in st.session_state.stamps:
    # 新しいスタンプを追加
    st.session_state.stamps.append(formatted_time)
    st.info(f"{formatted_time} のスタンプを押しました！")
else:
    st.warning(f"{formatted_time} のスタンプは既に押しています。")

# 全てのスタンプを表示
st.subheader("これまでのスタンプ")
for stamp in st.session_state.stamps:
    st.write(stamp)



######################################
# 一日ごとのスタンプ
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
