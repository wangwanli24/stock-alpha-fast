import pandas as pd

df = pd.read_csv("datasets/recommended_top10_20250527.csv")
print(df[["ts_code", "模型信心分", "预测概率", "综合评分"]])
