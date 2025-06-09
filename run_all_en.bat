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

REM Step 2: Build full-market prediction input
echo [%TIME%] Building full-market input file...
python build_predict_input.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate input file. Please check calculate_factors.py
    pause
    exit /b
)

REM Step 3: Run batch prediction
echo [%TIME%] Running batch prediction...
python funB_multi_factor_ai\batch_predict.py
if %errorlevel% neq 0 (
    echo [ERROR] Prediction failed. Please check model or input format.
    pause
    exit /b
)

REM Step 4: Generate Top10 recommendation and heatmap
echo [%TIME%] Generating Top10 recommendation...
python generate_top10.py
if %errorlevel% neq 0 (
    echo [ERROR] Top10 generation failed. Please check generate_top10.py
    pause
    exit /b
)

echo [%TIME%]  Pipeline finished successfully. Output saved to /datasets and /top10_outputs
pause
