import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.graph_objects as go

# --------------------------
# AGV の移動経路（左→下→右）
# --------------------------
agv_path = [(i, 5) for i in range(6)] + [(5, 5 - j) for j in range(6)] + [(i, 0) for i in range(6, 10)]

# --------------------------
# 工場設備の配置
# --------------------------
equipment = [
    {"name": "倉庫", "position": (2, 4), "color": "red"},
    {"name": "加工機", "position": (6, 4), "color": "red"},
    {"name": "表面処理", "position": (8, 2), "color": "red"},
    {"name": "組立ライン", "position": (4, 1), "color": "red"},
]

# --------------------------
# 工場レイアウトの初期設定
# --------------------------
def create_factory_layout():
    fig = go.Figure()

    # 設備を配置
    for eq in equipment:
        fig.add_trace(go.Scatter(
            x=[eq["position"][0]], y=[eq["position"][1]],
            mode="markers+text",
            marker=dict(size=20, color=eq["color"]),
            text=[eq["name"]],
            textposition="top center",
            name=eq["name"]
        ))

    # AGVの初期位置
    agv_x, agv_y = agv_path[0]
    fig.add_trace(go.Scatter(
        x=[agv_x], y=[agv_y], mode="markers",
        marker=dict(size=15, color="blue"), name="AGV"
    ))

    fig.update_layout(title="🏭 工場レイアウト",
                      xaxis=dict(range=[0, 10], title="X座標"),
                      yaxis=dict(range=[0, 5], title="Y座標"))
    return fig

# --------------------------
# センサー値の生成
# --------------------------
def generate_sensor_data():
    return np.random.rand()

# --------------------------
# Streamlit アプリのメイン関数
# --------------------------
def main():
    st.title("🚀 AGVシミュレーション")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏭 工場のマップ")
        factory_plot = st.empty()

    with col2:
        st.subheader("📊 センサー値")
        sensor_chart = st.line_chart(pd.DataFrame({"センサー値": []}))

    # 初期グラフをセット
    factory_fig = create_factory_layout()

    # AGVの現在位置を更新する変数
    agv_index = 0
    sensor_data = []

    # シミュレーションループ
    for _ in range(len(agv_path)):
        agv_x, agv_y = agv_path[agv_index]

        # **設備の色を更新（近づいたら緑に変わる）**
        for eq in equipment:
            eq_x, eq_y = eq["position"]
            distance = np.sqrt((agv_x - eq_x) ** 2 + (agv_y - eq_y) ** 2)
            eq["color"] = "green" if distance < 1.5 else "red"

        # **工場レイアウトを更新**
        factory_fig.data = []  # 既存データをクリア

        # 更新された設備の色を反映
        for eq in equipment:
            factory_fig.add_trace(go.Scatter(
                x=[eq["position"][0]], y=[eq["position"][1]],
                mode="markers+text",
                marker=dict(size=20, color=eq["color"]),
                text=[eq["name"]],
                textposition="top center",
                name=eq["name"]
            ))

        # AGVの位置を更新
        factory_fig.add_trace(go.Scatter(
            x=[agv_x], y=[agv_y], mode="markers",
            marker=dict(size=15, color="blue"), name="AGV"
        ))

        # **ユニークなキーを付けてエラー回避**
        factory_plot.plotly_chart(factory_fig, use_container_width=True, key=f"factory_plot_{agv_index}")

        # **センサー値を更新**
        sensor_value = generate_sensor_data()
        sensor_data.append(sensor_value)
        sensor_chart.line_chart(pd.DataFrame({"センサー値": sensor_data}))

        # AGVを次の位置に移動
        agv_index += 1
        time.sleep(0.5)

    st.success("✅ シミュレーション完了！")

# --------------------------
# Streamlit アプリの実行
# --------------------------
if __name__ == "__main__":
    main()
