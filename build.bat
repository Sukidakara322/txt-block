@echo off
rem Ten skrypt buduje samodzielny plik .exe programu do szyfrowania plikow.
rem Uruchamiasz go TYLKO RAZ, na komputerze z zainstalowanym Pythonem.
rem Po zbudowaniu, gotowy plik .exe dziala juz bez Pythona - mozna go
rem przenosic i uruchamiac na dowolnym komputerze z Windows.

echo Sprawdzanie i instalowanie wymaganych bibliotek...
python -m pip install --no-warn-script-location cryptography pyinstaller

if errorlevel 1 (
    echo.
    echo BLAD: Nie udalo sie zainstalowac bibliotek.
    echo Sprawdz, czy Python i pip sa poprawnie zainstalowane.
    pause
    exit /b 1
)

echo.
echo Budowanie pliku .exe - to moze potrwac chwile...
rem Uzywamy "python -m PyInstaller" zamiast samej komendy "pyinstaller",
rem bo przy niektorych instalacjach Pythona (np. ze sklepu Microsoft Store)
rem folder ze skryptami nie jest dodany do PATH i sama komenda nie dziala.
python -m PyInstaller --onefile --console --name HasloDoPlikow haslo_app.py

if errorlevel 1 (
    echo.
    echo BLAD: Budowanie nie powiodlo sie.
    pause
    exit /b 1
)

echo.
echo =============================================
echo  Gotowe! Plik HasloDoPlikow.exe znajdziesz
echo  w folderze "dist", ktory pojawil sie obok.
echo =============================================
echo.
pause
