"""
generate_training_csv.py

构建动态训练数据集（近半年），标签为未来3日内是否涨幅超过10%
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
from funB_multi_factor_ai.generate_factors import calculate_factors

# 初始化 Tushare
ts.set_token("d6be033dbd2142b995c5d4b10b32f031a9f42ff8699f9f236f937b4f")
pro = ts.pro_api()

def get_basic_stock_list():
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code')
    stock_list = df['ts_code'].tolist()
    stock_list = [code for code in stock_list if not code.startswith("688") and not code.startswith("BJ")]
    return stock_list

def get_stock_kline(ts_code, start_date, end_date):
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date').reset_index(drop=True)
        return df
    except Exception as e:
        print("⚠️ 请求 {} 日K数据失败：{}".format(ts_code, e))
        return None

def add_label(df, future_days=3, threshold=0.10):
    future_high = df['close'].shift(-future_days).rolling(future_days).max()
    df['future_max_return'] = (future_high - df['close']) / df['close']
    df['label'] = (df['future_max_return'] >= threshold).astype(int)
    return df

def generate_training_data(start_date, end_date, limit=None):
    all_data = []
    stock_list = get_basic_stock_list()
    if limit:
        stock_list = stock_list[:limit]

    print("✅ 开始生成训练集，共处理股票：{}，区间：{} ~ {}".format(len(stock_list), start_date, end_date))

    for ts_code in stock_list:
        raw_df = get_stock_kline(ts_code, start_date, end_date)
        if raw_df is None or raw_df.empty or 'close' not in raw_df.columns or len(raw_df) < 40:
            continue
        try:
            factor_df = calculate_factors(raw_df)
            labeled_df = add_label(factor_df)
            all_data.append(labeled_df)
        except Exception as e:
            print("⚠️ {} 处理失败：{}".format(ts_code, e))
            continue

    if not all_data:
        print("❌ 没有成功生成任何训练样本")
        return

    df_all = pd.concat(all_data, ignore_index=True)
    os.makedirs("datasets", exist_ok=True)
    df_all.to_csv("datasets/training_data.csv", index=False, encoding='utf-8-sig')
    print("✅ 训练数据已保存：datasets/training_data.csv，样本数：", len(df_all))

if __name__ == "__main__":
    today = datetime.today()
    end_date = today.strftime("%Y%m%d")
    start_date = (today - timedelta(days=180)).strftime("%Y%m%d")
    generate_training_data(start_date=start_date, end_date=end_date, limit=None)
