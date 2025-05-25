"""
validate_tushare_data.py

用于快速验证 tushare.pro.daily() 是否返回正常数据结构。
"""

import tushare as ts

# 设置 token（已替换为你的 Token）
ts.set_token("d6be033dbd2142b995c5d4b10b32f031a9f42ff8699f9f236f937b4f")
pro = ts.pro_api()

def validate_single_stock(ts_code="000001.SZ", start_date="20240401", end_date="20240524"):
    print(f"验证股票：{ts_code}，时间区间：{start_date} ~ {end_date}")
    df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)

    if df is None or df.empty:
        print("⚠️ 数据为空！")
    else:
        print("✅ 数据返回成功")
        print("前5行：")
        print(df.head())
        print("字段列表：", df.columns.tolist())

if __name__ == "__main__":
    # 你可以修改 ts_code 和日期做更多验证
    validate_single_stock("000001.SZ")
