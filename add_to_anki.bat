@echo off
REM Exécute le premier script Python
python markdown_to_csv.py

REM Vérifie si le premier script s'est terminé avec succès
IF %ERRORLEVEL% NEQ 0 (
    echo Le premier script a échoué. Arrêt du processus.
    pause
    exit /b %ERRORLEVEL%
)

REM Exécute le deuxième script Python
python csv_to_anki.py@echo off
REM Run the first Python script
python markdown_to_csv.py

REM Check if the first script finished successfully
IF %ERRORLEVEL% NEQ 0 (
    echo The first script failed. Stopping the process.
    pause
    exit /b %ERRORLEVEL%
)

REM Run the second Python script
python csv_to_anki.py

REM Check if the second script finished successfully
IF %ERRORLEVEL% NEQ 0 (
    echo The second script failed. Stopping the process.
    pause
    exit /b %ERRORLEVEL%
)

echo Both scripts executed successfully.
pause


REM Vérifie si le deuxième script s'est terminé avec succès
IF %ERRORLEVEL% NEQ 0 (
    echo Le deuxième script a échoué. Arrêt du processus.
    pause
    exit /b %ERRORLEVEL%
)

echo Les deux scripts ont été exécutés avec succès.
pause
