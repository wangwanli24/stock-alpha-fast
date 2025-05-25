@echo off
echo ✅ 正在激活虚拟环境并运行预测模块...

call .venv\Scripts\activate

python funB_multi_factor_ai\batch_predict.py

pause
