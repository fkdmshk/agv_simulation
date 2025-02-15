import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.graph_objects as go

# 設備リスト（位置, 名称）
machines = {
    1: ((2, 4), "倉庫"),
    2: ((6, 4), "加工機"),
    3: ((8, 2), "表面処理"),
    4: ((4, 1), "組立ライン")
}

# デフォルトの巡回順序
default_order = [1, 2, 3, 4]

# AGVの経路を動的に生成
def generate_agv_path(order):
    path = []
    for step in order:
        path.append(machines[step][0])  # 設備の座標を取得
    return path

# センサー値をランダム生成（仮データ）
def generate_sensor_data(step):
    battery = max(100 - step, 10)  # バッテリー残量（%）
    temperature = np.random.uniform(25, 40)  # 温度（°C）
    distance = np.random.uniform(0.5, 5.0)  # 障害物までの距離（m）
    speed = np.random.uniform(0.8, 1.5)  # 移動速度（m/s）
    return battery, temperature, distance, speed

# 工場レイアウトの描画
def draw_factory_layout(agv_x, agv_y):
    fig = go.Figure()

    # 設備をプロット
    for _, (pos, name) in machines.items():
        fig.add_trace(go.Scatter(x=[pos[0]], y=[pos[1]], mode="markers+text",
                                 marker=dict(size=20, color="red"),
                                 text=[name], textposition="top center", name=name))
    
    # AGVの位置をプロット
    fig.add_trace(go.Scatter(x=[agv_x], y=[agv_y], mode="markers",
                             marker=dict(size=15, color="blue"), name="AGV"))

    fig.update_layout(title="工場レイアウト", xaxis=dict(range=[0, 10]), yaxis=dict(range=[0, 5]))
    return fig

# メイン処理
def main():
    st.title("🚗 AGVシミュレーション")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏭 工場のマップ")
        factory_plot = st.empty()

    with col2:
        st.subheader("📊 センサー値の推移")
        sensor_chart = st.empty()

    # シミュレーション制御用
    stop_simulation = st.button("🛑 STOP")

    # ユーザー入力（巡回順序）
    st.sidebar.subheader("🔄 AGVの巡回順序設定")
    order = []
    for i in range(1, 5):
        order.append(st.sidebar.number_input(f"巡回順序 {i}:", min_value=1, max_value=4, value=default_order[i-1], step=1))

    # ユーザー入力（滞留時間）
    st.sidebar.subheader("⏳ 滞留時間設定（秒）")
    dwell_times = {}
    for key, (_, name) in machines.items():
        dwell_times[key] = st.sidebar.number_input(f"{name} 滞留時間:", min_value=1, max_value=10, value=3, step=1)

    # センサー値データ保存用
    sensor_data = {"時間（秒）": [], "バッテリー（%）": [], "温度（°C）": [], "距離（m）": [], "速度（m/s）": []}

    # シミュレーションループ
    agv_path = generate_agv_path(order)
    step = 0

    while not stop_simulation:
        for agv_x, agv_y in agv_path:
            if stop_simulation:
                st.write("🛑 シミュレーションを停止しました")
                return

            # 設備の滞留時間を適用
            for key, (pos, name) in machines.items():
                if (agv_x, agv_y) == pos:
                    st.write(f"🕒 AGVが「{name}」に到達 - {dwell_times[key]}秒滞留")
                    time.sleep(dwell_times[key])

            # センサー値を取得
            battery, temp, distance, speed = generate_sensor_data(step)

            # データを追加
            sensor_data["時間（秒）"].append(step)
            sensor_data["バッテリー（%）"].append(battery)
            sensor_data["温度（°C）"].append(temp)
            sensor_data["距離（m）"].append(distance)
            sensor_data["速度（m/s）"].append(speed)

            # 工場レイアウト更新
            factory_fig = draw_factory_layout(agv_x, agv_y)
            factory_plot.plotly_chart(factory_fig, use_container_width=True)

            # センサー値グラフ更新
            df = pd.DataFrame(sensor_data)
            sensor_chart.line_chart(df.set_index("時間（秒）"))

            # 更新間隔
            time.sleep(1)
            step += 1

if __name__ == "__main__":
    main()
