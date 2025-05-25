"""
train_ai_model.py

使用 LightGBM 训练一个二分类模型，目标是预测未来3日涨幅是否 ≥10%（label=1）。
"""

import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os

# 读取数据
data_path = "datasets/training_data.csv"
df = pd.read_csv(data_path)

# 特征列（去除非数值列）
drop_cols = ['ts_code', 'trade_date', 'label']
features = [col for col in df.columns if col not in drop_cols]
X = df[features]
y = df['label']

# 划分训练集与测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# LightGBM 参数
params = {
    "objective": "binary",
    "metric": "binary_logloss",
    "verbosity": -1,
    "boosting_type": "gbdt",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "feature_fraction": 0.9,
    "bagging_fraction": 0.8,
    "bagging_freq": 5,
    "seed": 42
}

# 构建数据集
train_data = lgb.Dataset(X_train, label=y_train)
valid_data = lgb.Dataset(X_test, label=y_test)

# 训练模型
print("🚀 正在训练 LightGBM 模型...")
model = lgb.train(
    params,
    train_data,
    valid_sets=[train_data, valid_data],
    num_boost_round=200,
    callbacks=[
        lgb.early_stopping(stopping_rounds=20),
        lgb.log_evaluation(period=10)
    ]
)

# 模型评估
y_pred_prob = model.predict(X_test)
y_pred_label = (y_pred_prob >= 0.5).astype(int)
print("✅ 分类报告：")
print(classification_report(y_test, y_pred_label))
print("🎯 AUC 分数：", roc_auc_score(y_test, y_pred_prob))

# 保存模型
os.makedirs("models", exist_ok=True)
model_path = "models/lightgbm_classifier.txt"
joblib.dump(model, model_path)
print(f"✅ 模型已保存至：{model_path}")
