"""
batch_predict.py

批量加载因子 CSV 文件并输出 LightGBM 模型预测建议。
"""

import pandas as pd
import joblib
import lightgbm as lgb
import os
from datetime import datetime

def load_model(model_path="models/lightgbm_classifier.txt"):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在：{model_path}")
    model = joblib.load(model_path)
    return model

def load_feature_names():
    data_path = "datasets/training_data.csv"
    df = pd.read_csv(data_path)
    drop_cols = ['ts_code', 'trade_date', 'label']
    features = [col for col in df.columns if col not in drop_cols]
    return features

def predict_batch(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    model = load_model()
    features = load_feature_names()

    # 填补缺失字段
    for col in features:
        if col not in df.columns:
            df[col] = 0.0
    df_features = df[features]

    # 预测
    probs = model.predict(df_features)
    labels = (probs >= 0.5).astype(int)
    suggestions = ["✅ 建议买入" if l == 1 else "❌ 不建议买入" for l in labels]

    df["预测概率"] = probs
    df["预测标签"] = labels
    df["建议"] = suggestions

    df.to_csv(output_csv, index=False)
    print(f"✅ 批量预测完成，结果已保存至：{output_csv}")

if __name__ == "__main__":
    input_path = "datasets/sample_predict_input.csv"
    today = datetime.now().strftime("%Y%m%d")
    output_path = f"datasets/predict_result_{today}.csv"
    predict_batch(input_path, output_path)
