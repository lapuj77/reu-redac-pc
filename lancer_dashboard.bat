@echo off
title Dashboard Redaction
cd /d "E:\dev\reu-redac-01"

echo.
echo  ===================================
echo   Dashboard Reunion Redaction
echo  ===================================
echo.
echo  Demarrage en cours...
echo  Le navigateur va s'ouvrir dans quelques secondes.
echo.
echo  Pour arreter : appuyer sur Ctrl+C puis fermer cette fenetre.
echo.

python -m streamlit run dashboard.py

echo.
echo  Le serveur s'est arrete.
pause
