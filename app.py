import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")

# additional codes
df2 = pd.read_csv('data/koukouseiseki.csv')
df3 = pd.read_csv('data/nikkei225.csv')
vars2 = [var for var in df2.columns]
vars3 = [var for var in df3.columns]


# Layout (Sidebar)
st.sidebar.markdown("## サイドバーの使い方")
vars2_selected = st.sidebar.selectbox('散布図：高校科目', vars2)
vars2_multi_selected = st.sidebar.multiselect('相関行列：高校科目', vars2, default=vars2) # デフォルトは全部
vars3_selected = st.sidebar.selectbox('日経225の折れ線グラフ', vars3[1:])
vars3_multi_selected = st.sidebar.multiselect('日経225の折れ線グラフ（複数）', vars3, default=vars3[1:])


# 散布図
#fig2 = px.scatter(x=df2['国語'],y=df2['数学'])
fig2 = px.scatter(x=df2['国語'],y=df2[vars2_selected])
fig2.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

#（単一）折れ線グラフ
#fig3 = px.line(x=df3['日付'], y=df3['終値'])
df3['日付'] = pd.to_datetime(df3['日付'], format='%Y年%m月%d日')
fig3 = px.line(x=df3['日付'], y=df3[vars3_selected])
fig3.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

#fig4 = px.line(df3[vars3_multi_selected])
#fig4.update_layout(height=300,
#                   width=1000,
#                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

#（複数）折れ線グラフ
df3['日付'] = pd.to_datetime(df3['日付'], format='%Y年%m月%d日')
fig5 = px.line(df3, x='日付', y=vars3_multi_selected, 
              labels={'value': '株価（円）', 'variable': '株価の種類'},
              #title="日経225株価の推移"
              )
fig5.update_layout(height=300,
                   width=1000,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

#ウォーターフォール図
df3['終値'] = pd.to_numeric(df3['終値'].str.replace(',', ''))
df3['変化'] = df3['終値'].diff()
df3.at[0, '変化'] = df3.at[0, '終値']
fig6 = go.Figure(go.Waterfall(
    name="株価の変化",
    orientation="v",
    x=df3['日付'],
    y=df3['変化'],
    connector={"line":{"color":"rgb(63, 63, 63)"}},
    decreasing={"marker":{"color":"red"}},
    increasing={"marker":{"color":"green"}},
    totals={"marker":{"color":"blue"}},))
fig6.update_layout(
    title="日経225株価のウォーターフォール図",
    xaxis_title="日付",
    yaxis_title="株価の変化（円）",
    showlegend=True)


# Correlation Matrix of kamoku in Content
df2_corr = df2[vars2_multi_selected].corr()
fig_corr2 = go.Figure([go.Heatmap(z=df2_corr.values,
                                  x=df2_corr.index.values,
                                  y=df2_corr.columns.values)])
fig_corr2.update_layout(height=300,
                        width=1000,
                        margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

# 箱ひげ図
df2_melted = df2.melt(var_name='科目', value_name='得点')
fig7 = px.box(df2_melted, x='科目', y='得点', color='科目', title='各科目の得点分布')
fig7.update_layout(
    xaxis_title='科目',
    yaxis_title='得点',
    showlegend=False)

# ヒストグラム
fig8 = px.histogram(df2, x='国語', nbins=10, title='国語の得点分布')
fig8.update_layout(
    xaxis_title='得点',
    yaxis_title='頻度')

# 円グラフを作成
#final_row = df3.iloc[-1]
#fig9 = px.pie(names=['始値', '高値', '安値', '終値'], values=[final_row['始値'], final_row['高値'], final_row['安値'], final_row['終値']],
#             title='最終時点の株価')
#final_values = [33193.05, 33299.39, 32693.18, 33288.29]
#final_values = df3[vars3[1:]][:1]
final_values = df3.iloc[-1][['始値', '高値', '安値', '終値']].values
fig9 = px.pie(values=final_values, names=['始値', '高値', '安値', '終値'], title='最終時点の株価')

# Layout (Content)
left_column, right_column = st.columns(2)
left_column.subheader('日経225: ' + vars3_selected)
left_column.plotly_chart(fig3)
right_column.subheader('散布図：国語と' + vars2_selected)
right_column.plotly_chart(fig2)

left, center, right = st.columns(3)
left.subheader('ウォーターフォール')
left.plotly_chart(fig6)
center.subheader('箱ひげ図')
center.plotly_chart(fig7)
right.subheader('ヒストグラム')
right.plotly_chart(fig8)

st.subheader('円グラフ')
st.plotly_chart(fig9)

st.subheader('日経225すべて')
st.plotly_chart(fig5)
st.subheader('高校科目の相関行列')
st.plotly_chart(fig_corr2)
