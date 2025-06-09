import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib
from datetime import datetime

matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def generate_heatmap(csv_path: str, output_dir="top10_outputs", date_str=None):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)

    df["label"] = df["ts_code"]

    # ========== 多因子字段构造 ==========

    # 技术面
    df["3日预测涨幅 (%)"] = df["return_3"] * 100 if "return_3" in df.columns else 0.0
    df["近5日波动率 (%)"] = df["return_std_5"] * 100 if "return_std_5" in df.columns else 0.0

    # 模型面 ✅ 核心修复：强制数值转换
    if "模型信心分" in df.columns:
        df["模型信心分 (0~100)"] = pd.to_numeric(df["模型信心分"], errors="coerce").fillna(0.0) * 100
    elif "预测概率" in df.columns:
        df["模型信心分 (0~100)"] = df["预测概率"] * 100
    else:
        df["模型信心分 (0~100)"] = 0.0

    if "综合评分" in df.columns:
        df["综合评分 (0~100)"] = pd.to_numeric(df["综合评分"], errors="coerce").fillna(0.0)
    elif "预测概率" in df.columns:
        df["综合评分 (0~100)"] = df["预测概率"] * 100
    else:
        df["综合评分 (0~100)"] = 0.0

    # 资金面
    df["今日换手率 (%)"] = df["amount_ratio"] if "amount_ratio" in df.columns else 0.0
    if "amount_ratio" in df.columns:
        amt = df["amount_ratio"]
        df["成交额强度 (0~100)"] = 100 * (amt - amt.min()) / (amt.max() - amt.min() + 1e-6)
    else:
        df["成交额强度 (0~100)"] = 0.0

    # ========== 显示字段顺序 ==========
    fields_to_show = [
        "3日预测涨幅 (%)",
        "近5日波动率 (%)",
        "模型信心分 (0~100)",
        "综合评分 (0~100)",
        "今日换手率 (%)",
        "成交额强度 (0~100)"
    ]

    # 构建热力图 DataFrame
    heatmap_df = df[["label"] + fields_to_show].set_index("label").T
    heatmap_df = heatmap_df.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    # 按综合评分排序
    if "综合评分 (0~100)" in heatmap_df.index:
        sorted_cols = heatmap_df.loc["综合评分 (0~100)"].sort_values(ascending=False).index
        heatmap_df = heatmap_df[sorted_cols]

    # 绘图
    plt.figure(figsize=(1.2 * len(heatmap_df.columns), 6))
    sns.heatmap(
        heatmap_df,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        linewidths=0.5,
        linecolor="gray",
        cbar=True,
        mask=heatmap_df.isna()
    )
    plt.title("AI选股Top10热力图（技术 + 模型 + 资金多因子评分）", fontsize=16, pad=20)
    plt.xticks(rotation=45)
    plt.yticks(rotation=0)
    plt.tight_layout()

    # 保存图像
    date_str = date_str or datetime.now().strftime("%Y%m%d")
    out_path = os.path.join(output_dir, f"top10_heatmap_{date_str}.png")
    plt.savefig(out_path, dpi=300)
    plt.close()

    print(f"✅ 热力图已保存：{out_path}")
