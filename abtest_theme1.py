import streamlit as st
import pandas as pd
import random
import os
from scipy.stats import ttest_ind, sem, t
import matplotlib.pyplot as plt

# データ保存用ファイル（最初は存在しなくても通る）
DATA_FILE = 'ab_test_data_theme1.csv'

# 広告画像のパス
ad_images = {
    'A': 'data/ad_A.png',
    'B': 'data/ad_B.png'
}

# 広告のランダム表示（セッション状態に保存）
if 'ad_type' not in st.session_state:
    st.session_state.ad_type = random.choice(['A', 'B'])

st.title("レストランQR注文画面")
st.write("以下はメニュー画面の一部")
st.image(ad_images[st.session_state.ad_type], width=200)
st.write("【おすすめ】ミートソーススパゲティ 900円（税込み）")


st.divider()

# 食べたい度の入力（0〜10のスライダー）
rating = st.slider(
    "このミートソーススパゲティをどのくらい食べたい？（10段階）",
    min_value=0,
    max_value=10,
    value=5,
    step=1
)
st.caption("0 = 全く食べたくない ／ 10 = 今すぐ注文")

# 評価の記録ボタン
if st.button("評価を送信（記録）して画面更新"):
    new_row = pd.DataFrame([{
        'ad_type': st.session_state.ad_type,
        'rating': rating,
        'timestamp': pd.Timestamp.now()
    }])

    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row

    df.to_csv(DATA_FILE, index=False)
    st.success(f"{st.session_state.ad_type} の食べたい度 {rating} を記録しました。")

    # 次のユーザーに向けて広告種類をリセットしてページをリロード
    if 'ad_type' in st.session_state:
        del st.session_state['ad_type']
    st.rerun()


st.markdown("<br>" * 20, unsafe_allow_html=True)

# データ処理と分析
st.divider()
st.write("※ 以下に示されるデータ分析はユーザーから見えません")
st.subheader("食べたい度の基本統計・データ可視化")

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)

    # 基本統計量
    summary = df.groupby("ad_type")["rating"].agg(['count', 'mean', 'std'])
    st.dataframe(summary)

    a_data = df[df["ad_type"] == "A"]["rating"]
    b_data = df[df["ad_type"] == "B"]["rating"]

    # グラフ表示
    st.subheader("食べたい度の分布")
    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots()
        ax1.hist(a_data, bins=11, alpha=0.6, label='A')  # 0〜10なので11ビン
        ax1.hist(b_data, bins=11, alpha=0.6, label='B')
        ax1.set_xlabel("Rating (0–10)")
        ax1.set_ylabel("Frequency")
        ax1.set_title("Histogram of Desire-to-Eat Rating")
        ax1.legend()
        st.pyplot(fig1)

    with col2:
        fig2, ax2 = plt.subplots()
        ax2.boxplot([a_data, b_data], labels=['A', 'B'])
        ax2.set_ylabel("Rating (0–10)")
        ax2.set_title("Boxplot of Desire-to-Eat Rating")
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

    st.subheader("平均食べたい度の95%信頼区間")
    ci_a = compute_ci(a_data)
    ci_b = compute_ci(b_data)

    if ci_a:
        st.write(
            f"Aの平均食べたい度: {a_data.mean():.2f} "
            f"(95% CI: [{ci_a[0]:.2f}, {ci_a[1]:.2f}])"
        )
    else:
        st.write("Aの信頼区間を計算するには2件以上のデータが必要です。")

    if ci_b:
        st.write(
            f"Bの平均食べたい度: {b_data.mean():.2f} "
            f"(95% CI: [{ci_b[0]:.2f}, {ci_b[1]:.2f}])"
        )
    else:
        st.write("Bの信頼区間を計算するには2件以上のデータが必要です。")

    # t検定
    if len(a_data) >= 2 and len(b_data) >= 2:
        t_stat, p_value = ttest_ind(a_data, b_data, equal_var=False)
        st.subheader("平均食べたい度のt検定")
        st.write(f"p値 = {p_value:.4f}（"
                 "「AとBで食べたい度の平均に差がない」という仮説の下で、"
                 "このデータ以上の差が得られる確率）")
        alpha = 0.05
        if p_value < alpha:
            st.success("差は統計的に有意です（p < 0.05）")
        else:
            st.info("差は統計的に有意とは言えません（p ≥ 0.05）")
    else:
        st.warning("検定には各群で2件以上のデータが必要です。")
else:
    st.info("まだ記録がありません。評価を送信してください。")

# 全データの表示
st.divider()
st.subheader("(参考)これまでに記録された全データ")
if os.path.exists(DATA_FILE):
    st.dataframe(df.sort_values("timestamp", ascending=False).reset_index(drop=True))
else:
    st.info("まだデータはありません。")
