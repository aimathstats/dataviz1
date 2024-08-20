import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
import json
from io import StringIO
import openpyxl
import xlrd

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
st.write(kyoto_pop)

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
#st.subheader('Choropleth Map in Kyoto district')
#st.plotly_chart(fig1)

st.subheader('Choropleth Map in Kyoto district (selective)')
st.plotly_chart(fig2)

