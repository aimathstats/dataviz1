import streamlit as st

st.set_page_config(layout="wide")

st.title("簡単避難所マップ by streamlit")
st.write("デフォルト現在地：京都府立植物園北門")

list = [
  {"latitude":35.051095034877825, "longitude":135.76477636253375}, #デフォルト現在地（植物園）
  {"latitude":35.04289379, "longitude":135.75676882}, #紫明小学校
  {"latitude":35.05044293, "longitude":135.75418841}, #元町小学校
]

st.map(list)



##### jsで現在地取得してfoliumマップに表示（google api不使用）
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import get_geolocation

st.title("現在地を取得して地図に表示")
st.write("ブラウザに位置情報の使用を許可してください。")

loc = get_geolocation()  # JavaScriptで現在地を取得（navigator.geolocation）

if loc:
    lat = loc["coords"]["latitude"]
    lon = loc["coords"]["longitude"]
    st.success(f"現在地：緯度 {lat:.5f}, 経度 {lon:.5f}")
    m = folium.Map(location=[lat, lon], zoom_start=19)
    folium.Marker([lat, lon], tooltip="現在地", icon=folium.Icon(color="red")).add_to(m)
    st_folium(m, height=500, width=500)
else:
    st.warning("位置情報を取得中...またはブラウザで位置情報が許可されていません。")

st.write("取得した現在地情報（jsonファイル）") # 確認のため、アプリ上に表示
st.json(loc)



##### Google map api から座標に基づくルート情報を取得して表示
import requests
import polyline  # Googleのポリラインデータのデコード
import random

st.title("ルート表示：北大路～京都御所")
st.write("by Google Maps Directions API")
API_KEY = st.secrets["GOOGLE_API_KEY"]

# 出発地と到着地の座標
origin_coords = "35.04540,135.75870"      # 北大路駅
if "destination_coords" not in st.session_state:
    lat = 35.02332 + random.uniform(-0.003, 0.003)
    lon = 135.75953 + random.uniform(-0.003, 0.003)
    st.session_state.destination_coords = f"{lat:.6f},{lon:.6f}"
destination_coords = st.session_state.destination_coords
#destination_coords = "35.02332,135.75953" # 京都御所

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
    # ポリラインをデコード
    polyline_str = data["routes"][0]["overview_polyline"]["points"]
    decoded_path = polyline.decode(polyline_str)

    # 地図の中心をルート中点に、地図作成、ルート描画、マーカー追加
    midpoint = decoded_path[len(decoded_path)//2]
    m = folium.Map(location=midpoint, zoom_start=14)
    folium.PolyLine(decoded_path, color="blue", weight=5).add_to(m)
    folium.Marker(decoded_path[0], tooltip="出発", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(decoded_path[-1], tooltip="到着", icon=folium.Icon(color="red")).add_to(m)

    # 地図表示
    st_folium(m, width=700, height=500)

# 確認のため，アプリ上にデータ表示
st.write("取得したデータ")
st.json(data)



##### Google map places API
st.title("北大路駅周辺のレストラン（簡単版）")
st.write("by Google Places API")
center_lat, center_lng = 35.04540, 135.75870 # 北大路駅

# Places API Nearby Search リクエスト
places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
params = {
    "location": f"{center_lat},{center_lng}",
    "radius": 500,
    "type": "restaurant",  # レストランに限定
    "key": API_KEY
}

### type list
# レストラン `restaurant`        
# カフェ   `cafe`              
# コンビニ  `convenience_store` 
# バス停  `bus_station`       
# 美術館   `museum`            
# 駐車場　parking"

res = requests.get(places_url, params=params)
data = res.json()

m = folium.Map(location=[center_lat, center_lng], zoom_start=16)
folium.Marker([center_lat, center_lng], tooltip="北大路駅中心").add_to(m)

# レストラン表示
if data.get("status") == "OK":
    for place in data.get("results", []):
        name = place.get("name")
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]
        folium.Marker([lat, lng], tooltip=name, icon=folium.Icon(color="red", icon="cutlery", prefix="fa")).add_to(m)
else:
    st.error(f"Places APIエラー: {data.get('status')}")
    st.json(data)

st_folium(m, width=700, height=500)



#### 人気順表示
st.title("北大路駅周辺のレストラン（人気順表示）")
center_lat, center_lng = 35.04540, 135.75870 # 北大路駅
places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
params = {
    "location": f"{center_lat},{center_lng}",
    "rankby": "prominence",   # 評価・レビューなどを加味した人気順
    "radius": 500,            # 半径（prominenceの場合でも使える）
    "type": "restaurant",
    "key": API_KEY
}

res = requests.get(places_url, params=params)
data = res.json()
m = folium.Map(location=[center_lat, center_lng], zoom_start=16)
folium.Marker([center_lat, center_lng], tooltip="北大路駅中心", icon=folium.Icon(color="blue")).add_to(m)

if data.get("status") == "OK":
    for i, place in enumerate(data.get("results", []), start=1):
        name = place.get("name", "名称不明")
        rating = place.get("rating", "不明")
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]
        tooltip = f"{i}. {name}（評価: {rating}）" # modified
        folium.Marker([lat, lng], tooltip=tooltip, icon=folium.Icon(color="red", icon="cutlery", prefix="fa")).add_to(m)
else:
    st.error(f"Places APIエラー: {data.get('status')}")
    st.json(data)

st_folium(m, width=700, height=500)



##### 駐車場リスト書き出し
st.title("北大路駅周辺の駐車場（評価順）")
center_lat, center_lng = 35.04540, 135.75870 # 北大路駅

# APIリクエスト設定
places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
params = {
    "location": f"{center_lat},{center_lng}",
    "radius": 800,
    "type": "parking",
    "rankby": "prominence",
    "key": API_KEY
}

res = requests.get(places_url, params=params)
data = res.json()
m = folium.Map(location=[center_lat, center_lng], zoom_start=16)
folium.Marker([center_lat, center_lng], tooltip="北大路駅中心", icon=folium.Icon(color="blue")).add_to(m)
place_list = []

if data.get("status") == "OK":
    for i, place in enumerate(data.get("results", []), start=1):
        name = place.get("name", "名称不明")
        rating = place.get("rating", "評価なし")
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]
        place_id = place.get("place_id")

        # Google Maps の URL を生成
        gmap_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        tooltip = f"{i}. {name}（評価: {rating}）"
        folium.Marker([lat, lng], tooltip=tooltip, icon=folium.Icon(color="purple", icon="info-sign")).add_to(m)
        place_list.append(f"{i}. [{name}]({gmap_url}) - 評価: {rating}")

else:
    st.error(f"Places APIエラー: {data.get('status')}")
    st.json(data)

st_folium(m, width=700, height=500)
st.markdown("一覧（Googleマップリンク付き）") # リスト表示（地図の下）
for entry in place_list:
    st.markdown(entry)



##### ポップアップで詳細表示
st.title("京都御所周辺の駐車場（クリックで詳細表示）")
center_lat, center_lng = 35.025400, 135.762116
places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
params = {
    "location": f"{center_lat},{center_lng}",
    "radius": 800,
    "type": "parking",
    "rankby": "prominence",
    "key": API_KEY
}

res = requests.get(places_url, params=params)
data = res.json()
m = folium.Map(location=[center_lat, center_lng], zoom_start=16)
folium.Marker([center_lat, center_lng], tooltip="京都御所中心", icon=folium.Icon(color="blue")).add_to(m)

place_list = []

if data.get("status") == "OK":
    results = data.get("results", [])[:10] # 10件のみ表示

    for i, place in enumerate(results, start=1):
        name = place.get("name", "名称不明")
        rating = place.get("rating", "評価なし")
        lat = place["geometry"]["location"]["lat"]
        lng = place["geometry"]["location"]["lng"]
        place_id = place.get("place_id")
        gmap_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

        # HTMLポップアップを作成
        popup_html = f'''
        <b>{i}. {name}</b><br>
        評価: {rating}<br>
        <a href="{gmap_url}" target="_blank">Googleマップで見る</a>
        '''

        folium.Marker(
            [lat, lng],
            tooltip=f"{name}（クリックで詳細）",
            popup=folium.Popup(popup_html, max_width=300),
            icon=folium.Icon(color="purple", icon="info-sign")
        ).add_to(m)

        place_list.append(f"**{i}. [{name}]({gmap_url})**  \n評価: {rating}")

else:
    st.error(f"Places APIエラー: {data.get('status')}")
    st.json(data)

st_folium(m, width=700, height=500)
st.markdown("上位10件の駐車場リスト")
for entry in place_list:
    st.markdown(entry)


