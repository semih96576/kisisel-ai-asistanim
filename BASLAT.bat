@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
echo.
echo  ======================================================
echo     Semihcim AI - Uygulama Yoneticisi (2'si 1 Arada)
echo  ======================================================
echo.
echo Lutfen baslatmak istediginiz islemi secin:
echo.
echo [1] Web Arayuzunu (Chatbot) Baslat
echo [2] Yapay Zeka Model Egitimi (semihcim_ai)
echo.
set /p secim="Seciminiz (1 veya 2): "

if "%secim%"=="1" (
    echo Web Arayuzu baslatiliyor... Lutfen bekleyin.
    start http://127.0.0.1:5000
    python app.py
    pause
    exit
)

if "%secim%"=="2" (
    echo.
    echo  --------------------------------------------------
    echo     semihcim_ai Egitim Sistemi Alt Menusu
    echo  --------------------------------------------------
    echo [1] Sadece veri topla (Wikipedia + arXiv + GitHub vb.)
    echo [2] Veriyi isle (ham - egitim formati)
    echo [3] Modeli egit
    echo [4] HEPSINI YAPTIR (tam pipeline)
    echo [5] Hizli test egitimi (5000 ornek)
    echo [6] Model ile sohbet
    echo [7] Durum raporu
    echo.
    set /p sub="Egitim Seciminiz (1-7): "
    
    cd semihcim_ai
    if "!sub!"=="1" python main.py --collect
    if "!sub!"=="2" python main.py --process
    if "!sub!"=="3" python main.py --train
    if "!sub!"=="4" python main.py --all
    if "!sub!"=="5" python main.py --train --quick
    if "!sub!"=="6" python main.py --chat
    if "!sub!"=="7" python main.py --status
    pause
    exit
)

echo Gecersiz secim yaptiniz.
pause
