
from funB_multi_factor_ai.generate_factors import calculate_factors
import tushare as ts
import pandas as pd
import os
from datetime import datetime

ts.set_token("d6be033dbd2142b995c5d4b10b32f031a9f42ff8699f9f236f937b4f")
pro = ts.pro_api()

def build_prediction_input(save_path: str):
    # 获取所有 A 股股票基本信息
    stock_basic = pro.stock_basic(exchange='', list_status='L', fields='ts_code')

    # ✅ 过滤掉科创板（688***.SH）和北证（.BJ）
    stock_basic = stock_basic[stock_basic["ts_code"].str.match(r"^(000|001|002|300|600)\d{3}\.(SZ|SH)$")]

    ts_codes = stock_basic["ts_code"].tolist()


    predict_date = datetime.now().strftime("%Y%m%d")
    all_factors = []

    for i, ts_code in enumerate(ts_codes):
        try:
            # 拉取最近 20 日行情数据
            df = pro.daily(ts_code=ts_code, end_date=predict_date)
            if df.empty or len(df) < 10:
                continue
            df = df.sort_values("trade_date").reset_index(drop=True)

            # 计算因子
            factor_df = calculate_factors(df)
            if not factor_df.empty:
                all_factors.append(factor_df.iloc[-1:])  # 仅取最近一行

            if i % 100 == 0:
                print(f"Progress: {i}/{len(ts_codes)}")

        except Exception as e:
            print(f"⚠️ Skipping {ts_code}: {e}")
            continue

    if not all_factors:
        print("❌ No valid factor data generated.")
        return

    df_final = pd.concat(all_factors, ignore_index=True)
    os.makedirs("datasets", exist_ok=True)
    df_final.to_csv(save_path, index=False)
    print(f"✅ Prediction input saved: {save_path}, total: {len(df_final)} rows")


if __name__ == "__main__":
    build_prediction_input("datasets/sample_predict_input.csv")
