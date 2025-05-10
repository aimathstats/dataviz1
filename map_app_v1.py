import streamlit as st
#import numpy as np
#import pandas as pd

st.set_page_config(layout="wide")

pref_list = [
  {"latitude":35.051095034877825, "longitude":135.76477636253375}, #現在地（デフォルト）
  {"latitude":35.04289379, "longitude":135.75676882}, #紫明小学校
  {"latitude":35.05044293, "longitude":135.75418841}, #元町小学校
]
st.map(pref_list)
