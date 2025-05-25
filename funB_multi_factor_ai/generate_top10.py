"""
generate_top10.py

自动读取 datasets/predict_result_*.csv 中最新文件，生成 Top10 推荐榜单。
"""

import pandas as pd
import glob
import os

def find_latest_prediction_file(folder="datasets"):
    files = glob.glob(os.path.join(folder, "predict_result_*.csv"))
    if not files:
        raise FileNotFoundError("❌ 未找到任何预测结果文件，请先运行 batch_predict.py")
    return max(files, key=os.path.getmtime)

def generate_top10(input_path: str, output_path: str):
    df = pd.read_csv(input_path)
    df_top10 = df.sort_values(by="预测概率", ascending=False).head(10)
    df_top10.to_csv(output_path, index=False)
    print(f"✅ Top10 推荐榜已保存至：{output_path}")
    print(df_top10[["ts_code", "trade_date", "预测概率", "建议"]])

if __name__ == "__main__":
    latest_file = find_latest_prediction_file()
    output_file = latest_file.replace("predict_result_", "recommended_top10_")
    generate_top10(latest_file, output_file)
