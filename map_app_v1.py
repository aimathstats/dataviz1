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
