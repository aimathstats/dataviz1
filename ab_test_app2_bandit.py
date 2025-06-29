import streamlit as st
import pandas as pd
import numpy as np
import time
import os
import json
import matplotlib.pyplot as plt

# ---------- ファイルと初期設定 ----------
DATA_FILE = "ab_test_data2.csv"
BANDIT_STATE_FILE = "bandit_state.json"
ads = ["A", "B"]

# 広告画像のパス
ad_images = {
    'A': 'data/ad_A.png',
    'B': 'data/ad_B.png'
}

# ---------- バンディット状態の読み込み・初期化 ----------
if os.path.exists(BANDIT_STATE_FILE):
    with open(BANDIT_STATE_FILE, "r") as f:
        bandit_state = json.load(f)
else:
    bandit_state = {
        "counts": {ad: 0 for ad in ads},
        "values": {ad: 0.0 for ad in ads},
    }

# ---------- 広告選択（UCB） ----------
def select_ad(state):
    total_counts = sum(state["counts"].values()) + 1
    ucb_scores = {}
    for ad in ads:
        count = state["counts"][ad]
        value = state["values"][ad]
        if count == 0:
            ucb_scores[ad] = float("inf")
        else:
            ucb_scores[ad] = value + np.sqrt(2 * np.log(total_counts) / count)
    return max(ucb_scores, key=ucb_scores.get), ucb_scores

# ---------- 選択広告と滞在開始時間 ----------
if "ad_type" not in st.session_state:
    selected_ad, current_ucb = select_ad(bandit_state)
    st.session_state.ad_type = selected_ad
    st.session_state.ucb_scores = current_ucb
    st.session_state.start_time = time.time()

# ---------- UI：広告表示 ----------
st.title("📊 ABテスト with UCB")

# 広告表示（背景色なし）
ad = st.session_state.ad_type
st.markdown(f"### あなたに表示された広告タイプ：{ad}")
st.image(ad_images[ad], width=200)

# ---------- UCBスコアの可視化 ----------
st.subheader("📐 現在のUCBスコア")
st.table(pd.DataFrame({
    "表示回数 (count)": bandit_state["counts"],
    "平均滞在時間 (mean)": bandit_state["values"],
    "UCBスコア": st.session_state.ucb_scores
}))

# ---------- リアルタイム滞在時間表示 ----------
duration_placeholder = st.empty()
stop_button = st.button("✅ 滞在完了として記録")

#if not stop_button:
#    elapsed = time.time() - st.session_state.start_time
#    duration_placeholder.markdown(f"### ⏱ 現在の滞在時間：{elapsed:.1f} 秒")
#    time.sleep(1)
#    st.rerun()

# ---------- 記録と更新 ----------
if stop_button:
    end_time = time.time()
    duration = end_time - st.session_state.start_time

    new_row = pd.DataFrame([{"ad_type": ad, "duration": duration, "timestamp": pd.Timestamp.now()}])

    # CSVに保存
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(DATA_FILE, index=False)

    # バンディット状態を更新
    n = bandit_state["counts"][ad]
    old_mean = bandit_state["values"][ad]
    new_mean = (old_mean * n + duration) / (n + 1)
    bandit_state["counts"][ad] += 1
    bandit_state["values"][ad] = new_mean

    with open(BANDIT_STATE_FILE, "w") as f:
        json.dump(bandit_state, f)

    st.success(f"{ad} の滞在時間 {duration:.2f} 秒を記録しました。画面を更新して次の広告を表示します。")
    del st.session_state.ad_type
    del st.session_state.start_time
    del st.session_state.ucb_scores
    st.rerun()

# ---------- 結果の表示 ----------
st.divider()
st.subheader("📈 滞在時間の比較")

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    #st.dataframe(df.groupby("ad_type")["duration"].agg(["count", "mean", "std"]))
    summary = df.groupby("ad_type")["duration"].agg(['count','mean','std'])
    st.dataframe(summary)

    # グラフ表示を左右に並べる
    col1, col2 = st.columns(2)
    with col1:
        fig1, ax1 = plt.subplots()
        ax1.hist(df[df.ad_type == "A"]["duration"], bins=15, alpha=0.6, label="A")
        ax1.hist(df[df.ad_type == "B"]["duration"], bins=15, alpha=0.6, label="B")
        ax1.set_title("Histogram")
        ax1.set_xlabel("Duration (sec)")
        ax1.set_ylabel("Frequency")
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.boxplot([df[df.ad_type == "A"]["duration"], df[df.ad_type == "B"]["duration"]], labels=["A", "B"])
        ax2.set_title("Boxplot")
        ax2.set_ylabel("Duration (sec)")
        st.pyplot(fig2)

    # 全記録表示
    st.subheader("🗃 すべての記録")
    st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
else:
    st.info("まだ記録はありません。")
