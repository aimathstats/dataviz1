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
vars2_selected = st.sidebar.selectbox('高校科目', vars2)
vars2_multi_selected = st.sidebar.multiselect('高校科目', vars2, default=vars2) # デフォルトは全部
vars3_selected = st.sidebar.selectbox('日経225系列', vars3[1:])
vars3_multi_selected = st.sidebar.multiselect('日経225系列', vars3, default=vars3[1:])


# additional codes
#fig2 = px.scatter(x=df2['国語'],y=df2['数学'])
fig2 = px.scatter(x=df2['国語'],y=df2[vars2_selected])
fig2.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})


#fig3 = px.line(x=df3['日付'], y=df3['終値'])
df3['日付'] = pd.to_datetime(df3['日付'], format='%Y年%m月%d日')
fig3 = px.line(x=df3['日付'], y=df3[vars3_selected])
fig3.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

fig4 = px.line(df3[vars3_multi_selected])
fig4.update_layout(height=300,
                   width=1000,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

df3['日付'] = pd.to_datetime(df3['日付'], format='%Y年%m月%d日')
fig5 = px.line(df3, x='日付', y=vars3[1:], 
              labels={'value': '株価（円）', 'variable': '株価の種類'},
              title="日経225株価の推移")

# Correlation Matrix of kamoku in Content
df2_corr = df2[vars2_multi_selected].corr()
fig_corr2 = go.Figure([go.Heatmap(z=df2_corr.values,
                                  x=df2_corr.index.values,
                                  y=df2_corr.columns.values)])
fig_corr2.update_layout(height=300,
                        width=1000,
                        margin={'l': 20, 'r': 20, 't': 0, 'b': 0})

# Layout (Content)
left_column, right_column = st.columns(2)
left_column.subheader('日経225: ' + vars3_selected)
left_column.plotly_chart(fig3)
right_column.subheader('散布図：国語と' + vars2_selected)
right_column.plotly_chart(fig2)

st.subheader('日経225すべて')
st.plotly_chart(fig5)
st.subheader('高校科目の相関行列')
st.plotly_chart(fig_corr2)
