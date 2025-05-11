import streamlit as st

st.set_page_config(layout="wide")

list = [
  {"latitude":35.051095034877825, "longitude":135.76477636253375}, #デフォルト現在地（植物園）
  {"latitude":35.04289379, "longitude":135.75676882}, #紫明小学校
  {"latitude":35.05044293, "longitude":135.75418841}, #元町小学校
]

st.title("簡単避難所マップ by streamlit")
st.write("デフォルト現在地：京都府立植物園北門")
st.map(list)


##############################
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.title("現在地を取得して地図に表示")
st.write("ブラウザに位置情報の使用を許可してください。")

# JavaScriptで現在地を取得（navigator.geolocation）
loc = get_geolocation()

if loc:
    lat = loc["coords"]["latitude"]
    lon = loc["coords"]["longitude"]
    st.success(f"現在地：緯度 {lat:.5f}, 経度 {lon:.5f}")
    # Foliumマップ作成
    m = folium.Map(location=[lat, lon], zoom_start=19)
    folium.Marker([lat, lon], tooltip="現在地", icon=folium.Icon(color="red")).add_to(m)
    st_folium(m, height=500, width=500)
else:
    st.warning("位置情報を取得中...またはブラウザで許可されていません。")


###############################################
# google map api
import requests
import polyline  # Googleのポリラインデータのデコード
import numpy as np

st.title("Google Maps Directions API")
API_KEY = st.secrets["GOOGLE_API_KEY"]

# 出発地と到着地の座標
origin_coords = "35.04540,135.75870"      # 北大路駅
destination_coords = "35.02332,135.75953" # 京都御所
#center_lat, center_lon = 35.02332, 135.75953
#a = np.random.randn(1,2)/[10,10] + [center_lat, center_lon] 
#destination_coords = f"a[0],a[1]"
import random
#e1 = random.uniform(-0.003, 0.003)
#e2 = random.uniform(-0.003, 0.003)
#destination_coords = f"{35.02332 + e1:.6f},{135.75953 + e2:.6f}"
#destination_coords = f"{35.02332 + random.uniform(-0.003, 0.003):.6f}," \
#                     f"{135.75953 + random.uniform(-0.003, 0.003):.6f}"
if "destination_coords" not in st.session_state:
    lat = 35.025 + random.uniform(-0.003, 0.003)
    lon = 135.762 + random.uniform(-0.003, 0.003)
    st.session_state.destination_coords = f"{lat:.6f},{lon:.6f}"
destination_coords = st.session_state.destination_coords

# Directions APIリクエスト作成
url = "https://maps.googleapis.com/maps/api/directions/json"
params = {
    "origin": origin_coords,
    "destination": destination_coords,
    "mode": "walking", #driving
    "key": API_KEY
}

# APIリクエスト送信
res = requests.get(url, params=params)
data = res.json()

# レスポンスの確認
if data.get("status") != "OK":
    st.error(f"Directions APIの取得に失敗しました: {data.get('status')}")
    st.json(data)  # エラーメッセージの中身を表示

else:
    #print(data)
    # ポリラインをデコード
    polyline_str = data["routes"][0]["overview_polyline"]["points"]
    decoded_path = polyline.decode(polyline_str)

    # 地図の中心（ルート中点）
    midpoint = decoded_path[len(decoded_path)//2]
    m = folium.Map(location=midpoint, zoom_start=13)

    # ルート描画
    folium.PolyLine(decoded_path, color="blue", weight=5).add_to(m)

    # マーカー追加
    folium.Marker(decoded_path[0], tooltip="出発", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(decoded_path[-1], tooltip="到着", icon=folium.Icon(color="red")).add_to(m)

    # 地図表示
    st_folium(m, width=700, height=500)

