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
python funB_multi_factor_ai\generate_training_csv.py
if %errorlevel% neq 0 (
    echo [ERROR] Failed to generate input file. Please check generate_training_csv.py
    pause
    exit /b
)

REM Step 3: Run batch prediction
echo [%TIME%] Running batch prediction...
python funB_multi_factor_ai\train_ai_model.py
if %errorlevel% neq 0 (
    echo [ERROR] Prediction failed. Please check train_ai_modelt.
    pause
    exit /b
)

echo ✅ 模型训练完成，已保存至 models/lightgbm_classifier.pkl
pause
