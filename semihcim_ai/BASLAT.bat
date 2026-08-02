@echo off
chcp 65001 > nul
echo.
echo  ╔══════════════════════════════════════╗
echo  ║    semihcim4.0 AI Egitim Sistemi     ║
echo  ╚══════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [1] Sadece veri topla (Wikipedia + arXiv + GitHub + Finans/Kripto)
echo [2] Veriyi isle (ham → eğitim formatı)
echo [3] Modeli egit
echo [4] HEPSINI YAPTIR (tam pipeline)
echo [5] Hızlı test egitimi (5000 örnek)
echo [6] Model ile sohbet
echo [7] Durum raporu
echo.

set /p choice="Seçiminiz (1-7): "

if "%choice%"=="1" (
    set GITHUB_TOKEN=%GITHUB_TOKEN%
    python main.py --collect
)
if "%choice%"=="2" python main.py --process
if "%choice%"=="3" python main.py --train
if "%choice%"=="4" python main.py --all
if "%choice%"=="5" python main.py --train --quick
if "%choice%"=="6" python main.py --chat
if "%choice%"=="7" python main.py --status

pause
