"""
batch_predict.py

批量加载因子 CSV 文件并输出 LightGBM 模型预测建议（基于 LGBMClassifier）。
"""

import pandas as pd
import joblib
import os
from datetime import datetime

def load_model(model_path="models/lightgbm_classifier.pkl"):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"❌ 模型文件不存在：{model_path}")
    model = joblib.load(model_path)
    return model

def load_feature_names():
    data_path = "datasets/training_data.csv"
    df = pd.read_csv(data_path)
    drop_cols = ['ts_code', 'trade_date', 'label']
    features = [col for col in df.columns if col not in drop_cols]
    return features

# ✅ 信心分映射函数（0-100 分级评分）
def map_confidence(prob):
    if prob >= 0.9:
        return 100
    elif prob >= 0.8:
        return 90
    elif prob >= 0.7:
        return 80
    elif prob >= 0.6:
        return 70
    elif prob >= 0.5:
        return 60
    elif prob >= 0.4:
        return 40
    elif prob >= 0.3:
        return 20
    else:
        return 0

# ✅ 建议标签函数（多级建议）
def map_suggestion(prob):
    if prob >= 0.85:
        return "🔥 强烈建议买入"
    elif prob >= 0.7:
        return "✅ 建议买入"
    elif prob >= 0.5:
        return "☑️ 可考虑关注"
    else:
        return "❌ 不建议买入"

def predict_batch(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    model = load_model()
    features = load_feature_names()

    # 填补缺失字段
    for col in features:
        if col not in df.columns:
            df[col] = 0.0
    df_features = df[features]

    # 使用 predict_proba 输出 P(1)
    probs = model.predict_proba(df_features)[:, 1]
    df["预测概率"] = probs.round(6)
    df["模型信心分"] = df["预测概率"].apply(map_confidence)
    df["建议"] = df["预测概率"].apply(map_suggestion)

    # 保留原始预测标签（可选）
    df["预测标签"] = (df["预测概率"] >= 0.5).astype(int)

    df.to_csv(output_csv, index=False)
    print(f"✅ 批量预测完成，结果已保存至：{output_csv}")

if __name__ == "__main__":
    input_path = "datasets/sample_predict_input.csv"
    today = datetime.now().strftime("%Y%m%d")
    output_path = f"datasets/predict_result_{today}.csv"
    predict_batch(input_path, output_path)
