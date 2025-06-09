@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo [%DATE% %TIME%] Launching AI stock pipeline...
echo ================================================

REM Step 0: Activate virtual environment
if exist ".venv\Scripts\activate" (
    call .venv\Scripts\activate
) else (
    echo [ERROR] .venv not found. Please run: python -m venv .venv
    pause
    exit /b
)

REM Step 1: Install dependencies
echo [%TIME%] Installing dependencies...
pip install -r requirements.txt

REM Step 2: Train model
echo [%TIME%] Training model...
python funB_multi_factor_ai\train_ai_model.py

REM Step 3: Run batch prediction
echo [%TIME%] Running batch prediction...
python funB_multi_factor_ai\batch_predict.py

REM Step 4: Generate Top10 and heatmap
echo [%TIME%] Generating Top10 and heatmap...
python funB_multi_factor_ai\generate_top10.py

REM Done
echo ================================================
echo [%TIME%] All tasks completed.
echo Top10 CSV: datasets\recommended_top10_*.csv
echo Heatmap:   top10_outputs\top10_heatmap_*.png
echo ================================================
pause
