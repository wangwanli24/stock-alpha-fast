import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import tushare as ts

# ✅ 中文字体支持
plt.rcParams['font.family'] = 'Microsoft YaHei'
plt.rcParams['axes.unicode_minus'] = False

# ===== 参数设定 =====
TOTAL_CAPITAL = 80000
TOP3_PATH_FOLDER = "datasets"
OUTPUT_CSV_FOLDER = "datasets"
OUTPUT_IMG_FOLDER = "top3_outputs"
WEIGHT_SCORE = 0.85
WEIGHT_AMOUNT = 0.15

# 初始化 Tushare
ts.set_token("d6be033dbd2142b995c5d4b10b32f031a9f42ff8699f9f236f937b4f")
pro = ts.pro_api()

def find_latest_top3_file(folder="datasets"):
    files = [f for f in os.listdir(folder) if f.startswith("recommended_top3_")]
    if not files:
        raise FileNotFoundError("❌ 未找到Top3推荐结果，请先运行 generate_top3.py")
    latest_file = max(files)
    return os.path.join(folder, latest_file)

def get_latest_close_price(ts_code):
    today = datetime.today().strftime("%Y%m%d")
    recent = (datetime.today() - timedelta(days=7)).strftime("%Y%m%d")
    df = pro.daily(ts_code=ts_code, start_date=recent, end_date=today)
    if df.empty:
        return 10.0  # fallback
    return float(df.iloc[0]["close"])

def predict_smart_buy_price(close_price, score):
    return round(close_price * (1 - (0.01 + 0.05 * (1 - score / 100))), 2)

def plot_buy_advice(df_open, df_smart, save_path):
    plt.figure(figsize=(11, 6))
    names = [
        f"{(row.get('label') or row.get('name') or row['ts_code'])}（{row['ts_code']}）"
        for _, row in df_open.iterrows()
    ]
    x = range(len(names))
    bar_width = 0.35

    open_heights = df_open['预计买入金额']
    smart_heights = df_smart['预计买入金额']

    plt.bar([i - bar_width / 2 for i in x], open_heights, width=bar_width, label="开盘买入", color='skyblue')
    plt.bar([i + bar_width / 2 for i in x], smart_heights, width=bar_width, label="智慧预测", color='orange')

    for i, (a, b) in enumerate(zip(open_heights, smart_heights)):
        open_text = f"{int(df_open['股数'][i])}股\n￥{df_open['建议买入价'][i]:.2f}\n￥{a:.0f}"
        smart_text = f"{int(df_smart['股数'][i])}股\n￥{df_smart['建议买入价'][i]:.2f}\n￥{b:.0f}"
        plt.text(i - bar_width / 2, a * 0.4, open_text, ha='center', va='center', fontsize=9, color='black')
        plt.text(i + bar_width / 2, b * 0.4, smart_text, ha='center', va='center', fontsize=9, color='black')

    plt.xticks(x, names, rotation=15)
    plt.title("明日买入建议对比（开盘价 vs 智慧预测）")
    plt.ylabel("预计买入金额（元）")
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def record_buy():
    os.makedirs(OUTPUT_IMG_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_CSV_FOLDER, exist_ok=True)

    today_str = datetime.today().strftime("%Y%m%d")
    top3_path = find_latest_top3_file(TOP3_PATH_FOLDER)
    df = pd.read_csv(top3_path)

    score_col = [col for col in df.columns if "综合评分" in col][0]
    amount_col = [col for col in df.columns if "成交额强度" in col]
    amount_col = amount_col[0] if amount_col else None

    df["score_weight"] = df[score_col] * WEIGHT_SCORE
    df["amount_weight"] = df[amount_col] * WEIGHT_AMOUNT if amount_col else 0
    df["total_weight"] = df["score_weight"] + df["amount_weight"]
    df["weight_ratio"] = df["total_weight"] / df["total_weight"].sum()

    open_records, smart_records = [], []

    for _, row in df.iterrows():
        ts_code = row["ts_code"]
        name = row.get("label") or row.get("name") or ts_code
        score = row[score_col]
        weight = row["weight_ratio"]

        allocated_cash = TOTAL_CAPITAL * weight

        # ✅ 拉取真实收盘价
        close_price = get_latest_close_price(ts_code)

        # 方案A：开盘价买入
        open_price = round(close_price, 2)
        open_shares = int(allocated_cash // (open_price * 100)) * 100
        open_amount = open_price * open_shares
        open_records.append({
            "ts_code": ts_code, "name": name, "建议买入价": open_price,
            "股数": open_shares, "预计买入金额": round(open_amount, 2),
            "占比": round(weight * 100, 2), "买入策略": "开盘买入"
        })

        # 方案B：智慧预测买入
        smart_price = predict_smart_buy_price(close_price, score)
        smart_shares = int(allocated_cash // (smart_price * 100)) * 100
        smart_amount = smart_price * smart_shares
        smart_records.append({
            "ts_code": ts_code, "name": name, "建议买入价": smart_price,
            "股数": smart_shares, "预计买入金额": round(smart_amount, 2),
            "占比": round(weight * 100, 2), "买入策略": "智慧预测"
        })

    df_open = pd.DataFrame(open_records)
    df_smart = pd.DataFrame(smart_records)

    open_path = os.path.join(OUTPUT_CSV_FOLDER, f"buy_record_open_{today_str}.csv")
    smart_path = os.path.join(OUTPUT_CSV_FOLDER, f"buy_record_smart_{today_str}.csv")
    df_open.to_csv(open_path, index=False, encoding="utf-8-sig")
    df_smart.to_csv(smart_path, index=False, encoding="utf-8-sig")

    print(f"✅ 开盘买入建议已保存：{open_path}")
    print(f"✅ 智慧预测买入建议已保存：{smart_path}")

    # 输出图像
    image_path = os.path.join(OUTPUT_IMG_FOLDER, f"buy_advice_{today_str}.png")
    plot_buy_advice(df_open, df_smart, image_path)
    print(f"📈 明日买入建议图已保存：{image_path}")

if __name__ == "__main__":
    record_buy()
