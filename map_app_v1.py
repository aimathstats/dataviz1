import streamlit as st

st.set_page_config(layout="wide")

list = [
  {"latitude":35.051095034877825, "longitude":135.76477636253375}, #デフォルト現在地（植物園）
  {"latitude":35.04289379, "longitude":135.75676882}, #紫明小学校
  {"latitude":35.05044293, "longitude":135.75418841}, #元町小学校
]

st.title("避難所マップ　version 1")
st.map(list)
st.write("デフォルト現在地：京都府立植物園北門")
#st.write(list)


###############################################
# google map api
import folium
from streamlit_folium import st_folium
import requests

# Google Maps API Key
GOOGLE_MAPS_API_KEY = "GOOGLE_API_KEY"

# サンプルの現在地と目的地
current_location = (35.681236, 139.767125)  # 東京駅
destination = (35.689487, 139.691706)       # 新宿駅

# 地図作成
m = folium.Map(location=current_location, zoom_start=13)
folium.Marker(current_location, tooltip="現在地").add_to(m)
folium.Marker(destination, tooltip="目的地").add_to(m)
