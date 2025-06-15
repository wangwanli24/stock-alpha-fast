import streamlit as st
import pandas as pd
import glob
import os
import subprocess

st.set_page_config(page_title="Top10 打分系统", layout="wide")
st.title("🧠 Top10 人工打分 + 持仓确认系统")

# === 1. 获取最新 Top10 文件 ===
def get_latest_top10():
    files = glob.glob("datasets/recommended_top10_*.csv")
    if not files:
        st.error("未找到 Top10 文件，请先运行 generate_top10.py")
        st.stop()
    return max(files, key=os.path.getmtime)

latest_file = get_latest_top10()
df = pd.read_csv(latest_file)

st.success(f"已加载最新 Top10 文件：{os.path.basename(latest_file)}")

# === 2. 显示股票表格 + 打分框 + ✔确认复选框 ===
st.write("请为下列股票打分（0~20 分）并勾选你最终想持仓的股票")
scores = {}
confirmed = []

for idx, row in df.iterrows():
    col1, col2, col3, col4 = st.columns([2, 5, 3, 2])
    with col1:
        st.write(f"**{row['ts_code']}**")
    with col2:
        st.write(f"建议：{row.get('建议', '')} ｜ 模型分：{row.get('模型信心分', '')}")
    with col3:
        score = st.slider(f"打分 ({row['ts_code']})", 0, 20, 0, key=row['ts_code'])
        scores[row['ts_code']] = score
    with col4:
        confirm = st.checkbox("✔确认", key="confirm_" + row['ts_code'])
        if confirm:
            confirmed.append(row['ts_code'])

# === 3. 提交按钮 ===
if st.button("✅ 提交并保存 manual_score.csv + confirmed_top.csv"):
    df_score = pd.DataFrame(list(scores.items()), columns=["ts_code", "manual_score"])
    df_score.to_csv("manual_score.csv", index=False)
    st.success("manual_score.csv 已保存 ✅")

    if confirmed:
        df_confirmed = df[df['ts_code'].isin(confirmed)]
        df_confirmed.to_csv("confirmed_top.csv", index=False)
        st.success("confirmed_top.csv（最终确认持仓）已保存 ✅")
    else:
        st.warning("未勾选任何确认股票，未生成 confirmed_top.csv")

    if st.checkbox("🚀 同时重新生成 Top10 + 热力图"):
        cmd = f"python generate_top10.py"
        with st.spinner("正在重新生成推荐榜与热力图..."):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            st.text(result.stdout)
            if result.stderr:
                st.error(result.stderr)
        st.success("🎉 已完成重新生成！")
