"""
generate_top10.py

自动读取 datasets/predict_result_*.csv 中最新文件，生成 Top10 推荐榜单并绘制热力图。
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
    # ✅ 加入 ST、退市、停牌过滤逻辑（此处插入）
    import tushare as ts
    ts.set_token("d6be033dbd2142b995c5d4b10b32f031a9f42ff8699f9f236f937b4f")
    pro = ts.pro_api()
    basic_info = pro.stock_basic(exchange='', list_status='L', fields='ts_code,name,list_status')
    valid_stocks = basic_info[~basic_info['name'].str.contains('ST')]
    valid_ts_codes = set(valid_stocks['ts_code'])
    df = df[df['ts_code'].isin(valid_ts_codes)]
    if 'volume' in df.columns:
        df = df[df['volume'] > 0]
    if 'latestPrice' in df.columns:
        df = df[~df['latestPrice'].isin(['--'])]
        df = df[df['latestPrice'].notna()]
    # ✅ 过滤掉科创板（688***.SH）和北证（*.BJ）股票，仅保留主板和创业板
    df = df[df["ts_code"].str.match(r"^(000|001|002|300|600)\d{3}\.(SZ|SH)$")]

    # ====== 字段构建（避免缺失） ======
    df["预测概率"] = df["预测概率"] if "预测概率" in df.columns else 0.0
    df["return_3"] = df["return_3"] if "return_3" in df.columns else 0.0
    df["return_std_5"] = df["return_std_5"] if "return_std_5" in df.columns else 0.0
    df["amount_ratio"] = df["amount_ratio"] if "amount_ratio" in df.columns else 0.0

    # ====== 新字段构造 ======
    df["模型信心分"] = (df["预测概率"] * 100).round(2)
    df["波动率"] = (df["return_std_5"] * 100).round(2)

    # 计算综合评分（加权方案可调）
    df["综合评分"] = (
        df["模型信心分"] * 0.5 +
        df["amount_ratio"] * 0.3 +
        df["波动率"] * 0.2
    ).round(2)

    # 选出 Top10
    df_top10 = df.sort_values(by="综合评分", ascending=False).head(10)

    # 明确导出字段（供热力图使用）
    columns_to_save = [
        "ts_code", "trade_date", "预测概率", "建议",
        "return_3", "return_std_5", "amount_ratio",
        "模型信心分", "波动率", "综合评分"
    ]
    df_top10.to_csv(output_path, index=False, columns=[col for col in columns_to_save if col in df_top10.columns])

    print(f"✅ Top10 推荐榜已保存至：{output_path}")
    print(df_top10[["ts_code", "trade_date", "模型信心分", "综合评分", "建议"]])

    # 🔥 自动绘制热力图
    try:
        from plot_top10 import generate_heatmap
        os.makedirs("top10_outputs", exist_ok=True)
        csv_out = os.path.join("top10_outputs", os.path.basename(output_path))
        df_top10.to_csv(csv_out, index=False)
        # generate_heatmap(csv_out)
        generate_heatmap(output_path, date_str=predict_date_str)

    except Exception as e:
        print(f"⚠️ 热力图绘制失败：{e}")


if __name__ == "__main__":
    latest_file = find_latest_prediction_file()
    predict_date_str = latest_file.split("_")[-1].split(".")[0]  # 提取日期：20250527
    output_file = f"datasets/recommended_top10_{predict_date_str}.csv"
    generate_top10(latest_file, output_file)
