import pandas as pd
import plotly.express as px
import streamlit as st
from io import StringIO

kyoto_pop_text = """A,B
1,5
2,6
3,7
4,8"""
kyoto_pop = pd.read_csv(StringIO(kyoto_pop_text))
st.table(kyoto_pop)

#st.subheader('tabs')
#tab1, tab2, tab3 = st.tabs(["Cat", "Dog", "Owl"])
#with tab1:
#    st.header("A cat")
#    st.image("https://static.streamlit.io/examples/cat.jpg", width=200)
#with tab2:
#    st.header("A dog")
#    st.image("https://static.streamlit.io/examples/dog.jpg", width=200)
#with tab3:
#    st.header("An owl")
#    st.image("https://static.streamlit.io/examples/owl.jpg", width=200)

st.subheader('columns')
col1, col2, col3 = st.columns(3)
with col1:
    st.header("A cat")
    st.latex(r'''\sum_{k=0}^{n-1} ar^k = a \left(\frac{1-r^{n}}{1-r}\right)''')
with col2:
    st.header("A dog")
    st.image("https://static.streamlit.io/examples/dog.jpg")
with col3:
    st.header("An owl")
    st.image("https://static.streamlit.io/examples/owl.jpg")

st.subheader('container')
container = st.container(border=True)
container.write("This is inside the container")
st.write("This is outside the container")
# Now insert some more in the container
container.write("This is inside too")

st.subheader('expander')
st.bar_chart({"data": [1, 5, 2, 6, 2, 1]})
with st.expander("See explanation"):
    st.write('''
        The chart above shows some numbers I picked for you.
        I rolled actual dice for these, so they're *guaranteed* to
        be random.
    ''')
    st.image("https://static.streamlit.io/examples/dice.jpg")

st.subheader('popover')
with st.popover("Open popover"):
    st.markdown("Hello World 👋")
    name = st.text_input("What's your name?")
st.write("Your name:", name)

popover = st.popover("Filter items")
red = popover.checkbox("Show red items.", True)
blue = popover.checkbox("Show blue items.", True)
if red:
    st.write(":red[This is a red item.]")
if blue:
    st.write(":blue[This is a blue item.]")


st.subheader('sidebar')
# Using object notation
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)
# Using "with" notation
with st.sidebar:
    add_radio = st.radio(
        "Choose a shipping method",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )

import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import json
from io import StringIO
import openpyxl
import xlrd

land_price = pd.read_csv("data/L01-2024P-2K_26.csv", encoding="cp932")
land_price.loc[:, ["経度", "緯度"]] = land_price.loc[:, ["経度", "緯度"]] / 3600
st.write(land_price)

fig5 = px.scatter_mapbox(
    land_price,
    lat="緯度",
    lon="経度",
    size="価格R06",
    color="標準地名",
    #hover_name="市区町村名",
    #hover_data=["所在並びに地番"],
    center={"lat": 35.02, "lon": 135.76},
    zoom=10, opacity=0.5,
    width=800, height=800,
    mapbox_style="carto-positron",
)
st.plotly_chart(fig5)

# data
#with open("data/kokusei_R2.xlsx", encoding = 'utf-8') as f:
#    geojson = json.load(f)
df1 = pd.read_excel('data/kokusei_R2_v2.xlsx', sheet_name=0, index_col=None, skiprows = [0,1,3,4,5,6,7])
df2 = pd.read_excel('data/kokusei_R2_v2.xlsx', sheet_name=1, index_col=None, skiprows = [0,1,2,4,5,6,7,8])
st.write(df1.columns)

df1 = df1[df1["地域都道府県名"] == "26_京都府"]
df1 = df1[df1["地域市などの別（地域識別コード）"] == 0]
df1["地域都道府県・市区町村名"] = df1["地域都道府県・市区町村名"].str.replace(r'^\d+_', '', regex=True)
st.write(df1)

df = df1[["地域都道府県・市区町村名","総人口（男女別）総数（人）"]]
df["総人口（男女別）総数（人）"] = pd.to_numeric(df["総人口（男女別）総数（人）"], errors='coerce') # additional
st.write(df)
#st.write(df2)

# データフレームをCSVファイルに書き出し
df.to_csv("population_data.csv", index=False)
df = pd.read_csv("population_data.csv")
print(df.dtypes)

# geojson
with open("data/N03-23_26_230101.geojson", encoding = 'utf-8') as f:
    geojson = json.load(f)

fig2 = px.choropleth_mapbox(
    df,
    geojson=geojson,
    locations="地域都道府県・市区町村名",
    color="総人口（男女別）総数（人）",
    hover_name="地域都道府県・市区町村名",
    featureidkey="properties.N03_004",
    mapbox_style="carto-positron",
    center={"lat": 35.02, "lon": 135.76},
    zoom=9, opacity=0.5,
    color_continuous_scale="Viridis",  # 連続的なカラースケールを明示的に指定
    width=800, height=800,
)

# data frame
kyoto_pop_text = """市区町村,総数
京都市北区,117165
京都市上京区,83832
京都市左京区,166039
京都市中京区,110488
京都市東山区,36602
京都市下京区,82784
京都市南区,101970
京都市右京区,202047
京都市伏見区,277858
京都市山科区,135101
京都市西京区,149837"""
kyoto_pop = pd.read_csv(StringIO(kyoto_pop_text))
#st.write(kyoto_pop)

fig1 = px.choropleth_mapbox(
    kyoto_pop, geojson=geojson,
    locations="市区町村",
    color="総数",
    hover_name="市区町村",
    featureidkey="properties.N03_004",
    mapbox_style="carto-positron",
    center={"lat": 35.02, "lon": 135.76},
    zoom=9, opacity=0.5,
    width=800, height=800,
)
#st.plotly_chart(fig1)

# toyama women
toyama_pop_text = """市区町村,若年女性人口減少率
富山市,-27.7
高岡市,-41.8
魚津市,-46.9
氷見市,-63.0 
滑川市,-30.3 
黒部市,-37.1 
砺波市,-35.5 
小矢部市,-49.3 
南砺市,-55.4 
射水市,-31.9 
舟橋村,-22.6 
上市町,-59.0 
立山町,-46.0 
入善町,-56.3 
朝日町,-64.0"""
toyama_pop = pd.read_csv(StringIO(toyama_pop_text))
#st.write(toyama_pop)

with open("data/N03-20240101_16.geojson", encoding = 'utf-8') as f:
    geojson2 = json.load(f)

fig6 = px.choropleth_mapbox(
    toyama_pop,
    geojson=geojson2,
    locations="市区町村",
    color="若年女性人口減少率",
    hover_name="市区町村",
    featureidkey="properties.N03_004",
    mapbox_style="carto-positron",
    center={"lat": 36.64, "lon": 137.21}, #36.642108540104545, 137.21097192980957
    zoom=8, opacity=0.5,
    color_continuous_scale="Viridis",  # 連続的なカラースケールを明示的に指定
    width=800, height=800,
)


#### reference -> https://python.monzblog.com/plotly_express_scatter_mapbox/
df = px.data.carshare()
fig3 = px.scatter_mapbox(
    df, 
    lat="centroid_lat", 
    lon="centroid_lon", 
    zoom=10,
    #mapbox_style="open-street-map"
    mapbox_style="carto-positron",
)
fig3.update_layout(margin={"r":0,"t":0,"l":0,"b":0}) #余白消しのため追記

fig4 = px.scatter_mapbox(df, lat="centroid_lat", lon="centroid_lon",zoom=10,
                        mapbox_style="open-street-map",color="peak_hour")

st.subheader('Choropleth Map in Kyoto district (selective)')
st.plotly_chart(fig2)

st.subheader('scatter_mapbox')
st.write(df)
st.plotly_chart(fig3)
st.plotly_chart(fig4)
st.plotly_chart(fig6)
