"""
generate_training_csv.py

用于构建多因子训练数据集，标签为未来3日内是否涨幅超过10%。
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
    """获取当前A股上市公司列表"""
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    return df['ts_code'].tolist()

def get_stock_kline(ts_code, start_date, end_date):
    """获取个股日K数据"""
    try:
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        df = df.sort_values('trade_date').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"⚠️ 请求 {ts_code} 日K数据失败：{e}")
        return None

def add_label(df, future_days=3, threshold=0.10):
    """
    为每一行加上标签：未来future_days内最大涨幅是否超过 threshold
    1 = 涨幅超标；0 = 未超标
    """
    future_high = df['close'].shift(-future_days).rolling(future_days).max()
    df['future_max_return'] = (future_high - df['close']) / df['close']
    df['label'] = (df['future_max_return'] >= threshold).astype(int)
    return df

def generate_training_data(start_date="20240101", end_date="20240520", limit=100):
    """
    批量构建训练集
    """
    all_data = []
    stock_list = get_basic_stock_list()[:limit]

    for ts_code in stock_list:
        raw_df = get_stock_kline(ts_code, start_date, end_date)

        if raw_df is None:
            print(f"跳过 {ts_code}，原因：拉取数据失败")
            continue
        if raw_df.empty:
            print(f"跳过 {ts_code}，原因：数据为空")
            continue
        if 'close' not in raw_df.columns:
            print(f"跳过 {ts_code}，原因：缺少 close 字段，字段为：{raw_df.columns.tolist()}")
            continue
        if len(raw_df) < 40:
            print(f"跳过 {ts_code}，原因：数据不足40行（仅 {len(raw_df)} 行）")
            continue

        try:
            factor_df = calculate_factors(raw_df)
            labeled_df = add_label(factor_df)
            all_data.append(labeled_df)
        except Exception as e:
            print(f"跳过 {ts_code}，处理因子或标签时报错：{e}")
            continue

    if not all_data:
        print("❌ 无有效样本生成，可能是接口请求限制或数据缺失。")
        return

    df_all = pd.concat(all_data, ignore_index=True)
    df_all.to_csv("datasets/training_data.csv", index=False, encoding='utf-8-sig')
    print("✅ 训练数据已保存至 datasets/training_data.csv，共计样本数：", len(df_all))

if __name__ == "__main__":
    generate_training_data(start_date="20240101", end_date="20240520", limit=100)
