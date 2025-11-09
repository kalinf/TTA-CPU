## Must have
- generowanie rdzenia z konfiguracji
    - generate_template.py
        - ~~przyjęcie ścieżki do katalogu z konfiguracją~~
        - ~~wygenerowanie katalogu FU z miejscem w plikach na uzupełnianie własnych funkcjonalności~~
        - ~~nadpisanie adresów / zapisanie ich w nowym pliku konfiguracyjnym~~
        - ~~wyliczenia layoutów i magistral~~
        - podmienienie ścieżki do `core` jeśli plik fu już istnieje
    - zainstancjonowanie layoutów i magistral
    - zaimportowanie konstruktorów jednostek funkcyjnych i ich instancjonowanie
- test wyliczanie n-tej liczby fibbonacciego
    - ogarnięcie pytest
    - tłumaczenie czytelnych transportów (Adder.i0 -> Result.trigger) na "assembler"
- pamięć programu
- logical operations unit
- jump branch unit
- uniwersalne tesy "assemblerowe"
- testy uruchamiane na FPGA
    - ~~zdobycie (drogą kupna lub wypożyczenia) devkitu FPGA~~

## Nice to have
- częściowo pipelined TTA
- formatter

## Optional
- UART