"""
predict_by_model.py

加载 LightGBM 模型并预测新数据样本的涨幅概率与建议。
"""

import pandas as pd
import joblib
import lightgbm as lgb
import os

def load_model(model_path="models/lightgbm_classifier.txt"):
    """加载训练好的 LightGBM 模型"""
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"模型文件不存在：{model_path}")
    model = joblib.load(model_path)
    return model

def load_feature_names():
    """加载训练时的特征字段名"""
    data_path = "datasets/training_data.csv"
    df = pd.read_csv(data_path)
    drop_cols = ['ts_code', 'trade_date', 'label']
    features = [col for col in df.columns if col not in drop_cols]
    return features

def predict_sample(sample_df: pd.DataFrame, model, feature_names: list) -> dict:
    """
    对单支股票样本进行预测

    参数:
        sample_df: 包含字段的 DataFrame（可缺失字段）
        model: 已加载模型
        feature_names: 模型所需字段顺序

    返回:
        预测结果字典
    """
    for col in feature_names:
        if col not in sample_df.columns:
            sample_df[col] = 0.0  # 默认值填补缺失字段

    sample_df = sample_df[feature_names]  # 确保列顺序一致
    prob = model.predict(sample_df)[0]
    label = int(prob >= 0.5)
    return {
        "预测概率": round(prob, 4),
        "预测标签": label,
        "建议": "✅ 建议买入" if label == 1 else "❌ 不建议买入"
    }

# 示例调用
if __name__ == "__main__":
    model = load_model()
    feature_names = load_feature_names()

    sample_data = {
        "return_1": 0.01,
        "return_3": 0.03,
        "ma_ratio_5_10": 1.05,
        "ma_ratio_5_20": 1.10,
        "vol_ratio_5": 1.2,
        "high_low_range": 0.03,
        "return_std_5": 0.015,
        "momentum_3": 0.5,
        "amount_ratio": 1.5,
        "green_days": 0.6,
        "close": 11.38  # ✅ 保证 close 字段也包含
    }
    sample_df = pd.DataFrame([sample_data])

    result = predict_sample(sample_df, model, feature_names)
    print("🎯 预测结果：", result)
