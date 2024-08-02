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


# map graph
from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

import pandas as pd
df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/fips-unemp-16.csv",
                   dtype={"fips": str})
import plotly.express as px
fig11 = px.choropleth(df, geojson=counties, locations='fips', color='unemp',
                           color_continuous_scale="Viridis",
                           range_color=(0, 12),
                           scope="usa",
                           labels={'unemp':'unemployment rate'}
                          )
fig11.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# 
import plotly.graph_objects as go
df4 = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2011_us_ag_exports.csv')
fig12 = go.Figure(data=go.Choropleth(
    locations=df4['code'], # Spatial coordinates
    z = df4['total exports'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Millions USD",))
fig12.update_layout(
    title_text = '2011 US Agriculture Exports by State',
    geo_scope='usa', # limite map scope to USA
)

#
import json
from io import StringIO
with open("data/N03-23_25_230101.geojson", encoding = 'utf-8') as f:
    geojson = json.load(f)
#geojson["features"][1]["properties"]

shiga_pop_text = """市区町村名,男,女,計,世帯数
大津市,160170,169871,330041,130143
彦根市,53908,55368,109276,41257
長浜市,39575,41263,80838,27937
近江八幡市,33530,34786,68316,25445
草津市,59131,58415,117546,46997
守山市,37379,38152,75531,26689
栗東市,31775,31670,63445,23091
甲賀市,45782,46877,92659,30640
野洲市,24889,24960,49849,17639
湖南市,27278,25621,52899,20037
高島市,26260,27599,53859,19205
東近江市,56384,57781,114165,38143
米原市,20140,20932,41072,13147
日野町,11158,11644,22802,7552
竜王町,7068,6256,13324,4412
愛荘町,9623,9833,19456,6256
豊郷町,3524,3681,7205,2574
甲良町,3792,4162,7954,2425
多賀町,3882,4251,8133,2640"""
shiga_pop = pd.read_csv(StringIO(shiga_pop_text))
shiga_pop.head()

fig13 = px.choropleth_mapbox(
    shiga_pop,
    geojson=geojson,
    locations="市区町村名",
    color="計",
    hover_name="市区町村名",
    hover_data=["男", "女", "世帯数"],
    featureidkey="properties.N03_004",
    mapbox_style="carto-positron",
    zoom=8,
    center={"lat": 35.09, "lon": 136.18},
    opacity=0.5,
    width=800,
    height=800,
)

# treemap
df5 = px.data.tips()
fig14 = px.treemap(df5, path=[px.Constant("all"), 'day', 'time', 'sex'], values='total_bill')
fig14.update_traces(root_color="lightgrey")
#fig14.update_layout(margin = dict(t=50, l=25, r=25, b=25))

# area map
df6 = px.data.iris()
fig15 = px.area(df6, x="sepal_width", y="sepal_length",
            color="species",
            hover_data=['petal_width'],)


# 散布図
#fig2 = px.scatter(x=df2['国語'],y=df2['数学'])
fig2 = px.scatter(x=df2['国語'],y=df2[vars2_selected])
fig2.update_layout(height=300,
                   width=500,
                   margin={'l': 20, 'r': 20, 't': 0, 'b': 0})


# contribution graph
df8 = pd.read_csv('data/kisho_data.csv')


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
df2_ = df2[vars2_multi_selected]
df2_melted = df2_.melt(var_name='科目', value_name='得点')
fig7 = px.box(df2_melted, x='科目', y='得点', color='科目', title='各科目の得点分布')
#fig7 = px.box(df2_melted, x=vars2_multi_selected, y='得点', color='科目', title='各科目の得点分布')
fig7.update_layout(
    xaxis_title='科目',
    yaxis_title='得点',
    showlegend=False)

# ヒストグラム
fig8 = px.histogram(df2, x='国語', nbins=10, title='国語の得点分布')
fig8 = px.histogram(df2, x=vars2_selected, nbins=10)
fig8.update_layout(
    xaxis_title='得点',
    yaxis_title='頻度')


# 円グラフを作成
data = pd.read_csv('data/nikkei225.csv')
#final_values = df3[vars3[1:]][:1]
#final_values = df3.iloc[-1][['始値', '高値', '安値', '終値']].values
final_values = [33193.05, 33299.39, 32693.18, 33288.29]
fig9 = px.pie(values=final_values, names=['始値', '高値', '安値', '終値'], title='最終時点の株価')

# 棒グラフで作成
data['始値'] = pd.to_numeric(data['始値'].str.replace(',', ''))
data['高値'] = pd.to_numeric(data['高値'].str.replace(',', ''))
data['安値'] = pd.to_numeric(data['安値'].str.replace(',', ''))
data['終値'] = pd.to_numeric(data['終値'].str.replace(',', ''))
final_row = data.iloc[-1]
final_values = [final_row['始値'], final_row['高値'], final_row['安値'], final_row['終値']]
fig10 = go.Figure(data=[
    go.Bar(name='始値', x=['始値'], y=[final_values[0]]),
    go.Bar(name='高値', x=['高値'], y=[final_values[1]]),
    go.Bar(name='安値', x=['安値'], y=[final_values[2]]),
    go.Bar(name='終値', x=['終値'], y=[final_values[3]])])
fig10.update_layout(
    title='最終時点の株価',
    xaxis_title='種類',
    yaxis_title='株価（円）',
    barmode='group')

# bar chart
import numpy as np
np.random.seed(42) 
random_x= np.random.randint(1,101,100) 
random_y= np.random.randint(1,101,100) 
fig16 = px.bar(random_x, random_y)

df7 = px.data.iris()
fig17 = px.bar(df7, x="sepal_width", y="sepal_length")
fig18 = px.bar(df7, x="sepal_width", y="sepal_length", color="species",
            hover_data=['petal_width'], barmode = 'stack')


# (green) contribution graph
def load_data():
    data = pd.read_csv('data/kisho_data.csv')
    data['年月日'] = pd.to_datetime(data['年月日'])
    return data

# 日付を基に週番号と曜日を計算
data3 = load_data()
data3['week'] = data3['年月日'].apply(lambda x: x.isocalendar()[1])
data3['day_of_week'] = data3['年月日'].dt.dayofweek

# ピボットテーブルを作成して行列を転置
temperature_matrix = data3.pivot_table(values='最高気温(℃)', index='week', columns='day_of_week', aggfunc='mean').fillna(0)
#temperature_matrix = data3.pivot_table(values='降水量の合計(mm)', index='week', columns='day_of_week', aggfunc='mean').fillna(0)
temperature_matrix = temperature_matrix.T
custom_colorscale = [[0, 'black'],[1, 'green']]
#custom_colorscale = [[0, 'black'],[1, 'lightgreen']]

# Plotlyでヒートマップを作成（色を反転）
fig19 = go.Figure(data=go.Heatmap(
    z=temperature_matrix.values,
    x=temperature_matrix.columns,
    y=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
    colorscale=custom_colorscale,
    #colorscale='Greens_r'
    showscale=True
))

# グラフのレイアウトを設定して、セルを正方形にする
fig19.update_layout(
    title='Weekly Temperature Heatmap',
    xaxis_nticks=52,
    yaxis_nticks=7,
    yaxis_title='Day of the Week',
    xaxis_title='Week',
    xaxis=dict(
        tickmode='array',
        tickvals=list(range(1, 53)),
        ticktext=[str(i) for i in range(1, 53)]
    ),
    yaxis=dict(
        tickmode='array',
        tickvals=list(range(7)),
        #ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        ticktext=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
        scaleanchor='x',  # Make y-axis scale anchor to x-axis to make cells square
        scaleratio=1     # Ensure the ratio is 1 to make cells square
    ),
    autosize=False,
    width=1400,
    height=300
)

# 2
# ピボットテーブルを作成して行列を転置
temperature_matrix = data3.pivot_table(values='最高気温(℃)', index='week', columns='day_of_week', aggfunc='mean').fillna(0)
#temperature_matrix = data3.pivot_table(values='降水量の合計(mm)', index='week', columns='day_of_week', aggfunc='mean').fillna(0)
temperature_matrix = temperature_matrix.T
custom_colorscale = [[0, 'black'],[1, 'green']]

# Create the heatmap with gaps
z_values = rainfall_matrix_transposed.values
z_with_gaps = np.zeros((z_values.shape[0] * 2, z_values.shape[1] * 2)) * np.nan
z_with_gaps[::2, ::2] = z_values

fig20 = go.Figure(data=go.Heatmap(
    z=z_with_gaps,
    x0=0.5,
    dx=1,
    y0=0.5,
    dy=1,
    colorscale=custom_colorscale,
    showscale=True,
    zmin=rainfall_matrix_transposed.values.min(),
    zmax=rainfall_matrix_transposed.values.max()
))

fig20.update_layout(
    title='Weekly Rainfall Heatmap (Transposed and Color Reversed)',
    xaxis_nticks=52,
    yaxis_nticks=7,
    yaxis_title='Day of the Week',
    xaxis_title='Week',
    xaxis=dict(
        tickmode='array',
        tickvals=np.arange(0.5, len(rainfall_matrix.columns) + 0.5, 1),
        ticktext=[str(i) for i in range(1, 53)]
    ),
    yaxis=dict(
        tickmode='array',
        tickvals=np.arange(0.5, 7 + 0.5, 1),
        #ticktext=['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        ticktext=['Sat', 'Fri', 'Thu', 'Wed', 'Tue', 'Mon', 'Sun'],
        scaleanchor='x',  # Make y-axis scale anchor to x-axis to make cells square
        scaleratio=1     # Ensure the ratio is 1 to make cells square
    ),
    autosize=False,
    width=1400,
    height=400
)



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
right.subheader('ヒストグラム' + vars2_selected)
right.plotly_chart(fig8)

st.subheader('日経225すべて')
st.plotly_chart(fig5)
st.subheader('高校科目の相関行列')
st.plotly_chart(fig_corr2)

left_column2, right_column2 = st.columns(2)
left_column2.subheader('円グラフ')
left_column2.plotly_chart(fig9)
right_column2.subheader('棒グラフ')
right_column2.plotly_chart(fig10)


st.subheader('Choropleth map using GeoJSON')
st.plotly_chart(fig11)
st.subheader('Choropleth Maps with goChoropleth')
st.plotly_chart(fig12)
st.subheader('Choropleth Maps with goChoropleth')
st.plotly_chart(fig13)

st.subheader('treemap')
st.plotly_chart(fig14)
st.subheader('filled area chart')
st.plotly_chart(fig15)
st.subheader('bar chart')
st.plotly_chart(fig16)
st.subheader('bar chart with dataframe')
st.plotly_chart(fig17)
st.subheader('stack bar chart with dataframe')
st.plotly_chart(fig18)

st.subheader('Weekly Temperature Heatmap')
st.plotly_chart(fig19)
st.subheader('Weekly Temperature Heatmap')
st.plotly_chart(fig20)
