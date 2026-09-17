#!/usr/bin/env python3
"""
Aplikacja do szyfrowania i odszyfrowywania plikow tekstowych (.txt) haslem.
Wersja przystosowana do dzialania jako samodzielny plik .exe (PyInstaller).

Sposoby uzycia po zbudowaniu .exe:
1. Przeciagnij plik .txt (albo .locked) na ikone programu.
2. Albo po prostu dwuklikniej program - zapyta Cie o sciezke do pliku.

Program sam rozpoznaje, czy plik nalezy zaszyfrowac, czy odszyfrowac,
na podstawie rozszerzenia ".locked" - nie trzeba podawac zadnych
dodatkowych opcji ani komend.

Uzywa biblioteki cryptography (Fernet) z kluczem wyprowadzonym z hasla
za pomoca PBKDF2HMAC, wiec samo haslo nigdy nie jest zapisywane w pliku.
"""

import base64
import getpass
import os
import sys

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_SIZE = 16              # rozmiar soli w bajtach
KDF_ITERATIONS = 390000     # liczba iteracji PBKDF2 (bezpieczna wartosc)
MAGIC_HEADER = b"PTXT1"     # naglowek identyfikujacy plik zaszyfrowany tym programem
LOCKED_SUFFIX = ".locked"   # koncowka dodawana do zaszyfrowanych plikow


def derive_key(password: str, salt: bytes) -> bytes:
    """Wyprowadza klucz Fernet z hasla i soli za pomoca PBKDF2HMAC."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def read_password(confirm: bool = False) -> str:
    """Pobiera haslo od uzytkownika bez wyswietlania go na ekranie."""
    password = getpass.getpass("Podaj haslo: ")
    if confirm:
        password2 = getpass.getpass("Potwierdz haslo: ")
        if password != password2:
            print("Hasla nie sa identyczne.")
            return ""
    if not password:
        print("Haslo nie moze byc puste.")
        return ""
    return password


def write_output(output: str, data: bytes) -> None:
    """Zapisuje dane do pliku wyjsciowego i sprawdza, czy naprawde tam sa."""
    with open(output, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())

    abs_output = os.path.abspath(output)
    print(f"Sciezka docelowa: {abs_output}")

    if os.path.exists(abs_output):
        rozmiar = os.path.getsize(abs_output)
        print(f"Potwierdzono: plik istnieje, rozmiar {rozmiar} bajtow.")
    else:
        print("UWAGA: zaraz po zapisie plik NIE ISTNIEJE pod ta sciezka!")
        print("To zwykle oznacza, ze program antywirusowy (np. ochrona")
        print("przed ransomware / Kontrolowany dostep do folderow w")
        print("Windows Defender) usunal plik zaraz po jego utworzeniu.")
        print("Sprawdz: Windows Security > Ochrona przed wirusami >")
        print("Historia ochrony - powinien tam byc wpis o zablokowanym")
        print("pliku. Sprobuj tez wylaczyc 'Kontrolowany dostep do")
        print("folderow' na czas testu albo dodac wyjatek dla programu.")


def lock_file(path: str, password: str) -> None:
    """Szyfruje plik i zapisuje wynik jako plik.txt.locked."""
    output = path + LOCKED_SUFFIX

    with open(path, "rb") as f:
        data = f.read()

    print(f"Odczytano {len(data)} bajtow z pliku zrodlowego.")
    if len(data) == 0:
        print("UWAGA: plik zrodlowy jest pusty! Sprawdz, czy na pewno")
        print("zapisales tresc w pliku przed jego zaszyfrowaniem.")

    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    token = Fernet(key).encrypt(data)

    write_output(output, MAGIC_HEADER + salt + token)

    print(f"\nGotowe! Plik zaszyfrowany i zapisany jako:\n{output}")


def unlock_file(path: str, password: str) -> None:
    """Odszyfrowuje plik .locked i zapisuje wynik bez tej koncowki."""
    with open(path, "rb") as f:
        content = f.read()

    if not content.startswith(MAGIC_HEADER):
        print("\nTo nie jest plik zaszyfrowany tym programem.")
        return

    content = content[len(MAGIC_HEADER):]
    salt = content[:SALT_SIZE]
    token = content[SALT_SIZE:]

    key = derive_key(password, salt)

    try:
        data = Fernet(key).decrypt(token)
    except InvalidToken:
        print("\nBledne haslo albo uszkodzony plik.")
        return

    print(f"Odszyfrowano {len(data)} bajtow danych.")
    if len(data) == 0:
        print("UWAGA: odszyfrowana tresc jest pusta - oznacza to, ze plik")
        print("byl juz pusty w chwili jego szyfrowania (nie jest to blad")
        print("samego odszyfrowywania).")

    if path.endswith(LOCKED_SUFFIX):
        output = path[: -len(LOCKED_SUFFIX)]
    else:
        output = path + ".odszyfrowany"

    write_output(output, data)

    print(f"\nGotowe! Plik odszyfrowany i zapisany jako:\n{output}")


def process_file(path: str) -> None:
    """Rozpoznaje, czy plik nalezy zaszyfrowac czy odszyfrowac, i to robi."""
    path = path.strip('"')

    if not os.path.isfile(path):
        print(f"\nPlik nie istnieje: {path}")
        return

    if path.endswith(LOCKED_SUFFIX):
        print(f"\nRozpoznano plik zaszyfrowany: {path}")
        password = read_password(confirm=False)
        if password:
            unlock_file(path, password)
    else:
        print(f"\nRozpoznano plik do zaszyfrowania: {path}")
        password = read_password(confirm=True)
        if password:
            lock_file(path, password)


def interactive_mode() -> None:
    """Tryb interaktywny - uzytkownik sam wpisuje sciezke do pliku."""
    print("=" * 50)
    print("  Program do szyfrowania plikow .txt haslem")
    print("=" * 50)
    print("\nPodpowiedz: mozesz tez po prostu przeciagnac plik")
    print("na ikone tego programu, zamiast wpisywac sciezke.\n")

    path = input(
        "Podaj sciezke do pliku (.txt do zaszyfrowania\n"
        "albo .locked do odszyfrowania): "
    ).strip()

    if path:
        process_file(path)


def main() -> None:
    """Glowna funkcja programu."""
    args = sys.argv[1:]

    if args:
        # program uruchomiony np. przez przeciagniecie pliku na ikone
        for path in args:
            process_file(path)
    else:
        # program uruchomiony przez zwykle dwuklikniecie
        interactive_mode()

    try:
        input("\nNacisnij Enter, aby zakonczyc...")
    except EOFError:
        pass


if __name__ == "__main__":
    main()