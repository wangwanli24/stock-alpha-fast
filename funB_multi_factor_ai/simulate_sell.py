import pandas as pd
import os
import re
import glob
from datetime import datetime, timedelta
import tushare as ts

# ===== 初始化 Tushare =====
ts.set_token("d6be033dbd2142b995c5d4b10b32f031a9f42ff8699f9f236f937b4f")
pro = ts.pro_api()

# ===== 参数设定 =====
FOLDER = "datasets"
SELL_USE = "close"  # 可选 "close" 或 "high"

def find_latest_file(prefix):
    pattern = os.path.join(FOLDER, f"{prefix}_*.csv")
    files = glob.glob(pattern)
    if not files:
        return None, None
    latest_file = max(files, key=os.path.getmtime)
    date_match = re.search(r"(\d{8})", latest_file)
    if not date_match:
        return None, None
    date_str = date_match.group(1)
    return latest_file, date_str

def get_sell_prices(ts_codes, trade_date):
    results = []
    for code in ts_codes:
        try:
            df = pro.daily(ts_code=code, trade_date=trade_date)
            if df.empty:
                results.append((code, None, None))
            else:
                close = df.iloc[0]["close"]
                high = df.iloc[0]["high"]
                results.append((code, close, high))
        except:
            results.append((code, None, None))
    return pd.DataFrame(results, columns=["ts_code", "close", "high"])

def simulate_sell():
    # ===== 自动识别最新买入记录 =====
    open_path, open_date = find_latest_file("buy_record_open")
    smart_path, smart_date = find_latest_file("buy_record_smart")

    if not open_path and not smart_path:
        print("❌ 未找到任何买入记录文件")
        return

    use_date = open_date or smart_date
    sell_date_obj = datetime.strptime(use_date, "%Y%m%d") + timedelta(days=1)
    sell_date_str = sell_date_obj.strftime("%Y%m%d")

    records = []
    for strategy, path in [("open", open_path), ("smart", smart_path)]:
        if not path:
            continue
        df_buy = pd.read_csv(path)
        ts_codes = df_buy["ts_code"].tolist()
        price_df = get_sell_prices(ts_codes, sell_date_str)
        merged = pd.merge(df_buy, price_df, on="ts_code", how="left")

        for _, row in merged.iterrows():
            sell_price = row["close"] if SELL_USE == "close" else row["high"]
            if pd.isna(sell_price):
                record = {
                    "ts_code": row["ts_code"],
                    "name": row.get("name", ""),
                    "策略": "开盘买入" if strategy == "open" else "智慧预测",
                    "买入价": row["建议买入价"],
                    "卖出价": "数据缺失",
                    "股数": row["股数"],
                    "盈亏金额": "N/A",
                    "盈亏率": "N/A"
                }
            else:
                profit = (sell_price - row["建议买入价"]) * row["股数"]
                profit_rate = profit / (row["建议买入价"] * row["股数"])
                record = {
                    "ts_code": row["ts_code"],
                    "name": row.get("name", ""),
                    "策略": "开盘买入" if strategy == "open" else "智慧预测",
                    "买入价": round(row["建议买入价"], 2),
                    "卖出价": round(sell_price, 2),
                    "股数": int(row["股数"]),
                    "盈亏金额": round(profit, 2),
                    "盈亏率": f"{profit_rate * 100:.2f}%"
                }
            records.append(record)

    df_result = pd.DataFrame(records)
    out_path = os.path.join(FOLDER, f"sell_result_{sell_date_str}.csv")
    df_result.to_csv(out_path, index=False, encoding="utf-8-sig")

    print(f"✅ 模拟卖出结果已保存：{out_path}")
    print(df_result)

if __name__ == "__main__":
    simulate_sell()
