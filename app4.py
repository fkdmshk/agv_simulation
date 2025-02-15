import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.graph_objects as go

# AGVの経路
agv_path = [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5),  # → 倉庫
            (5, 4), (5, 3), (5, 2), (5, 1), (5, 0), (6, 0),  # ↓ 加工機
            (7, 0), (8, 0), (9, 0)]  # → 出口

# 設備リスト（位置, 名称, 滞留時間）
machines = {
    (2, 4): ("倉庫", 3),
    (6, 4): ("加工機", 5),
    (8, 2): ("表面処理", 4),
    (4, 1): ("組立ライン", 6)
}

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
    for (x, y), (name, _) in machines.items():
        fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers+text",
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

    # センサー値データ保存用
    sensor_data = {"時間（秒）": [], "バッテリー（%）": [], "温度（°C）": [], "距離（m）": [], "速度（m/s）": []}

    for step, (agv_x, agv_y) in enumerate(agv_path):
        if stop_simulation:
            st.write("🛑 シミュレーションを停止しました")
            break

        # 設備の滞留時間をチェック
        if (agv_x, agv_y) in machines:
            machine_name, dwell_time = machines[(agv_x, agv_y)]
            st.write(f"🕒 AGVが「{machine_name}」に到達 - {dwell_time}秒滞留")
            time.sleep(dwell_time)

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

if __name__ == "__main__":
    main()
