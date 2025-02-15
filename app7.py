import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.graph_objects as go
from geopy.geocoders import Nominatim

# 🌍 住所から緯度経度を取得
geolocator = Nominatim(user_agent="logistics_app")

def get_coordinates(address):
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None

# 🚛 ユーザー入力（出発地・目的地）
st.sidebar.subheader("🌍 運送元・運送先の設定")
source_address = st.sidebar.text_input("🚚 運送元（住所）", "新潟県新潟市中央区")
destination_address = st.sidebar.text_input("🏭 運送先（住所）", "大阪府堺市")

# 初期位置の座標取得
source_coords = get_coordinates(source_address)
destination_coords = get_coordinates(destination_address)

if not source_coords or not destination_coords:
    st.sidebar.error("❌ 住所が見つかりません。正しい住所を入力してください。")

# 🚚 トラックの移動シミュレーション
truck_position = list(source_coords)

def move_truck(truck_pos, destination_pos, step=0.1):
    lat_step = (destination_pos[0] - truck_pos[0]) * step
    lon_step = (destination_pos[1] - truck_pos[1]) * step
    truck_pos[0] += lat_step
    truck_pos[1] += lon_step
    return truck_pos

# 🚀 メイン処理
def main():
    st.title("🚛 物流シミュレーション（新潟 ➝ 大阪）")

    # 🌍 地図の表示
    st.subheader("📍 現在の位置（トラック・船）")
    map_placeholder = st.empty()

    # 🛑 停止ボタン
    stop_simulation = st.checkbox("🛑 STOP", value=False)

    step_count = 0
    while True:
        if stop_simulation:
            st.write("🛑 シミュレーションを停止しました")
            break

        # 🚚 トラックを移動
        global truck_position
        truck_position = move_truck(truck_position, destination_coords, step=0.02)

        # 📍 地図データ更新
        df = pd.DataFrame([
            {"latitude": source_coords[0], "longitude": source_coords[1], "type": "運送元"},
            {"latitude": destination_coords[0], "longitude": destination_coords[1], "type": "運送先"},
            {"latitude": truck_position[0], "longitude": truck_position[1], "type": "トラック"},
        ])

        # 🌍 地図を更新
        map_placeholder.map(df)

        time.sleep(1)  # 更新間隔
        step_count += 1

        # 目的地到着で終了
        if abs(truck_position[0] - destination_coords[0]) < 0.01 and abs(truck_position[1] - destination_coords[1]) < 0.01:
            st.write("✅ トラックが目的地に到着しました！")
            break

if __name__ == "__main__":
    main()


