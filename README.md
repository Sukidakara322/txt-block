# HasloDoPlikow

## Jak to działa

Program szyfruje i odszyfrowuje pliki tekstowe hasłem. Sam rozpoznaje, co ma zrobić z podanym plikiem, patrząc na jego rozszerzenie - nie trzeba wybierać żadnej opcji ręcznie.

- Jeśli plik **nie** ma końcówki `.locked` - program go **szyfruje**. Pyta o hasło dwa razy (żeby uniknąć literówki), a wynik zapisuje jako nowy plik z dodaną końcówką `.locked`. Oryginał zostaje nietknięty.
- Jeśli plik **ma** końcówkę `.locked` - program go **odszyfrowuje**. Pyta o hasło raz, a wynik zapisuje bez tej końcówki.

Do szyfrowania używane jest hasło, z którego wyprowadzany jest klucz (PBKDF2 + losowa sól przy każdym szyfrowaniu, potem szyfrowanie Fernet). Dzięki temu samo hasło nigdy nie jest nigdzie zapisywane, a to samo hasło użyte dwa razy da inny plik wynikowy. Jeśli hasło zostanie zapomniane, nie da się odzyskać danych - nie ma na to żadnego mechanizmu.

Program dodatkowo po zapisie sprawdza, czy plik wynikowy naprawdę powstał na dysku. Jeśli nie - zwykle oznacza to, że antywirus (np. "Kontrolowany dostęp do folderów" w Windows Defender) usunął go zaraz po utworzeniu, i program o tym informuje.

## Jak z tego korzystać

Są dwa sposoby uruchomienia `HasloDoPlikow.exe`:

**1. Przeciągnięcie pliku na ikonę programu (najwygodniejsze)**

- Aby zaszyfrować: przeciągnij plik `.txt` na ikonę `HasloDoPlikow.exe`, podaj hasło dwa razy. Powstanie plik `nazwa.txt.locked`.
- Aby odszyfrować: przeciągnij plik `.locked` na ikonę, podaj hasło raz. Powstanie plik bez końcówki `.locked`.
- Na koniec naciśnij Enter, żeby zamknąć okno.

**2. Zwykłe dwuklikniecie na `HasloDoPlikow.exe`**

- Program nie dostaje wtedy żadnego pliku od razu, więc sam pyta: "Podaj ścieżkę do pliku (.txt do zaszyfrowania albo .locked do odszyfrowania):".
- W tym miejscu wpisz pełną ścieżkę do pliku, np. `C:\Dokumenty\notatki.txt` albo `C:\Dokumenty\notatki.txt.locked`, i naciśnij Enter.
- Ścieżkę można też wkleić w cudzysłowie (np. skopiowaną z paska adresu Eksploratora Windows przez Shift+prawy klawisz myszy -> "Kopiuj jako ścieżkę") - program sam usunie te cudzysłowy, więc nie trzeba ich ręcznie kasować.
- Zamiast wpisywać ścieżkę z klawiatury, można też przeciągnąć plik z Eksploratora myszką prosto do okna konsoli - ścieżka wstawi się sama.
- Po podaniu ścieżki program dalej działa dokładnie tak samo jak przy przeciąganiu na ikonę: sam rozpoznaje po rozszerzeniu, czy szyfrować, czy odszyfrowywać, i pyta o hasło (dwa razy przy szyfrowaniu, raz przy odszyfrowywaniu).
- Jeśli podana ścieżka jest błędna albo plik pod nią nie istnieje, program to zgłosi i nic nie zrobi.

To wszystko - żadnych dodatkowych komend ani przełączników.