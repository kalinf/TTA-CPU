## Must have
- generowanie rdzenia z konfiguracji
    - ~~generate_template.py~~
        - ~~przyjęcie ścieżki do katalogu z konfiguracją~~
        - ~~wygenerowanie katalogu FU z miejscem w plikach na uzupełnianie własnych funkcjonalności~~
        - ~~nadpisanie adresów / zapisanie ich w nowym pliku konfiguracyjnym~~
        - ~~wyliczenia layoutów i magistral~~
    - ~~zainstancjonowanie layoutów i magistral~~
    - ~~zaimportowanie konstruktorów jednostek funkcyjnych i ich instancjonowanie~~
- ~~test wyliczanie n-tej liczby fibbonacciego~~
    - ~~pierwszy działający test~~
    - ~~ogarnięcie pytest~~
    - ~~tłumaczenie czytelnych transportów (Adder.i0 -> Result.trigger) na "assembler"~~
- ~~brak operacji nie zmieniający stanu~~
    - ~~przydzielanie rejestrów od 1~~
- ~~porty inout~~
- ~~fix: poprawne przydzielanie portów~~
- porządne komentarze
- ~~pamięć programu~~
- pamięć danych
- ~~logical operations unit~~
- ~~instruction operation fu~~
- ~~uniwersalne tesy "assemblerowe"~~
- testy uruchamiane na FPGA
    - ~~zdobycie (drogą kupna lub wypożyczenia) devkitu FPGA~~
    - ~~synteza na ecp5~~
    - ~~testy timingów~~
    - uruchomienie na sprzęcie
    - możliwość zapisywania pamięci bez konieczności resyntezowania rdzenia
- Licencja i przeklejone notki licencyjne z miejsc skąd brałam kod (colorlight i9, coreblocks)

## Nice to have
- częściowo pipelined TTA
- ~~formatter~~
- pyproject.toml
- wiele możliwych szyn danych ("przerwania" między jednostkami)
- pisanie pseudo assemblera n wykorzystaniem niekoniecznie instancji rdzenia (lepiej pliku konfiguracyjnego)

## Optional
- UART
- wiele możliwych szyn instrukcji (VLIV)