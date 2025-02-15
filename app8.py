import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import osmnx as ox
import networkx as nx

# 🌍 住所から緯度経度を取得
geolocator = Nominatim(user_agent="logistics_app")

def get_coordinates(address):
    location = geolocator.geocode(address)
    return (location.latitude, location.longitude) if location else None

# 🚛 ユーザー入力（出発地・目的地）
st.sidebar.subheader("🌍 運送元・運送先の設定")
source_address = st.sidebar.text_input("🚚 運送元（住所）", "新潟県新潟市中央区")
destination_address = st.sidebar.text_input("🏭 運送先（住所）", "大阪府堺市")

# 初期位置の座標取得
source_coords = get_coordinates(source_address)
destination_coords = get_coordinates(destination_address)

if not source_coords or not destination_coords:
    st.sidebar.error("❌ 住所が見つかりません。正しい住所を入力してください。")
    st.stop()

# 🚚 トラックの移動シミュレーション（グローバル変数）
truck_position = list(source_coords)

def move_truck(truck_pos, destination_pos, step=0.05):
    lat_step = (destination_pos[0] - truck_pos[0]) * step
    lon_step = (destination_pos[1] - truck_pos[1]) * step
    truck_pos[0] += lat_step
    truck_pos[1] += lon_step
    return truck_pos

# 🏭 **工場内の設定**
machines = {
    "倉庫": ((2, 4), "倉庫"),
    "加工機": ((6, 4), "加工機"),
    "表面処理": ((8, 2), "表面処理"),
    "組立ライン": ((4, 1), "組立ライン")
}

# プルダウンメニューで順番を選択
st.sidebar.subheader("🔄 AGVの巡回順序設定")
machine_list = list(machines.keys())
order = [
    st.sidebar.selectbox(f"巡回順序 {i+1}:", machine_list, index=i)
    for i in range(4)
]

# 各工程の滞留時間
st.sidebar.subheader("⏳ 各工程の滞留時間設定（秒）")
dwell_times = {machine: st.sidebar.number_input(f"{machine} 滞留時間:", min_value=1, max_value=10, value=3, step=1) for machine in machines.keys()}

# センサー値の初期化
sensor_data = {"時間（秒）": [], "バッテリー（%）": [], "温度（°C）": [], "距離（m）": [], "速度（m/s）": []}

def generate_sensor_data(step):
    battery = max(100 - step, 10)
    temperature = np.random.uniform(25, 40)
    distance = np.random.uniform(0.5, 5.0)
    speed = np.random.uniform(0.8, 1.5)
    return battery, temperature, distance, speed

# 🏭 工場レイアウト描画
def draw_factory_layout(agv_x, agv_y):
    fig = go.Figure()
    for name, (pos, _) in machines.items():
        fig.add_trace(go.Scatter(x=[pos[0]], y=[pos[1]], mode="markers+text",
                                 marker=dict(size=20, color="red"),
                                 text=[name], textposition="top center", name=name))
    fig.add_trace(go.Scatter(x=[agv_x], y=[agv_y], mode="markers",
                             marker=dict(size=15, color="blue"), name="AGV"))
    fig.update_layout(title="🏭 工場レイアウト", xaxis=dict(range=[0, 10]), yaxis=dict(range=[0, 5]))
    return fig

# 🚀 メイン処理
def main():
    global truck_position  # ← 修正：グローバル変数を参照

    st.title("🚛 物流 + 🏭 工場シミュレーション")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📍 トラックの移動（日本地図）")
        map_placeholder = st.empty()

    with col2:
        st.subheader("🏭 工場のマップ（AGV移動）")
        factory_plot = st.empty()

    st.subheader("📊 センサー値の推移")
    sensor_chart = st.line_chart([])

    stop_simulation = st.checkbox("🛑 STOP", value=False)

    # 🚛 トラック移動
    step_count = 0
    while step_count < 30:  # 🚀 **30秒以内にトラック移動を完了**
        if stop_simulation:
            st.write("🛑 シミュレーションを停止しました")
            return

        truck_position = move_truck(truck_position, destination_coords)

        # 地図更新
        df_map = pd.DataFrame([
            {"latitude": source_coords[0], "longitude": source_coords[1], "type": "運送元"},
            {"latitude": destination_coords[0], "longitude": destination_coords[1], "type": "運送先"},
            {"latitude": truck_position[0], "longitude": truck_position[1], "type": "トラック"},
        ])
        map_placeholder.map(df_map)

        time.sleep(1)
        step_count += 1

    # 🏭 **工場内シミュレーション**
    agv_path = [machines[m][0] for m in order]
    step = 0

    while step < 30:  # 🚀 **30秒で工場シミュレーションを完了**
        for agv_x, agv_y in agv_path:
            if stop_simulation:
                st.write("🛑 シミュレーションを停止しました")
                return

            for name, (pos, _) in machines.items():
                if (agv_x, agv_y) == pos:
                    st.write(f"🕒 AGVが「{name}」に到達 - {dwell_times[name]}秒滞留")
                    time.sleep(dwell_times[name])

            # センサー値更新
            battery, temp, distance, speed = generate_sensor_data(step)
            sensor_data["時間（秒）"].append(step)
            sensor_data["バッテリー（%）"].append(battery)
            sensor_data["温度（°C）"].append(temp)
            sensor_data["距離（m）"].append(distance)
            sensor_data["速度（m/s）"].append(speed)

            # 画面更新
            factory_plot.plotly_chart(draw_factory_layout(agv_x, agv_y), use_container_width=True)
            sensor_chart.line_chart(pd.DataFrame(sensor_data).set_index("時間（秒）"))

            time.sleep(1)
            step += 1

if __name__ == "__main__":
    main()

