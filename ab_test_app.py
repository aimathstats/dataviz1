import streamlit as st
import pandas as pd
import random
import time
import os
from scipy.stats import ttest_ind, sem, t
import matplotlib.pyplot as plt

# データ保存用ファイル（最初は存在しなくても通る）
DATA_FILE = 'ab_test_data.csv'

# 広告画像のパス
ad_images = {
    'A': 'data/ad_A.png',
    'B': 'data/ad_B.png'
}

ad_images = {
    'A': 'data/movA.mp4',
    'B': 'data/movB.mp4'
}

# 広告のランダム表示と計測開始（セッション状態に保存）
if 'ad_type' not in st.session_state:
    st.session_state.ad_type = random.choice(['A', 'B'])
    st.session_state.start_time = time.time()

st.title("Web広告のABテスト")
st.write("広告AまたはBをそれぞれ確率1/2で表示する")
st.subheader(f"あなたの広告：**{st.session_state.ad_type}**")
st.video(ad_images[st.session_state.ad_type], width=200, autoplay=True, loop=True)
#st.image(ad_images[st.session_state.ad_type], width=200)

#st.write("このページに滞在した時間を記録します。「滞在完了」ボタンを押すと記録されます。")

# 滞在時間の記録
if st.button("滞在完了（記録）して画面更新"):
    end_time = time.time()
    duration = end_time - st.session_state.start_time

    new_row = pd.DataFrame([{
        'ad_type': st.session_state.ad_type,
        'duration': duration,
        'timestamp': pd.Timestamp.now()
    }])

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row

    df.to_csv(DATA_FILE, index=False)
    st.success(f"{st.session_state.ad_type} の滞在時間 {duration:.2f} 秒を記録しました。")
    
    # session_stateをクリアしてページをリロード
    for key in ['ad_type', 'start_time']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# データ処理と分析
st.divider()
st.write("※ 以下に示されるデータ分析はユーザーから見えません")
st.subheader("広告の滞在時間の基本統計・データ可視化")

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
    summary = df.groupby("ad_type")["duration"].agg(['count','mean','std'])
    st.dataframe(summary)
    a_data = df[df["ad_type"] == "A"]["duration"]
    b_data = df[df["ad_type"] == "B"]["duration"]

    # グラフ表示
    st.subheader("滞在時間の分布")
    col1, col2 = st.columns(2)
    with col1:
        fig1, ax1 = plt.subplots()
        ax1.hist(a_data, bins=15, alpha=0.6, label='A')
        ax1.hist(b_data, bins=15, alpha=0.6, label='B')
        ax1.set_xlabel("Duration (second)")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Histogram of Stay Duration")
        ax1.legend()
        st.pyplot(fig1)
    with col2:
        fig2, ax2 = plt.subplots()
        ax2.boxplot([a_data, b_data], labels=['A', 'B'])
        ax2.set_ylabel("Duration (second)")
        ax2.set_title("Boxplot of Stay Duration")
        st.pyplot(fig2)

    # 信頼区間（95%）表示
    def compute_ci(data, alpha=0.05):
        n = len(data)
        if n < 2:
            return None
        m = data.mean()
        s = sem(data)
        t_val = t.ppf(1 - alpha/2, df=n - 1)
        ci = t_val * s
        return (m - ci, m + ci)

    st.subheader("平均滞在時間の95%信頼区間")
    ci_a = compute_ci(a_data)
    ci_b = compute_ci(b_data)

    if ci_a:
        st.write(f"広告Aの平均: {a_data.mean():.2f} 秒 (95% CI: [{ci_a[0]:.2f}, {ci_a[1]:.2f}])")
    else:
        st.write("広告Aの信頼区間を計算するには2件以上のデータが必要です。")

    if ci_b:
        st.write(f"広告Bの平均: {b_data.mean():.2f} 秒 (95% CI: [{ci_b[0]:.2f}, {ci_b[1]:.2f}])")
    else:
        st.write("広告Bの信頼区間を計算するには2件以上のデータが必要です。")

    # t検定
    if len(a_data) >= 2 and len(b_data) >= 2:
        t_stat, p_value = ttest_ind(a_data, b_data, equal_var=False)
        st.subheader("平均滞在時間のt検定")
        #st.write(f"検定統計量 t = {t_stat:.3f}")
        st.write(f"p値 = {p_value:.4f}（「広告の間に差がない」とする仮説の下でデータが得られる確率）")
        alpha = 0.05
        if p_value < alpha:
            st.success("差は統計的に有意です（p < 0.05）")
        else:
            st.info("差は統計的に有意とは言えません（p ≥ 0.05）")
    else:
        st.warning("検定には各群で2件以上のデータが必要です。")
else:
    st.info("まだ記録がありません。滞在完了を記録してください。")

# 全データの表示
st.divider()
st.subheader("(参考)これまでに記録された全データ")
if os.path.exists(DATA_FILE):
    st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
else:
    st.info("まだデータはありません。")
