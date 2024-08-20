import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import json
from io import StringIO

# geojson
with open("data/N03-23_26_230101.geojson", encoding = 'utf-8') as f:
    geojson = json.load(f)

# data frame
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
    shiga_pop, geojson=geojson,
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
st.write(kyoto_pop)

fig13 = px.choropleth_mapbox(
    kyoto_pop, geojson=geojson,
    locations="市区町村",
    color="総数",
    hover_name="市区町村",
    featureidkey="properties.N03_004",
    mapbox_style="carto-positron",
    zoom=9,
    center={"lat": 35.02, "lon": 135.76},
    opacity=0.5,
    width=800,
    height=800,
)

st.subheader('Choropleth Map in Kyoto district')
st.plotly_chart(fig13)

