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

# Directions APIでルート取得
directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={current_location[0]},{current_location[1]}&destination={destination[0]},{destination[1]}&mode=driving&key={GOOGLE_MAPS_API_KEY}"
response = requests.get(directions_url).json()

# ルートのpolylineを描画
if response['status'] == 'OK':
    points = response['routes'][0]['overview_polyline']['points']
    import polyline
    decoded = polyline.decode(points)
    folium.PolyLine(decoded, color="blue", weight=5, opacity=0.7).add_to(m)

# Places APIで周辺施設取得（例：レストラン）
places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={destination[0]},{destination[1]}&radius=500&type=restaurant&key={GOOGLE_MAPS_API_KEY}"
places = requests.get(places_url).json()

for place in places.get('results', []):
    lat = place['geometry']['location']['lat']
    lng = place['geometry']['location']['lng']
    name = place['name']
    folium.Marker([lat, lng], tooltip=name, icon=folium.Icon(color="green")).add_to(m)

# 表示
st.title("Google Maps APIアプリ")
st_folium(m, width=700)

#####
from streamlit_js_eval import streamlit_js_eval
st.title("現在地の取得")
# 現在地の取得
result = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition", key="get_geolocation")
st.write(result)



#####
from streamlit_js_eval import get_geolocation

st.set_page_config(page_title="現在地表示", layout="centered")

st.title("📍 現在地を取得して地図に表示する")
st.write("ブラウザに位置情報の使用を許可してください。")

# JavaScriptで現在地を取得（navigator.geolocation）
loc = get_geolocation()

if loc:
    lat = loc["coords"]["latitude"]
    lon = loc["coords"]["longitude"]
    st.success(f"現在地：緯度 {lat:.5f}, 経度 {lon:.5f}")

    # Foliumマップ作成
    m = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon], tooltip="現在地", icon=folium.Icon(color="red")).add_to(m)

    st_folium(m, height=500, width=700)

else:
    st.warning("位置情報を取得中...またはブラウザで許可されていません。")
