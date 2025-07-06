"""
generate_factors.py

生成用于模型训练和预测的技术、资金、情绪等因子特征。
"""

import pandas as pd
import numpy as np

print("✅ 正在使用我刚替换的 generate_factors.py")

def calculate_factors(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = [
        c.encode('ascii', 'ignore').decode('utf-8').strip().replace(" ", "").replace("　", "") 
        for c in df.columns
    ]

    print("🧪 字段名 repr 列表如下：")
    for col in df.columns:
        print(f"🔍 列名：{repr(col)}")

    print(f"🧪 close 预览:\n{df[['trade_date', 'close']].tail()}")

    df.sort_values('trade_date', inplace=True)

    required_columns = ['ts_code', 'trade_date', 'open', 'high', 'low', 'close', 'vol', 'amount']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"字段缺失: {col}")
    if df['close'].isna().all():
        raise ValueError("字段 'close' 全部为空值")

    df['return_1'] = df['close'].pct_change(1)
    df['return_3'] = df['close'].pct_change(3)
    df['ma_5'] = df['close'].rolling(5).mean()
    df['ma_10'] = df['close'].rolling(10).mean()
    df['ma_20'] = df['close'].rolling(20).mean()
    df['ma_ratio_5_10'] = df['ma_5'] / df['ma_10']
    df['ma_ratio_5_20'] = df['ma_5'] / df['ma_20']
    df['vol_ratio_5'] = df['vol'] / df['vol'].rolling(5).mean()

    df['high_low_range'] = (df['high'] - df['low']) / df['close']
    df['return_std_5'] = df['close'].pct_change().rolling(5).std()

    df['momentum_3'] = df['close'] - df['close'].shift(3)
    df['amount_ratio'] = df['amount'] / df['amount'].rolling(5).mean()
    df['green_days'] = (df['close'] > df['open']).rolling(5).sum() / 5
    df['amount'] = df['amount']

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    print("🧨 dropna 后 df.shape =", df.shape)
    if df.empty:
        raise ValueError("因子计算后 dropna 清空所有数据")

    factor_cols = [
        'ts_code', 'trade_date', 'close',  # ✅ 加回 close 字段，供 add_label 使用
        'return_1', 'return_3',
        'ma_ratio_5_10', 'ma_ratio_5_20',
        'vol_ratio_5', 'high_low_range',
        'return_std_5', 'momentum_3',
        'amount_ratio', 'green_days', 'amount',
    ]

    return df[factor_cols].reset_index(drop=True)
