import pandas as pd
import os
import glob
from datetime import datetime, timedelta

# ===== 可调参数 =====
FILTER_RECENT_DAYS = 2  # 最近N天内不建议重复推荐
TOP_N = 3               # 最终推荐Top N支股票
HISTORY_FOLDER = "datasets"  # 历史Top3文件保存目录

def find_latest_top10_file(folder="datasets"):
    files = glob.glob(os.path.join(folder, "recommended_top10_*.csv"))
    if not files:
        raise FileNotFoundError("❌ 未找到Top10推荐结果，请先运行 generate_top10.py")
    return max(files, key=os.path.getmtime)

def load_recent_top3_codes(n_days, folder=HISTORY_FOLDER):
    codes = set()
    today = datetime.today().date()
    for i in range(1, n_days + 1):
        check_date = (today - timedelta(days=i)).strftime("%Y%m%d")
        path = os.path.join(folder, f"recommended_top3_{check_date}.csv")
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                codes.update(df["ts_code"].tolist())
            except:
                continue
    return codes

def _get_score_column(df):
    """自动寻找包含“综合评分”字段"""
    for col in df.columns:
        if "综合评分" in col:
            return col
    raise KeyError("❌ 未找到包含 '综合评分' 的字段，请检查推荐文件格式")

def generate_top3():
    latest_path = find_latest_top10_file()
    df = pd.read_csv(latest_path)

    recent_codes = load_recent_top3_codes(FILTER_RECENT_DAYS)

    # 排除近期重复推荐
    filtered_df = df[~df["ts_code"].isin(recent_codes)].copy()

    # 若不足TOP_N，再从原始数据中补足
    score_col = _get_score_column(df)
    if len(filtered_df) < TOP_N:
        needed = TOP_N - len(filtered_df)
        remaining_df = df[df["ts_code"].isin(recent_codes)]
        supplement_df = remaining_df.sort_values(by=score_col, ascending=False).head(needed)
        filtered_df = pd.concat([filtered_df, supplement_df])

    # 最终选出Top N
    top3_df = filtered_df.sort_values(by=score_col, ascending=False).head(TOP_N).copy()

    # 添加推荐时间 & 输出路径
    today_str = datetime.today().strftime("%Y%m%d")
    top3_path = os.path.join(HISTORY_FOLDER, f"recommended_top3_{today_str}.csv")
    top3_df.to_csv(top3_path, index=False)

    print(f"✅ Top3 推荐已生成：{top3_path}")

    # 智能显示推荐结果
    display_cols = ["ts_code", score_col]
    if "label" in top3_df.columns:
        display_cols.insert(1, "label")
    print(top3_df[display_cols])

if __name__ == "__main__":
    generate_top3()
